from django.contrib import admin
from .models import Donation
from django.http import HttpResponse
import csv

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("created_at","name","email","amount","currency","status","payment_intent")
    list_filter = ("status","currency","created_at")
    search_fields = ("email","name","payment_intent")
    actions = ["export_csv"]

    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="donations.csv"'
        w = csv.writer(resp)
        w.writerow(["created_at","name","email","amount","currency","status","payment_intent","method","country"])
        for d in queryset:
            w.writerow([d.created_at, d.name, d.email, d.amount/100, d.currency.upper(),
                        d.status, d.payment_intent, d.method, d.country])
        return resp
    export_csv.short_description = "Экспорт выделенных в CSV"