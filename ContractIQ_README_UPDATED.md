# ContractIQ

## Contract Obligation Tracking & Compliance Management Platform

ContractIQ is a FastAPI and PostgreSQL backend for managing the contract lifecycle, contractual obligations, renewals, compliance/risk evaluation, notifications, reporting support, audit logging, and operational activities.

This README describes the **implementation contained in this project**, including the database structure, API modules, authentication, workflows, migration setup, Docker setup, testing, and development instructions.

---

## 1. Project Overview

ContractIQ is designed around a simple business flow:

```text
User
  |
  v
Contract
  |
  +--------------------+
  |                    |
  v                    v
Contract Versions   Obligations
                       |
                       v
                  Notifications
  |
  +--------------------+
  |                    |
  v                    v
Renewals          Compliance Records
  |
  v
Notifications

Users
  +--> Reports
  +--> Audit Logs
  +--> Activities
```

The database keeps each responsibility in a separate relational table so that contract information, tasks, renewal decisions, notifications, compliance evaluations, and audit information can be maintained independently while remaining connected through foreign keys.

The original Sprint 3 design identifies the core tables as `users`, `contracts`, `contract_versions`, `obligations`, `renewals`, `notifications`, `reports`, `audit_logs`, and `activities`. The supplied implementation additionally contains `compliance_records` to retain contract compliance evaluation history.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM/database models |
| Pydantic | Request/response validation |
| PostgreSQL | Relational database |
| Alembic | Database migrations |
| JWT | Authentication |
| Docker | Containerization |
| Uvicorn | ASGI application server |
| Pytest | Testing |
| Swagger/OpenAPI | API documentation and testing |

---

## 3. Project Structure

```text
contractiq/
│
├── requirements.txt
├── alembic.ini
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── seed.py
├── README.md
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── core/
│   │   ├── security.py
│   │   └── deps.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── contract.py
│   │   ├── contract_version.py
│   │   ├── obligation.py
│   │   ├── renewal.py
│   │   ├── notification.py
│   │   ├── report.py
│   │   ├── compliance.py
│   │   ├── audit.py
│   │   └── activity.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── contract.py
│   │   ├── obligation.py
│   │   ├── renewal.py
│   │   ├── compliance.py
│   │   └── notification.py
│   │
│   ├── services/
│   │   ├── contract_service.py
│   │   ├── obligation_service.py
│   │   ├── compliance_service.py
│   │   └── notification_service.py
│   │
│   └── api/
│       ├── auth.py
│       ├── users.py
│       ├── contracts.py
│       ├── obligations.py
│       ├── renewals.py
│       ├── compliance.py
│       ├── contract_compliance.py
│       └── notifications.py
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_contractiq.py
│
├── docs/
│   ├── schema.dbml
│   └── ER_DIAGRAM.md
│
└── tests/
    └── test_health.py
```

---

# 4. Database Design

## 4.1 Tables

The implementation contains the following database entities:

1. `users`
2. `contracts`
3. `contract_versions`
4. `obligations`
5. `renewals`
6. `notifications`
7. `reports`
8. `compliance_records`
9. `audit_logs`
10. `activities`

### users

Stores users, login credentials, roles and account status.

Important fields:

```text
id
full_name
email
hashed_password
role
is_active
created_at
updated_at
```

### contracts

Stores the master record for each contract.

Important fields:

```text
id
title
contract_number
category
description
start_date
end_date
status
created_by
assigned_to
reviewed_at
approved_at
created_at
updated_at
```

### contract_versions

Stores contract-document/version history.

```text
id
contract_id
version_number
file_path
change_summary
created_by
created_at
```

### obligations

Stores contractual responsibilities.

```text
id
contract_id
title
description
obligation_type
due_date
assigned_to
status
completion_date
created_at
updated_at
```

### renewals

Stores renewal planning and history.

```text
id
contract_id
renewal_date
previous_expiry_date
new_expiry_date
status
assigned_to
notes
created_at
updated_at
```

### notifications

Stores alerts and reminders.

```text
id
user_id
contract_id
obligation_id
notification_type
title
message
status
scheduled_at
sent_at
read_at
created_at
updated_at
```

### reports

Stores generated-report metadata.

```text
id
report_type
title
generated_by
file_path
parameters
created_at
```

### compliance_records

Stores compliance evaluation history.

