import time
from django.utils import timezone
from datetime import timedelta
from .models import Payout
from .tasks import process_payout


def retry_stuck_payouts():
    while True:
        now = timezone.now()

        stuck_payouts = Payout.objects.filter(
            status="processing",
            last_attempt_at__lt=now - timedelta(seconds=30),
            attempt_count__lt=3
        )

        for payout in stuck_payouts:
            print("🔁 Retrying payout:", payout.id)
            process_payout(payout.id)

        # max retries exceeded
        failed_payouts = Payout.objects.filter(
            status="processing",
            attempt_count__gte=3
        )

        for payout in failed_payouts:
            print("❌ Max retries reached:", payout.id)

            payout.status = "failed"
            payout.save()

        time.sleep(10)