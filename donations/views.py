import json
import traceback
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.core.mail import send_mail
from .models import Donation

stripe.api_key = settings.STRIPE_SECRET_KEY

def success(request):
    sid = request.GET.get("session_id")
    ctx = {}
    if sid:
        s = stripe.checkout.Session.retrieve(sid, expand=["payment_intent"])
        ctx = {"amount": s.payment_intent.amount/100, "currency": s.payment_intent.currency.upper()}
    return render(request, "donations/success.html", ctx)

def cancel(request):
    return render(request, "donations/cancel.html")

# @require_POST
@csrf_exempt   # можно убрать и передавать CSRF‑токен из формы
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    data = json.loads(request.body.decode())
    try:
        amount_float = float(data.get("amount"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Невалидная сумма"}, status=400)

    min_amt = settings.DONATION_MIN
    max_amt = settings.DONATION_MAX
    if amount_float < min_amt or amount_float > max_amt:
        return JsonResponse({"error": f"Сумма от {min_amt} до {max_amt}"}, status=400)

    donor_name = (data.get("name") or "").strip()
    donor_email = (data.get("email") or "").strip()
    currency = settings.DONATION_CURRENCY.lower()
    amount_minor = int(round(amount_float * 100))

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
                "metadata": {
                    "donor_name": donor_name,
                    "chosen_amount": str(amount_float),
                }
            },
            success_url=request.build_absolute_uri("/success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/cancel/"),
        )

        pi_id = session.get("payment_intent")
        if pi_id:
            Donation.objects.get_or_create(
                payment_intent=pi_id,
                defaults=dict(
                    name=donor_name, email=donor_email,
                    amount=amount_minor, currency=currency, status="pending"
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
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        pi_id = session.get("payment_intent")
        currency = (session.get("currency") or settings.DONATION_CURRENCY).lower()

        pi = stripe.PaymentIntent.retrieve(pi_id, expand=["charges"])
        amount_minor = pi.amount
        email = session.get("customer_email") or pi.get("receipt_email")
        name = (pi.metadata or {}).get("donor_name", "")

        Donation.objects.update_or_create(
            payment_intent=pi_id,
            defaults=dict(
                name=name,
                email=email or "",
                amount=amount_minor,
                currency=currency,
                status="succeeded" if pi.status == "succeeded" else pi.status,
                method=(pi.charges.data[0].payment_method_details["type"]
                        if pi.charges and pi.charges.data else ""),
                country=(pi.charges.data[0].billing_details.address.country
                         if pi.charges and pi.charges.data else ""),
                raw=pi
            )
        )

        if email:
            try:
                send_mail(
                    subject="Дякуємо за донат!",
                    message=f"Дякуємо, {name or 'друже'}! Отримали {amount_minor/100:.2f} {currency.upper()}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception:
                pass

    elif event["type"] == "charge.refunded":
        pi_id = event["data"]["object"]["payment_intent"]
        Donation.objects.filter(payment_intent=pi_id).update(status="refunded")

    return HttpResponse(status=200)

def export_all_csv(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    from django.http import StreamingHttpResponse
    import csv
    resp = StreamingHttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename=\"donations_all.csv\"'
    writer = csv.writer(resp)
    writer.writerow(["created_at","name","email","amount","currency","status","payment_intent","method","country"])
    for d in Donation.objects.order_by("-created_at"):
        writer.writerow([d.created_at, d.name, d.email, d.amount/100, d.currency.upper(),
                         d.status, d.payment_intent, d.method, d.country])
    return resp

# from django.conf import settings

# def donate_view(request):
#     return render(request, "donate.html", {
#         "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY
#     })