```text
id
contract_id
status
compliance_score
risk_level
completed_count
pending_count
overdue_count
notes
evaluated_at
created_at
updated_at
```

### audit_logs

Stores important actions and state changes.

```text
id
user_id
action
entity_type
entity_id
old_values
new_values
ip_address
created_at
```

### activities

Stores operational timeline events.

```text
id
user_id
activity_type
description
entity_type
entity_id
created_at
```

---

# 5. Database Relationships

The primary relationships are:

```text
users
  |
  +----< contracts
  |
  +----< contract_versions
  |
  +----< obligations
  |
  +----< renewals
  |
  +----< notifications
  |
  +----< reports
  |
  +----< audit_logs
  |
  +----< activities

contracts
  |
  +----< contract_versions
  |
  +----< obligations
  |
  +----< renewals
  |
  +----< notifications
  |
  +----< compliance_records

obligations
  |
  +----< notifications
```

Most relationships are one-to-many.

Foreign keys are used to maintain referential connections between records.

The project also contains:

```text
docs/schema.dbml
docs/ER_DIAGRAM.md
```

for database documentation.

---

# 6. User Roles

ContractIQ supports six application roles:

```text
Administrator
Legal Manager
Compliance Officer
Contract Manager
Department Head
Employee
```

Roles are used by the authorization layer to restrict protected operations.

Authentication and authorization are handled through JWT-based security and current-user dependencies.

---

# 7. Authentication

## Register

```http
POST /auth/register
```

Creates a user account.

## Login

```http
POST /auth/login
```

Returns an authentication token.

## Current User

```http
GET /users/me
```

Returns information about the authenticated user.

Protected endpoints require a valid JWT.

Expected security behavior:

```text
No/invalid authentication
        |
        v
   401 Unauthorized

Valid user but insufficient permission
        |
        v
    403 Forbidden
```

Passwords are stored using a password hash rather than plaintext.

---

# 8. Contract Management

## Contract APIs

```http
POST   /contracts
GET    /contracts
GET    /contracts/{contract_id}
PUT    /contracts/{contract_id}
PATCH  /contracts/{contract_id}/status
POST   /contracts/{contract_id}/submit-review
POST   /contracts/{contract_id}/approve
POST   /contracts/{contract_id}/activate
PATCH  /contracts/{contract_id}/assignment
```

Related information:

```http
GET /contracts/{contract_id}/obligations
GET /contracts/{contract_id}/renewals
GET /contracts/{contract_id}/compliance
```

## Contract lifecycle

```text
Draft
  |
  v
Under Review
  |
  v
Approved
  |
  v
Active
  |
  +----> Expired
  |
  +----> Terminated
```

Approval is restricted to the appropriate authorized roles.

The contract record contains:

- title
- contract number
- category
- description
- start date
- end date
- status
- creator
- assignee
- review timestamp
- approval timestamp

---

# 9. Contract Version Management

Contract versions preserve document history without overwriting previous version information.

Example:

```text
Contract: Vendor Agreement

Version 1
    |
    +-- Original contract

Version 2
    |
    +-- Pricing updated

Version 3
    |
    +-- Renewal terms updated
```

Each version stores:

- parent contract
- version number
- file path
- change summary
- creator
- creation timestamp

The `file_path` field is a storage reference. Production systems should use controlled object/file storage rather than storing confidential contract files directly in ordinary database columns.

---

# 10. Obligation Management

## Obligation APIs

```http
POST   /obligations
GET    /obligations
GET    /obligations/{obligation_id}
PUT    /obligations/{obligation_id}
PATCH  /obligations/{obligation_id}/status
POST   /obligations/{obligation_id}/complete
```

## Obligation workflow

```text
Pending
   |
   v
In Progress
   |
   v
Completed

Pending / In Progress
        |
        | due date missed
        v
      Overdue
```

Each obligation contains:

- contract
- title
- description
- obligation type
- due date
- assigned user
- status
- completion date

The service can detect incomplete obligations whose due date has passed and treat them as overdue.

---

# 11. Renewal Management

## Renewal APIs

```http
POST   /renewals
GET    /renewals
GET    /renewals/upcoming
GET    /renewals/{renewal_id}
PUT    /renewals/{renewal_id}
PATCH  /renewals/{renewal_id}/status
POST   /renewals/{renewal_id}/renew
```

## Renewal lifecycle

```text
Upcoming
    |
    v
In Progress
    |
    v
Renewed
```

