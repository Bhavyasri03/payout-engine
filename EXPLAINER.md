# EXPLAINER

## 1. The Ledger

Balance is not stored directly. It is derived from ledger entries.

Each entry has:

* amount_paise (integer)
* entry_type (credit, debit, hold, release)

SQL logic:

SELECT SUM(
CASE
WHEN entry_type = 'credit' THEN amount_paise
WHEN entry_type = 'release' THEN amount_paise
WHEN entry_type = 'debit' THEN -amount_paise
WHEN entry_type = 'hold' THEN -amount_paise
END
) AS balance
FROM core_ledgerentry
WHERE merchant_id = <merchant_id>;

This ensures:

* No floating point issues
* Full auditability
* Correct balance always

---

## 2. The Lock

Used database-level locking:

merchant = Merchant.objects.select_for_update().get(id=merchant.id)

This prevents concurrent payouts from overdrawing balance.

---

## 3. The Idempotency

Idempotency keys are stored per merchant.

Flow:

* Check if key exists
* If yes → return stored response
* If no → process request and store response

Ensures safe retries and prevents duplicate payouts.

---

## 4. The State Machine

Valid transitions:

* pending → processing → completed
* pending → processing → failed

Invalid transitions are blocked using:

if payout.status != "pending":
return

---

## 5. Retry Logic

* Payouts stuck in "processing" for >30 seconds are retried
* Each payout tracks attempts and last_attempt_at
* Max retries = 3
* After max retries → payout marked failed and funds released

---

## 6. AI Audit

AI initially suggested Celery-based implementation using @shared_task.

Issues:

* Celery requires Redis which was not configured locally
* Tasks were not executing, leaving payouts stuck in "pending"

Fix:

* Replaced Celery with Python threading
* Added proper DB handling inside threads
* Verified logic synchronously before async execution

---
