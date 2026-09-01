ContractIQ
Contract Obligation Tracking & Compliance Management Platform
ContractIQ is a FastAPI + PostgreSQL backend for managing the full contract lifecycle — creation, review, approval, activation, obligation tracking, renewals, compliance/risk scoring, notifications, and audit logging — behind a role-based, JWT-secured REST API.
---
Table of Contents
Overview
Tech Stack
Project Structure
Database Design
Roles & Permissions
Getting Started
Environment Variables
Database Migrations
Running with Docker
API Reference
Business Rules Cheat Sheet
Testing
Seed Data
Contributing
License
---
1. Overview
ContractIQ models the following business flow:
```
User
 │
 ▼
Contract ──┬─────────────────────┐
           │                     │
           ▼                     ▼
   Contract Versions        Obligations ──► Notifications
           │                     │
           ▼                     ▼
       Renewals            Compliance Records
           │
           ▼
     Notifications

User ──► Reports
User ──► Audit Logs
User ──► Activities
```
Each concern — contract data, obligations, renewals, compliance evaluation, notifications, and audit history — lives in its own table and is connected via foreign keys, so the pieces can be extended or queried independently.
Core capabilities:
JWT authentication with six-role RBAC (Administrator, Legal Manager, Compliance Officer, Contract Manager, Department Head, Employee)
Contract lifecycle management with enforced status transitions (Draft → Under Review → Approved → Active → …)
Obligation tracking with automatic overdue detection
Renewal workflow that rolls a completed renewal's new expiry date back onto the parent contract
Live compliance scoring and risk-level classification, persisted as historical records
In-app + email notifications (SMTP, degrades gracefully if unconfigured)
Audit logging and activity history models
2. Tech Stack
Technology	Purpose
Python 3.12+	Backend language
FastAPI	REST API framework
SQLAlchemy 2.0	ORM / database models
Pydantic v2	Request/response validation & settings
PostgreSQL 16	Relational database
Alembic	Database migrations
python-jose	JWT issuing/verification
passlib + bcrypt	Password hashing
Uvicorn	ASGI server
Docker / docker-compose	Containerized DB + API
Pytest	Testing
Swagger / OpenAPI	Interactive API docs (`/docs`)
3. Project Structure
```
contractiq/
├── requirements.txt
├── alembic.ini
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── seed.py
│
├── app/
│   ├── main.py                 # FastAPI app, CORS, router registration
│   ├── config.py                # Settings loaded from .env (pydantic-settings)
│   ├── database.py               # SQLAlchemy engine / session / Base
│   │
│   ├── core/
│   │   ├── security.py           # password hashing, JWT create/decode
│   │   ├── deps.py                # get_current_user / get_current_active_user
│   │   ├── permissions.py          # require_roles() RBAC dependency
│   │   └── roles.py                # UserRole enum
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py, contract.py, contract_version.py, obligation.py
│   │   ├── renewal.py, notification.py, compliance.py, report.py
│   │   └── audit_log.py, activity.py
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── auth.py, user.py, contract.py, obligation.py
│   │   └── renewal.py, compliance.py, notification.py
│   │
│   ├── services/                 # Business logic
│   │   ├── contract_service.py, obligation_service.py
│   │   ├── compliance_service.py    # scoring + risk-level rules
│   │   ├── notification_service.py  # central notification creation
│   │   └── email_service.py          # SMTP sending
│   │
│   └── api/                      # Routers registered in main.py
│       ├── auth.py                 # /auth
│       ├── users.py                # /users
│       ├── contracts.py            # /contracts
│       ├── obligations.py          # /obligations, /contracts/{id}/obligations
│       ├── renewals.py             # /renewals, /contracts/{id}/renewals
│       ├── compliance.py           # /compliance
│       └── notifications.py        # /notifications
│
├── alembic/
│   ├── env.py                    # wired to app.database.Base.metadata
│   └── versions/                 # migration history
│
├── docs/
│   ├── DATABASE_DESIGN.md
│   ├── ER_DIAGRAM.md
│   └── schema.dbml
│
└── tests/
    └── test_health.py
```
> **Note:** the repository also contains a couple of superseded/legacy files (`app/api/user_api.py`, `app/api/contract_compliance.py`, `app/database/database.py`, `app/models/audit.py`, `app/routers/*`) left over from earlier sprints. They are **not** imported by `app/main.py` and are not part of the live application — the files listed above under `app/api/` and `app/database.py` are the ones actually wired in. Safe to delete during cleanup.
4. Database Design
The schema has 10 tables, matching the original Sprint 3 design plus `compliance_records`, added to retain a history of compliance evaluations.
Table	Purpose	Key columns
`users`	Accounts, credentials, roles	`id`, `full_name`, `email`, `hashed_password`, `role`, `is_active`
`contracts`	Master contract record	`id`, `title`, `contract_number`, `category`, `status`, `start_date`, `end_date`, `created_by`, `assigned_to`, `reviewed_at`, `approved_at`, `activated_at`
`contract_versions`	Version history of a contract's document/content	`id`, `contract_id`, `version_number`, `file_url`, `changed_by`, `change_summary`
`obligations`	Tasks/deliverables tied to a contract	`id`, `contract_id`, `title`, `obligation_type`, `due_date`, `assigned_to`, `status`, `completion_date`
`renewals`	Renewal cycle tracking	`id`, `contract_id`, `renewal_date`, `previous_expiry_date`, `new_expiry_date`, `status`, `assigned_to`, `notes`
`notifications`	In-app/email notices	`id`, `user_id`, `contract_id`, `obligation_id`, `notification_type`, `title`, `message`, `status`, `sent_at`, `read_at`
`compliance_records`	Historical compliance evaluations	`id`, `contract_id`, `status`, `compliance_score`, `risk_level`, `evaluated_at`, `notes`
`reports`	Generated report metadata	`id`, `report_type`, `report_format`, `generated_by`, `file_url`, `parameters`
`audit_logs`	Security/action audit trail	`id`, `user_id`, `action`, `entity_type`, `entity_id`, `details`, `ip_address`
`activities`	General user activity feed	`id`, `user_id`, `description`, `entity_type`, `entity_id`
Relationships: a `User` creates/is assigned many `Contracts`; a `Contract` has many `ContractVersions`, `Obligations`, and `Renewals` (all cascade-deleted with the contract); `Obligations` and `Contracts` each generate `Notifications`; `ComplianceRecord` and `Report` reference a `Contract`/`User` respectively; `AuditLog` and `Activity` both belong to a `User`.
See `contractiq/docs/DATABASE_DESIGN.md` and `contractiq/docs/schema.dbml` for full column-level detail, and `ContractIQ_ER_Diagram.png` for the entity-relationship diagram.
5. Roles & Permissions
Six roles, defined in `app/core/roles.py`:
`ADMINISTRATOR`
`LEGAL_MANAGER`
`COMPLIANCE_OFFICER`
`CONTRACT_MANAGER`
`DEPARTMENT_HEAD`
`EMPLOYEE`
Authorization is enforced with a reusable `require_roles(*allowed_roles)` FastAPI dependency (`app/core/permissions.py`), layered on top of JWT auth: a missing/invalid token returns `401`, a valid token with an insufficient role returns `403`. Common groupings used across routers:
Group	Roles
`ANY_MANAGER_ROLES`	Administrator, Legal Manager, Contract Manager
`COMPLIANCE_VIEW_ROLES`	Administrator, Legal Manager, Compliance Officer, Contract Manager
`APPROVAL_ROLES`	Administrator, Legal Manager
6. Getting Started
Prerequisites: Python 3.12+, PostgreSQL 16 (or Docker), `pip`.
```bash
cd contractiq

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env: DATABASE_URL, SECRET_KEY, SMTP_* (optional)

# 4. Create the database (if running Postgres locally, not via Docker)
psql -U postgres -c "CREATE DATABASE contractiq_db;"

# 5. Apply migrations
alembic upgrade head

# 6. Run the API
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs for interactive Swagger docs, or http://127.0.0.1:8000/redoc for ReDoc.
Health check: `GET /` → `{"status": "ok", "service": "ContractIQ API"}`
7. Environment Variables
Set in `contractiq/.env` (see `.env.example`):
Variable	Default	Description
`DATABASE_URL`	`postgresql+psycopg2://postgres:postgres@localhost:5432/contractiq_db`	SQLAlchemy connection string
`SECRET_KEY`	(dev placeholder — change in production)	JWT signing secret
`ALGORITHM`	`HS256`	JWT signing algorithm
`ACCESS_TOKEN_EXPIRE_MINUTES`	`60`	JWT lifetime
`SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD`	—	Outbound email for notifications
`SMTP_FROM`	`ContractIQ <no-reply@contractiq.com>`	From-address for emails
`RENEWAL_REMINDER_DAYS`	`90,60,30,7`	Days-before-expiry thresholds for renewal reminders
If `SMTP_*` is left blank, notifications are still written to the database — email sending is simply skipped and logged rather than raising an error.
8. Database Migrations
Alembic (`alembic/env.py`) is wired to `app.database.Base.metadata` and reads `DATABASE_URL` from `.env`, so autogenerate picks up every model under `app/models/`.
```bash
# generate a migration after changing a model
alembic revision --autogenerate -m "describe your change"

# apply all pending migrations
alembic upgrade head
```
After migrating, you should see all 10 tables under `contractiq_db → public` in your database client: `users`, `contracts`, `contract_versions`, `obligations`, `renewals`, `notifications`, `reports`, `compliance_records`, `audit_logs`, `activities`.
9. Running with Docker
```bash
docker compose up --build
```
This starts a `postgres:16` container plus the API container, running migrations automatically on boot (`alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`). The API is then available at http://localhost:8000.
> The default `docker-compose.yml` uses hardcoded dev credentials (`postgres` / `postgres`, a placeholder `SECRET_KEY`). Override these via environment variables or a `.env` file for anything beyond local development.
10. API Reference
All endpoints except `/auth/register` and `/auth/login` require a `Bearer` JWT (obtained from `/auth/login`, form-encoded with `username`=email).
Auth — `/auth`
Method	Path	Description
POST	`/auth/register`	Create a new user
POST	`/auth/login`	Obtain a JWT access token
POST	`/auth/password-reset`	Reset a password
Users — `/users`
Method	Path	Description
GET	`/users/me`	Current user's profile
PUT	`/users/me`	Update current user's profile
GET	`/users`	List users
GET	`/users/{user_id}`	Get a user
PATCH	`/users/{user_id}/role`	Change a user's role
DELETE	`/users/{user_id}`	Delete a user (Administrator only)
Contracts — `/contracts`
Method	Path	Description
POST	`/contracts`	Create a contract (`created_by` taken from JWT)
GET	`/contracts`	List contracts
GET	`/contracts/{id}`	Get a contract
PUT	`/contracts/{id}`	Update a contract
PATCH	`/contracts/{id}/status`	Change status directly
POST	`/contracts/{id}/submit-review`	Draft → Under Review
POST	`/contracts/{id}/approve`	Under Review → Approved (Administrator/Legal Manager)
POST	`/contracts/{id}/activate`	Approved → Active
PATCH	`/contracts/{id}/assign`	Reassign owner
GET	`/contracts/{id}/compliance`	Live compliance snapshot for the contract
Obligations — `/obligations`, `/contracts/{id}/obligations`
Method	Path	Description
POST	`/obligations`	Create an obligation
GET	`/obligations`	List obligations
GET	`/obligations/{id}`	Get an obligation
GET	`/contracts/{id}/obligations`	List a contract's obligations
PUT	`/obligations/{id}`	Update an obligation
PATCH	`/obligations/{id}/status`	Change status
POST	`/obligations/{id}/complete`	Mark complete (server sets `completion_date`)
Overdue detection runs automatically whenever obligations are listed/fetched — any obligation past `due_date` and not `Completed` flips to `Overdue` and fires a notification.
Renewals — `/renewals`, `/contracts/{id}/renewals`
Method	Path	Description
POST	`/renewals`	Create a renewal for a contract
GET	`/renewals`	List renewals
GET	`/renewals/{id}`	Get a renewal
GET	`/contracts/{id}/renewals`	List a contract's renewals
PUT	`/renewals/{id}`	Update a renewal
PATCH	`/renewals/{id}/status`	Upcoming → In Progress, etc.
POST	`/renewals/{id}/renew`	Complete renewal — sets `Renewed`, pushes `new_expiry_date` to the contract, reactivates it if expired
Compliance — `/compliance`
Method	Path	Description
GET	`/compliance`	List all compliance records
GET	`/compliance/summary`	Aggregate compliance summary
GET	`/compliance/non-compliant`	Contracts currently non-compliant
GET	`/compliance/high-risk`	Contracts flagged high risk
Scoring rules live in `app/services/compliance_service.py`; each evaluation is persisted to `compliance_records` for history.
Notifications — `/notifications`
Method	Path	Description
GET	`/notifications`	Current user's notifications only
GET	`/notifications/{id}`	Get a notification
POST	`/notifications`	Create a notification
PATCH	`/notifications/{id}/read`	Mark as read
PATCH	`/notifications/read-all`	Mark all as read
11. Business Rules Cheat Sheet
Contract status transitions are enforced server-side — out-of-order transitions (e.g. approving a `Draft` contract) return `400`.
`created_by` / `completion_date` / other server-derived fields are always taken from the JWT or computed server-side, never trusted from the request body.
Obligation overdue flips happen lazily on read, not via a background job — no obligation is marked `Overdue` until it's next fetched or listed after its `due_date` has passed.
Renewal completion (`POST /renewals/{id}/renew`) is the only way a contract's expiry date and active status get updated as a result of a renewal.
Compliance is computed live, not cached — each call to `GET /contracts/{id}/compliance` re-evaluates the contract's obligations and writes a fresh `compliance_records` row.
12. Testing
```bash
pytest
```
`tests/test_health.py` covers the health-check endpoint; extend this directory as coverage grows.
13. Seed Data
```bash
python seed.py
```
Populates the database with sample users, contracts, obligations, and renewals for manual testing against Swagger UI.
14. Contributing
```bash
git add .
git commit -m "describe your change"
git push
```
`.env` is already excluded via `.gitignore` — never commit real credentials or a production `SECRET_KEY`.
15. License
MIT — see `LICENSE`.
