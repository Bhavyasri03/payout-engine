from django.db.models import Sum, Case, When, F, BigIntegerField
from .models import LedgerEntry

def get_balance(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
        balance=Sum(
            Case(
                When(entry_type="credit", then=F("amount_paise")),
                When(entry_type="debit", then=-F("amount_paise")),
                When(entry_type="hold", then=-F("amount_paise")),
                When(entry_type="release", then=F("amount_paise")),
                default=0,
                output_field=BigIntegerField()
            )
        )
    )
    return result["balance"] or 0