Alternative outcomes:

```text
Upcoming
   |
   +----> Expired
   |
   +----> Cancelled

In Progress
   |
   +----> Cancelled
```

A renewal stores:

- contract
- renewal date
- previous expiry date
- new expiry date
- status
- responsible user
- notes
- timestamps

When a renewal is completed, the associated contract expiry can be updated.

Historical renewal records remain available for traceability.

---

# 12. Compliance and Risk Evaluation

ContractIQ includes a compliance service that evaluates obligations associated with contracts.

The evaluation considers:

- completed obligations
- pending/in-progress obligations
- overdue obligations
- compliance score
- risk level

## Current rule set

```text
2+ overdue obligations
        |
        v
High Risk

1 overdue obligation
        |
        v
Non-Compliant / Medium Risk

Delayed obligations without overdue items
        |
        v
Delayed / Medium Risk

Pending or In Progress obligations only
        |
        v
Pending / Low Risk

All obligations completed
        |
        v
Compliant / Low Risk
```

## Score

The current score calculation is:

```text
completed obligations
--------------------- × 100
total obligations
```

A contract with no obligations is treated as 100% for the current evaluation.

Compliance evaluations are stored in:

```text
compliance_records
```

This allows the system to retain historical compliance evaluations instead of keeping only the latest score.

## Compliance APIs

```http
GET /compliance
GET /compliance/summary
GET /compliance/non-compliant
GET /compliance/high-risk
GET /compliance/contracts/{contract_id}/history
```

---

# 13. Notification Management

## Notification APIs

```http
GET    /notifications
GET    /notifications/{notification_id}
POST   /notifications
PATCH  /notifications/{notification_id}/read
PATCH  /notifications/read-all
```

Notifications may relate to:

- contracts
- obligations
- renewal events
- compliance events
- deadlines
- overdue conditions
- system events

A notification supports:

```text
Unread
   |
   v
Read
```

Timestamp fields provide additional tracking:

```text
scheduled_at
sent_at
read_at
```

A user should only be able to access their own notifications.

---

# 14. Reporting

The `reports` table stores metadata for generated reports.

Fields include:

```text
report_type
title
generated_by
file_path
parameters
created_at
```

This allows reports to be associated with the user who generated them while keeping the generated file/reference separate from the database record.

---

# 15. Audit Logging

Audit logging provides traceability for important system actions.

Typical information includes:

```text
Who performed the action?
What action was performed?
Which entity was affected?
Which record was affected?
What was the old state?
What is the new state?
What IP address was recorded?
When did it happen?
```

The database supports:

```text
old_values
new_values
```

which can be used to preserve before/after state.

Audit records should be treated as append-only from the application perspective.

---

# 16. Activities

Activities provide an operational timeline.

An activity can contain:

```text
activity_type
description
entity_type
entity_id
user_id
created_at
```

Examples include:

```text
Contract created
Contract assigned
Contract reviewed
Contract approved
Obligation created
Obligation completed
Renewal updated
Status changed
```

Activities are intentionally simpler than audit logs.

---

# 17. Configuration

Configuration is loaded from environment variables.

Copy:

```text
.env.example
```

to:

```text
.env
```

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/contractiq_db
SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Use a strong secret in real environments.

Never commit the real `.env` file or production secrets to GitHub.

---

# 18. Local Installation

## Step 1 — Clone or extract the project

```bash
cd contractiq
```

## Step 2 — Create virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

## Step 4 — Configure environment

Windows:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env` and set the PostgreSQL connection and secret key.

---

# 19. PostgreSQL Setup

Create a database named:

```text
contractiq_db
```

Example PostgreSQL command:

```sql
CREATE DATABASE contractiq_db;
```

Configure:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/contractiq_db
```

Make sure PostgreSQL is running before applying migrations.

---

# 20. Alembic Migrations

The project includes Alembic configuration.

Run:

```bash
alembic upgrade head
```

This applies the initial database migration.

