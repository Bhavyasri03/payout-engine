import uuid
from django.db import models

class Merchant(models.Model):
    name = models.CharField(max_length=255)

class BankAccount(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    ifsc = models.CharField(max_length=20)

class LedgerEntry(models.Model):
    ENTRY_TYPES = [
        ("credit", "credit"),
        ("hold", "hold"),
        ("debit", "debit"),
        ("release", "release"),
    ]

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount_paise = models.BigIntegerField()
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    reference_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class Payout(models.Model):
    STATUS_CHOICES = [
        ("pending", "pending"),
        ("processing", "processing"),
        ("completed", "completed"),
        ("failed", "failed"),
    ]

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount_paise = models.BigIntegerField()
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # ✅ Retry logic fields
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

class IdempotencyKey(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    response_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("merchant", "key")