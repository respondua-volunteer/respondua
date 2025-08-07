import json
import logging
import csv
import stripe
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.mail import send_mail
from .models import Donation

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger("app.donations")


def success(request):
    sid = request.GET.get("session_id")
    ctx = {}
    if sid:
        try:
            session = stripe.checkout.Session.retrieve(sid, expand=["payment_intent"])
            ctx = {
                "amount": Decimal(session.payment_intent.amount) / 100,
                "currency": session.payment_intent.currency.upper(),
                "transaction_id": session.payment_intent.id
            }
            logger.info("Success page loaded", extra=ctx)
        except Exception as e:
            logger.exception("Session retrieval error")
    return render(request, "donations/success.html", ctx)


def cancel(request):
    logger.info("Donation cancelled by user")
    return render(request, "donations/cancel.html")


@csrf_exempt
def create_checkout_session(request):
    if request.method != "POST":
        logger.warning("Non-POST request to create_checkout_session")
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
        amount_decimal = Decimal(str(data.get("amount")))
    except (TypeError, ValueError, json.JSONDecodeError) as e:
        logger.warning("Invalid request data", exc_info=e)
        return JsonResponse({"error": "Invalid amount"}, status=400)

    min_amt = Decimal(str(settings.DONATION_MIN))
    max_amt = settings.DONATION_MAX

    if amount_decimal < min_amt:
        logger.info("Donation below minimum", extra={"amount": str(amount_decimal)})
        return JsonResponse({"error": f"The amount must be from {min_amt}"}, status=400)
    if max_amt and amount_decimal > Decimal(str(max_amt)):
        logger.info("Donation above maximum", extra={"amount": str(amount_decimal)})
        return JsonResponse({"error": f"The amount must not exceed {max_amt}"}, status=400)

    donor_name = (data.get("name") or "").strip()
    donor_email = (data.get("email") or "").strip()
    currency = settings.DONATION_CURRENCY.lower()
    amount_minor = int(amount_decimal * 100)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_creation="if_required",
            customer_email=donor_email or None,
            payment_method_types=["card", "link", "blik", "p24"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": "Donation"},
                    "unit_amount": amount_minor,
                },
                "quantity": 1,
            }],
            payment_intent_data={
                "receipt_email": donor_email or None,
                "metadata": {
                    "donor_name": donor_name,
                    "chosen_amount": str(amount_decimal),
                }
            },
            success_url=request.build_absolute_uri("/success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/cancel/"),
        )

        pi_id = session.get("payment_intent")
        if pi_id:
            obj, created = Donation.objects.get_or_create(
                payment_intent=pi_id,
                defaults=dict(
                    name=donor_name,
                    email=donor_email,
                    amount=amount_decimal,
                    currency=currency,
                    status="pending",
                    method="",
                    country="",
                )
            )
            logger.info("Donation created", extra={
                "intent": pi_id,
                "email": donor_email,
                "amount": float(amount_decimal),
                "name": donor_name,
                "created": created
            })

        return JsonResponse({"id": session.id})

    except Exception as e:
        logger.exception("Error creating Stripe session")
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    sig = request.META.get("HTTP_STRIPE_SIGNATURE")
    payload = request.body

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        logger.warning("Invalid Stripe webhook signature", exc_info=e)
        return HttpResponse(status=400)

    event_type = event["type"]
    logger.info(f"Webhook received: {event_type}")

    if event_type == "payment_intent.succeeded":
        pi_id = event["data"]["object"]["id"]

        try:
            pi = stripe.PaymentIntent.retrieve(pi_id)
        except Exception as e:
            logger.exception("Unable to retrieve PaymentIntent")
            return HttpResponse(status=400)

        amount_minor = pi.get("amount", 0)
        amount_decimal = Decimal(amount_minor) / 100
        currency = pi.get("currency", settings.DONATION_CURRENCY).lower()
        name = pi.metadata.get("donor_name", "") if pi.metadata else ""
        email = pi.get("receipt_email") or pi.get("customer_email") or ""

        charge_info = {}
        method = ""
        country = ""
        card_brand = ""
        funding = ""

        try:
            charge = stripe.Charge.retrieve(pi.get("latest_charge"))
            details = charge.get("payment_method_details", {})
            method = details.get("type", "")
            country = charge.get("billing_details", {}).get("address", {}).get("country", "")
            if method == "card":
                card = details.get("card", {})
                card_brand = card.get("brand", "")
                funding = card.get("funding", "")
        except Exception as e:
            logger.warning("Unable to retrieve Stripe charge", exc_info=e)

        Donation.objects.update_or_create(
            payment_intent=pi_id,
            defaults=dict(
                name=name,
                email=email,
                amount=amount_decimal,
                currency=currency,
                status="succeeded",
                method=method,
                country=country,
                card_brand=card_brand,
                funding=funding,
                raw=pi,
            )
        )

        logger.info("Donation saved after webhook", extra={
            "intent": pi_id,
            "email": email,
            "amount": float(amount_decimal),
            "currency": currency.upper(),
            "method": method,
            "country": country,
            "card_brand": card_brand,
            "funding": funding
        })

        if email:
            try:
                send_mail(
                    subject="Thank you for your donation!",
                    message=f"Thank you, {name or 'friend'}! We received {amount_decimal:.2f} {currency.upper()}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                logger.info("Confirmation email sent", extra={"email": email})
            except Exception as e:
                logger.warning("Error sending confirmation email", exc_info=e)

    elif event_type == "charge.refunded":
        try:
            pi_id = event["data"]["object"]["payment_intent"]
            Donation.objects.filter(payment_intent=pi_id).update(status="refunded")
            logger.info("Donation marked as refunded", extra={"intent": pi_id})
        except Exception as e:
            logger.warning("Error processing refund webhook", exc_info=e)

    return HttpResponse(status=200)


def export_all_csv(request):
    if not request.user.is_staff:
        logger.warning("Unauthorized CSV export attempt")
        return HttpResponseForbidden()

    logger.info("Donation CSV export initiated", extra={"user": request.user.email})

    resp = StreamingHttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="donations_all.csv"'
    writer = csv.writer(resp)
    writer.writerow(["created_at", "name", "email", "amount", "currency", "status", "payment_intent", "method", "country"])

    for d in Donation.objects.order_by("-created_at"):
        currency_symbols = {
            "pln": "zł",
            "usd": "$",
            "eur": "€",
        }
        symbol = currency_symbols.get(d.currency.lower(), "")
        amount_str = f"{symbol}{d.amount:.2f} {d.currency.upper()}"
        writer.writerow([
            d.created_at,
            d.name,
            d.email,
            amount_str,
            d.currency.upper(),
            d.status,
            d.payment_intent,
            d.method,
            d.country
        ])
    return resp


logger = logging.getLogger("app.donations")

def test_log_view(request):
    logger.info("Test JSON log", extra={"view": "test_log_view", "user": str(request.user)})
    return HttpResponse("Logged")