To create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe your change"
```

Review the generated migration before applying it.

Then:

```bash
alembic upgrade head
```

To check the current migration:

```bash
alembic current
```

To see migration history:

```bash
alembic history
```

---

# 21. Seed Data

The project contains:

```text
seed.py
```

Run:

```bash
python seed.py
```

This can be used to populate development/demo records.

For production, replace demo credentials and data with secure real configuration.

---

# 22. Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 23. Swagger Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger allows you to:

1. Register a user.
2. Login.
3. Obtain the JWT.
4. Authorize Swagger.
5. Create contracts.
6. Create obligations.
7. Create renewals.
8. Check compliance.
9. Create/read notifications.
10. Test protected endpoints.

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# 24. Docker Setup

The project contains:

```text
Dockerfile
docker-compose.yml
```

Start the application and PostgreSQL with:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

Stop and remove containers:

```bash
docker compose down
```

The Docker setup is intended to simplify local development by providing the backend/database environment together.

---

# 25. API Endpoint Reference

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /users/me
```

## Contracts

```text
POST   /contracts
GET    /contracts
GET    /contracts/{contract_id}
PUT    /contracts/{contract_id}
PATCH  /contracts/{contract_id}/status
POST   /contracts/{contract_id}/submit-review
POST   /contracts/{contract_id}/approve
POST   /contracts/{contract_id}/activate
PATCH  /contracts/{contract_id}/assignment
GET    /contracts/{contract_id}/obligations
GET    /contracts/{contract_id}/renewals
GET    /contracts/{contract_id}/compliance
```

## Obligations

```text
POST   /obligations
GET    /obligations
GET    /obligations/{obligation_id}
PUT    /obligations/{obligation_id}
PATCH  /obligations/{obligation_id}/status
POST   /obligations/{obligation_id}/complete
```

## Renewals

```text
POST   /renewals
GET    /renewals
GET    /renewals/upcoming
GET    /renewals/{renewal_id}
PUT    /renewals/{renewal_id}
PATCH  /renewals/{renewal_id}/status
POST   /renewals/{renewal_id}/renew
```

## Compliance

```text
GET /compliance
GET /compliance/summary
GET /compliance/non-compliant
GET /compliance/high-risk
GET /compliance/contracts/{contract_id}/history
```

## Notifications

```text
GET    /notifications
GET    /notifications/{notification_id}
POST   /notifications
PATCH  /notifications/{notification_id}/read
PATCH  /notifications/read-all
```

---

# 26. Recommended Testing Workflow

After starting the server, open Swagger:

```text
http://127.0.0.1:8000/docs
```

Test in this order:

### Test 1 — Register

```text
POST /auth/register
```

### Test 2 — Login

```text
POST /auth/login
```

Copy the JWT token.

### Test 3 — Authorize

Use Swagger's:

```text
Authorize
```

button.

### Test 4 — Create Contract

```text
POST /contracts
```

### Test 5 — Create Obligation

```text
POST /obligations
```

Assign it to a valid user.

### Test 6 — Update Obligation

```text
PATCH /obligations/{obligation_id}/status
```

### Test 7 — Complete Obligation

```text
POST /obligations/{obligation_id}/complete
```

### Test 8 — Create Renewal

```text
POST /renewals
```

### Test 9 — Check Compliance

```text
GET /compliance
GET /compliance/summary
GET /compliance/high-risk
```

### Test 10 — Notifications

```text
GET /notifications
POST /notifications
PATCH /notifications/{notification_id}/read
PATCH /notifications/read-all
```

---

# 27. Error Handling

The API should use standard HTTP responses.

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
```

Typical meanings:

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Invalid business request |
| 401 | Authentication missing/invalid |
| 403 | User lacks permission |
| 404 | Resource not found |
| 422 | Request validation failed |
| 500 | Unexpected server-side error |

---

# 28. Security Notes

Before production deployment:

- Change `SECRET_KEY`.
- Never commit `.env`.
- Use HTTPS.
- Use secure PostgreSQL credentials.
- Use a managed secrets system where appropriate.
- Keep password hashes only; never store plaintext passwords.
- Restrict protected API endpoints.
- Validate ownership before returning user-specific notifications.
- Review role permissions.
- Keep audit records protected from unauthorized modification.
- Use controlled document storage.
- Configure production CORS carefully.
- Use database backups.
- Monitor authentication and application logs.

---

# 29. Production Improvements

The current project is suitable as a backend project and development foundation. For a production deployment, consider:

### Background jobs

Use a worker/scheduler such as Celery/Redis or another job system for:

- renewal reminders
- overdue obligation detection
- compliance notifications
- email delivery

### Document storage

Use object storage such as an enterprise storage service for contract files and evidence.

Keep only references such as:

```text
file_path
```

in the database.

### Email

Configure SMTP or an email delivery provider for:

- renewal reminders
- overdue alerts
- compliance alerts
- approval notifications

### Observability

Add:

- structured logging
- metrics
- tracing
- error monitoring
- health/readiness checks

### Database

Use:

- managed PostgreSQL
- automated backups
- connection pooling
- migration review
- appropriate indexes
- least-privilege database credentials

---

# 30. Development Workflow

Recommended workflow:

```text
1. Update SQLAlchemy model
          |
          v
