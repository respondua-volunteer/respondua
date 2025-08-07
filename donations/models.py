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
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="In currency (e.g., 77.00 PLN or 15.50 USD)"
    )

    currency = models.CharField(max_length=10, default="pln")
    payment_intent = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, blank=True)
    card_brand = models.CharField(max_length=20, blank=True, default="")
    funding = models.CharField(max_length=20, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    raw = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.email or self.name} — {self.amount:.2f} {self.currency.upper()} — {self.status}"
