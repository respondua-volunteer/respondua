from django.db import models

class Donation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    amount = models.IntegerField(help_text="В минимальных единицах валюты (коп/грн*100, PLN grosz)")
    currency = models.CharField(max_length=10, default="pln")
    payment_intent = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    raw = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.email or self.name} — {self.amount/100:.2f} {self.currency.upper()} — {self.status}"