2. Update Pydantic schema
          |
          v
3. Update service logic
          |
          v
4. Update API router
          |
          v
5. Create Alembic migration
          |
          v
6. Review migration
          |
          v
7. Apply migration
          |
          v
8. Test through Swagger/Pytest
```

For database changes:

```bash
alembic revision --autogenerate -m "your change"
alembic upgrade head
```

---

# 31. Documentation Files

The project contains database documentation:

```text
docs/schema.dbml
docs/ER_DIAGRAM.md
```

These files complement the Sprint 3 database-design report.

The database design report documents:

- table purposes
- columns
- data types
- primary keys
- foreign keys
- relationships
- ER structure
- design decisions
- implementation alignment

---

# 32. Difference Between Proposed Design and Implementation

The supplied Sprint 3 report describes a proposed database design. The current backend implementation uses some different field names and structures.

Examples:

| Original proposal | Current implementation |
|---|---|
| `password_hash` | `hashed_password` |
| `owner_id` | `created_by` / `assigned_to` |
| `version_no` | `version_number` |
| `document_name` | `file_path` |
| `change_note` | `change_summary` |
| `frequency` | `obligation_type` |
| `completion_at` concept | `completion_date` |
| `notice_days` | Not present in current model |
| `decision` | `status` |
| `subject` | `title` |
| `renewal_id` in notifications | Not present in current implementation |
| `contract_id` in reports | Not present in current implementation |
| `JSONB filters` | `parameters` |
| `contract_id` in audit logs | Generic `entity_type` + `entity_id` |
| `contract_id` / `obligation_id` in activities | Generic `entity_type` + `entity_id` |
| — | `compliance_records` added in implementation |

The updated database-design report was prepared specifically to document the implementation rather than treating every originally proposed field as already implemented.

---

# 33. Project Completion Checklist

```text
[✓] FastAPI application
[✓] PostgreSQL database integration
[✓] SQLAlchemy models
[✓] Pydantic schemas
[✓] JWT authentication
[✓] Role-based authorization
[✓] Contract management
[✓] Contract approval workflow
[✓] Contract version management
[✓] Obligation management
[✓] Overdue obligation detection
[✓] Renewal management
[✓] Compliance/risk evaluation
[✓] Compliance history
[✓] Notification management
[✓] Audit logging
[✓] Activity tracking
[✓] Reporting model
[✓] Alembic migration
[✓] DBML schema
[✓] ER documentation
[✓] Docker configuration
[✓] Seed script
[✓] Test structure
[✓] Swagger/OpenAPI
```

---

# 34. Quick Start

For the fastest local setup:

```bash
cd contractiq

python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Configure:

```bash
copy .env.example .env
```

Create PostgreSQL database:

```text
contractiq_db
```

Migrate:

```bash
alembic upgrade head
```

Optional seed:

```bash
python seed.py
```

Start:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 35. Docker Quick Start

If Docker is installed:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 36. Final Notes

ContractIQ provides the backend foundation for a contract-obligation and compliance-management platform.

The central workflow is:

```text
User
 ↓
Contract
 ↓
Contract Version
 ↓
Obligation
 ↓
Assignment
 ↓
Due Date
 ↓
Pending / In Progress
 ↓
Completed
      \
       → Overdue
 ↓
Compliance Evaluation
 ↓
Risk / Compliance Status
 ↓
Notifications
```

Renewals operate alongside the contract lifecycle:

```text
Contract Expiry
      ↓
Upcoming Renewal
      ↓
In Progress
      ↓
Renewed / Cancelled / Expired
```

The combination of relational database design, JWT security, RBAC, lifecycle APIs, compliance evaluation, notifications, audit information and migration support provides a structured backend foundation for the ContractIQ application.

---

## License

This project is intended for educational, internship, demonstration, and development use unless a separate license is supplied by the project owner.

## Author / Project

**ContractIQ**

Contract Obligation Tracking & Compliance Management Platform
