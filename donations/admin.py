from django.contrib import admin
from .models import Donation
from django.http import HttpResponse
import csv

METHOD_DISPLAY = {
    "card": "Card",
    "blik": "BLIK",
    "p24": "Przelewy24",
    "link": "Stripe Link",
    "sepa_debit": "SEPA Debit",
    "bancontact": "Bancontact",
}

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "name", "email", "amount_display",
        "currency", "status", "method_display", "card_brand", "funding",
        "country", "payment_intent"
    )
    list_filter = ("status", "currency", "method", "country", "created_at", "card_brand", "funding")
    search_fields = ("email", "name", "payment_intent")
    readonly_fields = ("amount_display",)
    actions = ["export_csv"]

    def amount_display(self, obj):
        if obj.amount is None or obj.currency is None:
            return "—"
        currency_symbols = {
            "pln": "zł",
            "usd": "$",
            "eur": "€",
        }
        symbol = currency_symbols.get(obj.currency.lower(), "")
        return f"{symbol}{obj.amount:.2f} {obj.currency.upper()}"
    amount_display.short_description = "Amount"

    def method_display(self, obj):
        return METHOD_DISPLAY.get(obj.method, obj.method or "-")
    method_display.short_description = "Method"

    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="donations.csv"'
        resp.write('\ufeff')

        writer = csv.writer(resp)
        writer.writerow([
            "created_at", "name", "email", "amount", "currency",
            "status", "payment_intent", "method", "card_brand", "funding", "country"
        ])

        currency_symbols = {
            "pln": "zł",
            "usd": "$",
            "eur": "€",
        }

        for d in queryset:
            symbol = currency_symbols.get(d.currency.lower(), "")
            amount_str = f"{symbol}{d.amount:.2f} {d.currency.upper()}"
            method_label = METHOD_DISPLAY.get(d.method, d.method or "—")
            writer.writerow([
                d.created_at,
                d.name,
                d.email,
                amount_str,
                d.currency.upper(),
                d.status,
                d.payment_intent,
                method_label,
                d.card_brand,
                d.funding,
                d.country
            ])

        return resp
    export_csv.short_description = "Export selected items to CSV"
