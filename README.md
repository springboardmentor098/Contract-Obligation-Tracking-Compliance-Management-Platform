# ContractIQ — Contract Obligation Tracking & Compliance Management Platform

FastAPI + PostgreSQL backend implementing Sprints 3–12 of the ContractIQ
project: database design, authentication, RBAC, contract lifecycle,
obligation tracking, renewal management, compliance monitoring, and
notifications.

## 1. Project Structure

```
app/
├── main.py                # FastAPI app + router registration
├── config.py               # Settings (reads .env)
├── database.py              # SQLAlchemy engine/session/Base
├── core/
│   ├── security.py          # password hashing, JWT create/decode
│   ├── deps.py               # get_current_user / get_current_active_user
│   └── permissions.py         # require_roles() RBAC dependency (Sprint 6)
├── models/                  # SQLAlchemy models (Sprint 3/4)
│   ├── user.py, contract.py, contract_version.py, obligation.py,
│   ├── renewal.py, notification.py, compliance.py, report.py,
│   └── audit_log.py, activity.py
├── schemas/                 # Pydantic request/response schemas
├── api/                     # Routers: auth, users, contracts, obligations,
│                             # renewals, compliance, notifications
└── services/
    ├── email_service.py       # SMTP sending (Sprint 12)
    ├── notification_service.py # Central notification creation (Sprint 12)
    └── compliance_service.py   # Compliance scoring + risk rules (Sprint 11)

alembic/                    # Migration environment (autogenerate-ready)
docs/DATABASE_DESIGN.md       # Sprint 3 deliverable: schema + ER diagram
requirements.txt
.env.example
```

## 2. Local Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env: set DATABASE_URL, SECRET_KEY, SMTP_* values
```

Make sure PostgreSQL is running and the database exists:

```sql
CREATE DATABASE contractiq_db;
```

## 3. Database Migrations (Sprint 4)

The Alembic environment (`alembic/env.py`) is already wired to
`app.database.Base.metadata` and to `DATABASE_URL` from `.env`, so
autogenerate will pick up every model in `app/models/`.

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Verify the tables in pgAdmin: `contractiq_db → Schemas → public → Tables`.
You should see all 10 tables: `users`, `contracts`, `contract_versions`,
`obligations`, `renewals`, `notifications`, `reports`, `audit_logs`,
`activities`, `compliance_records`.

Whenever you change a model, repeat:
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## 4. Running the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI: **http://127.0.0.1:8000/docs**

## 5. Sprint-by-Sprint Testing Guide

### Sprint 5/6 — Auth & RBAC
1. `POST /auth/register` — create users with different `role` values
   (`Administrator`, `Legal Manager`, `Compliance Officer`,
   `Contract Manager`, `Department Head`, `Employee`).
2. `POST /auth/login` (form-encoded `username`=email, `password`) → copy
   `access_token`.
3. In Swagger, click **Authorize** and paste the token.
4. `DELETE /users/{user_id}` as Administrator → `200/204`.
   As Employee → `403 Forbidden`. With no token → `401 Unauthorized`.

### Sprint 7/8 — Contracts
1. `POST /contracts` — `created_by` is taken from the JWT, never the body.
2. `GET /contracts`, `GET /contracts/{id}` (try a bad id → `404`).
3. `POST /contracts/{id}/submit-review` → `Draft → Under Review`.
4. `POST /contracts/{id}/approve` (Administrator/Legal Manager only).
5. `POST /contracts/{id}/activate`.
6. Try an out-of-order transition (e.g. approve a Draft contract) → `400`.

### Sprint 9 — Obligations
1. `POST /obligations` with a valid `contract_id`.
2. `GET /obligations`, `GET /obligations/{id}`,
   `GET /contracts/{id}/obligations`.
3. `PATCH /obligations/{id}/status`, `POST /obligations/{id}/complete`
   (backend sets `completion_date`, not the client).
4. Overdue detection runs automatically whenever obligations are listed or
   fetched — any obligation whose `due_date` has passed and isn't
   `Completed` flips to `Overdue` and fires a notification.

### Sprint 10 — Renewals
1. `POST /renewals` for an existing contract.
2. `PATCH /renewals/{id}/status` → `Upcoming → In Progress`.
3. `POST /renewals/{id}/renew` → sets `Renewed`, pushes `new_expiry_date`
   onto the parent contract, and reactivates it if it had expired.

### Sprint 11 — Compliance
1. `GET /contracts/{id}/compliance` — computed live from the contract's
   obligations (see `docs/DATABASE_DESIGN.md` and
   `app/services/compliance_service.py` for the exact scoring rules) and
   written to `compliance_records` for history.
2. `GET /compliance/summary`, `GET /compliance/non-compliant`,
   `GET /compliance/high-risk`.

### Sprint 12 — Notifications
1. `GET /notifications` — only returns the authenticated user's own
   notifications.
2. `PATCH /notifications/{id}/read`, `PATCH /notifications/read-all`.
3. Set real `SMTP_*` values in `.env` to see emails actually sent; without
   them, notifications are still created in the DB but email sending is
   skipped gracefully (logged, never crashes the request).

## 6. Pushing to GitHub

```bash
git init
git add .
git commit -m "ContractIQ backend: Sprints 3-12 (DB design, auth/RBAC, contracts, obligations, renewals, compliance, notifications)"
git branch -M main
git remote add origin <your-assigned-repo-url>
git push -u origin main
```

`.env` is already excluded via `.gitignore` — never commit real credentials.
