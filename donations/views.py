import json
import traceback
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


def success(request):
    sid = request.GET.get("session_id")
    ctx = {}
    if sid:
        try:
            s = stripe.checkout.Session.retrieve(sid, expand=["payment_intent"])
            ctx = {
                "amount": Decimal(s.payment_intent.amount) / 100,
                "currency": s.payment_intent.currency.upper()
            }
        except Exception as e:
            print("❌ Ошибка получения сессии:", e)
    return render(request, "donations/success.html", ctx)


def cancel(request):
    return render(request, "donations/cancel.html")


@csrf_exempt
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body.decode())

    try:
        amount_decimal = Decimal(str(data.get("amount")))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Невалидная сума"}, status=400)

    min_amt = Decimal(str(settings.DONATION_MIN))
    max_amt = Decimal(str(settings.DONATION_MAX))
    if amount_decimal < min_amt or amount_decimal > max_amt:
        return JsonResponse({"error": f"Сума має бути від {min_amt} до {max_amt}"}, status=400)

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
            print("💾 Сохраняем Donation:", pi_id, amount_decimal, donor_email, donor_name)
            Donation.objects.get_or_create(
                payment_intent=pi_id,
                defaults=dict(
                    name=donor_name,
                    email=donor_email,
                    amount=amount_decimal,
                    currency=currency,
                    status="pending"
                )
            )

        return JsonResponse({"id": session.id})

    except Exception as e:
        print("Stripe error:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    sig = request.META.get("HTTP_STRIPE_SIGNATURE")
    payload = request.body

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print("❌ Stripe webhook signature error:", e)
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]

        # Расширяем charges вручную, если пусто
        if not pi.get("charges") or not pi["charges"].get("data"):
            try:
                pi = stripe.PaymentIntent.retrieve(
                    pi["id"],
                    expand=["charges.data.payment_method_details", "charges.data.billing_details"]
                )
            except Exception as e:
                print("❌ Не удалось получить charges:", e)

        pi_id = pi.get("id")
        amount_minor = pi.get("amount", 0)
        amount_decimal = Decimal(amount_minor) / 100
        currency = pi.get("currency", settings.DONATION_CURRENCY).lower()
        name = pi.metadata.get("donor_name", "") if pi.metadata else ""
        email = pi.get("receipt_email") or pi.get("customer_email") or ""

        method = ""
        country = ""
        try:
            charges = pi.get("charges", {}).get("data", [])
            if charges:
                charge = charges[0]
                method = charge.get("payment_method_details", {}).get("type", "")
                country = charge.get("billing_details", {}).get("address", {}).get("country", "")
        except Exception as e:
            print("⚠️ Ошибка при разборе charge:", e)

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
                raw=pi,
            )
        )

        print("✅ Donation сохранён:", pi_id, f"{amount_decimal:.2f} {currency.upper()}", email, name, method, country)

        if email:
            try:
                send_mail(
                    subject="Дякуємо за донат!",
                    message=f"Дякуємо, {name or 'друже'}! Отримали {amount_decimal:.2f} {currency.upper()}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                print("⚠️ Ошибка при отправке email:", e)

    elif event["type"] == "charge.refunded":
        try:
            pi_id = event["data"]["object"]["payment_intent"]
            Donation.objects.filter(payment_intent=pi_id).update(status="refunded")
        except Exception as e:
            print("❌ Ошибка обработки refunded:", e)

    return HttpResponse(status=200)


def export_all_csv(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

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
