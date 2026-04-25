# Payout Engine

A minimal backend system simulating a fintech payout engine where merchants can manage balances and request payouts.

## 🚀 Features

* Ledger-based balance system (credit, debit, hold, release)
* Payout API with idempotency support
* Concurrency-safe balance handling using DB locks
* Background payout processing (simulated async)
* Retry logic for stuck payouts

---

## 🛠 Tech Stack

* Django + Django REST Framework
* SQLite (can be replaced with PostgreSQL)
* Python threading (Celery-ready design)

---

## ⚙️ Setup Instructions

```bash
git clone <your-repo-url>
cd payout-engine

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Server runs at:
http://127.0.0.1:8001/

---

## 📌 API Endpoint

### Create Payout

POST /api/v1/payouts

Headers:
Idempotency-Key: <UUID>

Body:
{
"amount_paise": 5000,
"bank_account_id": 1
}

Response:
{
"payout_id": "uuid",
"status": "pending"
}

---

## 🧠 System Design Highlights

* Money stored as integers (paise) to avoid precision errors
* Ledger ensures full auditability
* Database-level locking prevents race conditions
* Idempotency prevents duplicate payouts
* Retry mechanism ensures reliability

---

## 📂 Project Structure

core/

* models.py
* views.py
* tasks.py
* retry.py

---

## ⚠️ Notes

* Background processing is simulated using threads
* In production, this should be replaced with Celery + Redis

---
