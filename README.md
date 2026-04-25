# Payout Engine

A minimal backend system simulating a real-world fintech payout engine where merchants can manage balances and request withdrawals safely.

---

## 🚀 Features

* Ledger-based balance system (credit, debit, hold, release)
* Payout API with idempotency support
* Concurrency-safe balance handling using database locks
* Background payout processing (async simulation)
* Retry logic for stuck payouts

---

## 🛠 Tech Stack

* Python
* Django + Django REST Framework
* SQLite (PostgreSQL compatible)
* Threading (Celery-ready architecture)

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

POST `/api/v1/payouts`

### Headers

```
Idempotency-Key: <UUID>
```

### Request Body

```json
{
  "amount_paise": 5000,
  "bank_account_id": 1
}
```

### Response

```json
{
  "payout_id": "uuid",
  "status": "pending"
}
```

---

## 🧠 Key Design Decisions

### Ledger-Based Accounting

Balance is not stored directly. It is derived from transaction history for accuracy and auditability.

### Concurrency Handling

Uses `select_for_update()` to prevent race conditions and double spending.

### Idempotency

Ensures duplicate API requests return the same response without creating multiple payouts.

### Retry Mechanism

Handles stuck payouts with retry logic and failure recovery.

---

## 📂 Project Structure

```
payout-engine/
│
├── core/
│   ├── models.py
│   ├── views.py
│   ├── tasks.py
│   ├── retry.py
│   └── utils.py
│
├── payout_engine/
├── manage.py
├── README.md
├── EXPLAINER.md
└── requirements.txt
```

---

## ⚠️ Notes

* SQLite is used for simplicity; system is compatible with PostgreSQL
* Background processing is simulated using threads
* In production, Celery + Redis should be used

---

## 📄 Documentation

* See **EXPLAINER.md** for detailed design explanations
