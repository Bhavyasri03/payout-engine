# core/tasks.py

import random
import time
from django.utils import timezone
from django.db import transaction, close_old_connections
from .models import Payout, LedgerEntry


def process_payout(payout_id):
    close_old_connections()

    payout = Payout.objects.get(id=payout_id)

    if payout.status != "pending":
        return

    # mark processing
    payout.status = "processing"
    payout.attempts += 1   # ⚠️ use YOUR field name (attempts, not attempt_count)
    payout.last_attempt_at = timezone.now()
    payout.save()

    time.sleep(2)

    result = random.choices(
        ["success", "fail", "hang"],
        weights=[70, 20, 10]
    )[0]

    if result == "success":
        with transaction.atomic():
            payout.status = "completed"
            payout.save()

            LedgerEntry.objects.create(
                merchant=payout.merchant,
                amount_paise=payout.amount_paise,
                entry_type="debit",
                reference_id=payout.id
            )

    elif result == "fail":
        with transaction.atomic():
            payout.status = "failed"
            payout.save()

            LedgerEntry.objects.create(
                merchant=payout.merchant,
                amount_paise=payout.amount_paise,
                entry_type="release",
                reference_id=payout.id
            )

    elif result == "hang":
        print("⏳ payout stuck:", payout.id)