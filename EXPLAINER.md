# EXPLAINER

## 1. The Ledger

Balance is not stored directly. It is derived from ledger entries to ensure full auditability and correctness.

Each ledger entry has:

* `amount_paise` (stored as integer, no floats)
* `entry_type` (credit, debit, hold, release)

Balance is computed using aggregation:

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

Design reasoning:

* Credits increase available balance
* Holds reduce available balance (reserved for payouts)
* Debits finalize the payout (money leaves system)
* Releases return funds when payout fails

This ensures:

* No floating point precision issues
* Balance is always reproducible from history
* Full audit trail of all money movements

---

## 2. The Lock

To prevent race conditions, I used database-level row locking:

merchant = Merchant.objects.select_for_update().get(id=merchant.id)

This ensures that only one transaction can modify a merchant’s balance at a time.

Scenario:

* Merchant balance = 100
* Two concurrent payout requests of 60 arrive

Execution:

* First request locks the row and proceeds
* Second request waits
* After first completes, second re-checks balance and fails if insufficient

This prevents double spending and solves the classic check-then-deduct race condition.

---

## 3. The Idempotency

Each payout request requires an `Idempotency-Key` header (UUID).

Implementation:

* Keys are stored in an `IdempotencyKey` table
* Scoped per merchant
* Stores response data

Flow:

1. Check if key exists for the merchant
2. If yes → return stored response (no new payout created)
3. If no → process request and store response

Edge case handled:
If two identical requests arrive simultaneously:

* First request processes normally
* Second request reads stored response and returns it

This ensures:

* Safe retries from client
* No duplicate payouts

---

## 4. The State Machine

Payout lifecycle:

Valid transitions:

* pending → processing → completed
* pending → processing → failed

Invalid transitions are blocked using:

if payout.status != "pending":
return

Rules:

* Only pending payouts can move forward
* Completed payouts are final
* Failed payouts cannot transition back

On failure:

* Funds are returned using a "release" ledger entry
* This is done inside a database transaction to ensure atomicity

---

## 5. Retry Logic

Payouts can get stuck in "processing" state (simulated 10% hang).

To handle this:

* Each payout tracks:

  * `attempts`
  * `last_attempt_at`

Retry conditions:

* status = processing
* last_attempt_at older than 30 seconds
* attempts < 3

Retry mechanism:

* Background loop scans for stuck payouts
* Retries processing
* Increments attempt count

Max retry handling:

* After 3 attempts → payout marked as failed
* Funds are released using a ledger entry

This ensures:

* No payout remains stuck indefinitely
* System is resilient to transient failures

---

## 6. The AI Audit

AI initially suggested a Celery-based implementation using `@shared_task` and `.delay()`.

Issues identified:

* Celery requires Redis, which was not configured in the local environment
* Tasks were not executing, leaving payouts stuck in "pending"
* AI did not account for environment setup constraints

Fix applied:

* Replaced Celery with Python threading for async simulation
* Ensured database connections work inside threads
* Verified payout lifecycle synchronously before adding async behavior

Final approach:

* Thread-based background processing for local execution
* Design is compatible with Celery + Redis for production

---

## 7. Additional Notes

* All monetary values are stored as integers (paise) to avoid precision issues
* All critical operations are wrapped in `transaction.atomic()` for consistency
* Ledger-based design ensures strong data integrity
* Concurrency is handled at the database level, not in application logic
* System is designed to be production-ready with minimal changes (Celery integration)
