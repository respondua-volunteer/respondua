# donations/views.py
import json
import logging
import csv
import stripe
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# i18n
from django.utils.translation import override, gettext as _, get_language

# email utils
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Donation

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger("app.donations")


# ---------- helpers ----------

def _send_donation_receipt(
    email: str,
    name: str,
    amount: Decimal,
    currency: str,
    transaction_id: str,
    locale: str | None,
):
    """
    Отправляет донору письмо-подтверждение (HTML + plain) с учётом локали.
    Пытаемся взять шаблоны, иначе отправляем упрощённую версию.
    """
    if not email:
        return

    active_locale = locale or settings.LANGUAGE_CODE

    with override(active_locale):
        ctx = {
            "name": name or "",
            "amount": f"{amount:.2f}",
            "currency": currency.upper(),
            "transaction_id": transaction_id,
            "contact_email": getattr(settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL),
            "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
        }

        # Fallback по умолчанию (тоже переведён через gettext)
        subject = _("Дякуємо! Оплату отримано")
        text_body = _(
            "Дякуємо, %(name)s!\n"
            "Ми отримали %(amount)s %(currency)s.\n"
            "Номер транзакції: %(tx)s\n\n"
            "Цей лист надіслано з адреси, яка не приймає відповіді. Питання: %(contact)s"
        ) % {
            "name": ctx["name"] or _("друже"),
            "amount": ctx["amount"],
            "currency": ctx["currency"],
            "tx": ctx["transaction_id"],
            "contact": ctx["contact_email"],
        }

        # Пытаемся использовать HTML/текстовые шаблоны
        html_body = render_to_string("donations/receipt.html", ctx)
        try:
            subj_tpl = render_to_string("donations/emails/receipt_subject.txt", ctx).strip()
            if subj_tpl:
                subject = subj_tpl
        except Exception:
            pass
        try:
            text_tpl = render_to_string("donations/emails/receipt.txt", ctx)
            if text_tpl:
                text_body = text_tpl
        except Exception:
            pass

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,  # no-reply@...
                to=[email],
                reply_to=[getattr(settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL)],
                bcc=getattr(settings, "DONATIONS_BCC", []),
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=True)
            logger.info("Receipt email sent", extra={"email": email, "intent": transaction_id, "locale": active_locale})
        except Exception:
            logger.warning("Error sending receipt email", exc_info=True)


# ---------- views ----------

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
        except Exception:
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

    # Язык пользователя
    donor_locale = getattr(request, "LANGUAGE_CODE", None) or get_language() or settings.LANGUAGE_CODE
    # Локаль для UI Stripe (если не входит в список — пусть Stripe сам определит)
    stripe_supported = {"auto", "bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fil", "fr",
                        "hr", "hu", "id", "it", "ja", "ko", "lt", "lv", "ms", "mt", "nb", "nl",
                        "pl", "pt", "ro", "ru", "sk", "sl", "sv", "th", "tr", "vi", "zh", "zh-HK", "zh-TW", "uk"}
    stripe_locale = donor_locale if donor_locale in stripe_supported else "auto"

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
                    "donor_locale": donor_locale,  # <<< сохраняем язык в PI
                }
            },
            locale=stripe_locale,  # <<< локаль интерфейса Checkout
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
                "created": created,
                "locale": donor_locale,
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
        except Exception:
            logger.exception("Unable to retrieve PaymentIntent")
            return HttpResponse(status=400)

        amount_minor = pi.get("amount", 0)
        amount_decimal = Decimal(amount_minor) / 100
        currency = (pi.get("currency") or settings.DONATION_CURRENCY).lower()
        name = pi.metadata.get("donor_name", "") if getattr(pi, "metadata", None) else ""
        email = pi.get("receipt_email") or pi.get("customer_email") or ""
        donor_locale = ""
        try:
            donor_locale = (pi.metadata or {}).get("donor_locale", "")
        except Exception:
            donor_locale = ""

        method = ""
        country = ""
        card_brand = ""
        funding = ""

        try:
            charge = stripe.Charge.retrieve(pi.get("latest_charge"))
            details = charge.get("payment_method_details", {}) or {}
            method = details.get("type", "") or ""
            country = (charge.get("billing_details", {}) or {}).get("address", {}).get("country", "") or ""
            if method == "card":
                card = details.get("card", {}) or {}
                card_brand = card.get("brand", "") or ""
                funding = card.get("funding", "") or ""
        except Exception:
            logger.warning("Unable to retrieve Stripe charge", exc_info=True)

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
            "funding": funding,
            "locale": donor_locale,
        })

        # письмо-квитанция с учётом языка
        _send_donation_receipt(
            email=email,
            name=name,
            amount=amount_decimal,
            currency=currency,
            transaction_id=pi_id,
            locale=donor_locale,
        )

    elif event_type == "charge.refunded":
        try:
            pi_id = event["data"]["object"]["payment_intent"]
            Donation.objects.filter(payment_intent=pi_id).update(status="refunded")
            logger.info("Donation marked as refunded", extra={"intent": pi_id})
        except Exception:
            logger.warning("Error processing refund webhook", exc_info=True)

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
        currency_symbols = {"pln": "zł", "usd": "$", "eur": "€"}
        symbol = currency_symbols.get(d.currency.lower(), "")
        amount_str = f"{symbol}{d.amount:.2f} {d.currency.upper()}"
        writer.writerow([
            d.created_at, d.name, d.email, amount_str, d.currency.upper(), d.status,
            d.payment_intent, d.method, d.country
        ])
    return resp


def test_log_view(request):
    logger.info("Test JSON log", extra={"view": "test_log_view", "user": str(request.user)})
    return HttpResponse("Logged")
