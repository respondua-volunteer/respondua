from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "email",
        "amount",
        "currency",
        "status",
        "payment_intent",
        "method",
        "country",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = ("email", "name", "payment_intent")
    actions = ["export_csv"]

    @admin.action(description="Экспорт выделенных в CSV")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="donations.csv"'
        writer = csv.writer(resp)

        writer.writerow([
            "created_at",
            "name",
            "email",
            "amount",
            "currency",
            "status",
            "payment_intent",
            "method",
            "country",
        ])

        for d in queryset:
            writer.writerow([
                d.created_at.isoformat(),
                d.name or "",
                d.email or "",
                "{:.2f}".format(d.amount / 100),
                d.currency.upper() if d.currency else "",
                d.status,
                d.payment_intent,
                d.method or "",
                d.country or "",
            ])

        return resp
