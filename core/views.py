from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Merchant, Payout, LedgerEntry, IdempotencyKey
from .utils import get_balance

from .tasks import process_payout
import threading


@api_view(['POST'])
@transaction.atomic
def create_payout(request):
    merchant = Merchant.objects.first()

    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return Response({"error": "Missing Idempotency-Key"}, status=400)

    existing = IdempotencyKey.objects.filter(
        merchant=merchant,
        key=idempotency_key
    ).first()

    if existing:
        return Response(existing.response_data)

    amount = int(request.data.get("amount_paise"))
    bank_id = request.data.get("bank_account_id")

    # 🔒 LOCK
    merchant = Merchant.objects.select_for_update().get(id=merchant.id)

    balance = get_balance(merchant)

    if balance < amount:
        return Response({"error": "Insufficient balance"}, status=400)

    payout = Payout.objects.create(
        merchant=merchant,
        amount_paise=amount,
        bank_account_id=bank_id
    )

    # HOLD funds
    LedgerEntry.objects.create(
        merchant=merchant,
        amount_paise=amount,
        entry_type="hold",
        reference_id=payout.id
    )

    # BACKGROUND PROCESS (thread)
    threading.Thread(target=process_payout, args=(payout.id,), daemon=True).start()
    response_data = {
        "payout_id": str(payout.id),
        "status": payout.status
    }

    IdempotencyKey.objects.create(
        merchant=merchant,
        key=idempotency_key,
        response_data=response_data
    )

    return Response(response_data)