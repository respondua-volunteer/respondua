from django.contrib import admin
from .models import Donation
from django.http import HttpResponse
import csv

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "amount_display", "currency", "status", "payment_intent")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("email", "name", "payment_intent")
    readonly_fields = ("amount_display",)
    actions = ["export_csv"]

    def amount_display(self, obj):
        currency_symbols = {
            "pln": "zł",
            "usd": "$",
            "eur": "€",
            # добавь другие валюты при необходимости
        }
        symbol = currency_symbols.get(obj.currency.lower(), "")
        return f"{symbol}{obj.amount:.2f} {obj.currency.upper()}"  # 🟢 без деления на 100
    amount_display.short_description = "Amount"

    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="donations.csv"'
        writer = csv.writer(resp)
        writer.writerow(["created_at", "name", "email", "amount", "currency", "status", "payment_intent", "method", "country"])
        for d in queryset:
            currency_symbols = {
                "pln": "zł",
                "usd": "$",
                "eur": "€",
            }
            symbol = currency_symbols.get(d.currency.lower(), "")
            amount_str = f"{symbol}{d.amount:.2f} {d.currency.upper()}"  # 🟢 без деления на 100
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
    export_csv.short_description = "Экспорт выделенных в CSV"
