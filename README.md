# ContractIQ Backend — Contract Obligation Tracking & Compliance Management Platform

FastAPI + SQLAlchemy + PostgreSQL backend. This build includes the fully working
**User Management module** (Create, Read, Update, Delete) as covered in class.

## Project Structure

```
contractiq_backend/
│
├── app/
│   ├── api/
│   │   └── users.py            # User Management endpoints (CRUD)
│   ├── core/
│   │   └── config.py           # Settings (reads DATABASE_URL from .env)
│   ├── database/
│   │   └── database.py         # engine, SessionLocal, Base, get_db, test_database_connection
│   ├── middleware/              # (reserved for future custom middleware)
│   ├── models/
│   │   └── user.py             # SQLAlchemy User model
│   ├── repositories/
│   │   └── user_repository.py  # Raw DB query functions
│   ├── schemas/
│   │   └── user.py             # Pydantic request/response models
│   ├── services/
│   │   └── user_service.py     # Business logic + duplicate-user checks
│   ├── utils/
│   │   └── security.py         # Password hashing (passlib/bcrypt)
│   └── main.py                 # FastAPI app entrypoint
│
├── migrations/                  # Alembic migration environment
│   ├── versions/
│   └── env.py                  # Wired to app's Base metadata + .env DATABASE_URL
├── tests/
│   └── test_users.py           # Pytest suite covering all 6 CRUD test scenarios
│
├── alembic.ini
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup (Visual Studio Code)

### 1. Open the folder in VS Code
`File > Open Folder…` → select the extracted `contractiq_backend` folder.

### 2. Create and activate a virtual environment

Open a terminal in VS Code (`` Ctrl+` ``):

```bash
python -m venv venv
```

Activate it:

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (cmd)
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

Select this interpreter in VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → pick the one inside `venv`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

Open **pgAdmin 4** → expand your PostgreSQL server → right-click **Databases** → **Create** → **Database…** → name it `contractiq_db` → Save.

### 5. Configure environment variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

Edit `.env` and set your actual PostgreSQL password:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/contractiq_db
```

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

On startup you should see `Database connection successful.` in the terminal, confirming PostgreSQL is reachable. The app also auto-creates the `users` table on startup via `Base.metadata.create_all`.

### 7. Open the API docs

Visit **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

## (Optional) Using Alembic for migrations instead of auto-create

The project ships with Alembic already initialized and pointed at your `.env` database and models.

```bash
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

If you use Alembic to manage the schema, you can remove the `Base.metadata.create_all(bind=engine)` line in `app/main.py` to avoid the two mechanisms conflicting.

## User Management API (`/users`)

| Method | Endpoint              | Description                     |
|--------|------------------------|----------------------------------|
| POST   | `/users/`              | Create a new user                |
| GET    | `/users/`               | List all users                   |
| GET    | `/users/{user_id}`      | Retrieve a single user           |
| PUT    | `/users/{user_id}`      | Update a user                    |
| DELETE | `/users/{user_id}`      | Delete a user                    |

Sample `POST /users/` body:

```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "password": "securePass123"
}
```

- Duplicate `username` or `email` → **409 Conflict**
- Non-existent `user_id` on GET/PUT/DELETE → **404 Not Found**
- Passwords are hashed with bcrypt before being stored — never returned in responses.

## Task Checklist (28-07-2026: User Management CRUD)

All 6 scenarios are implemented and covered by `tests/test_users.py`:

1. ✅ Create at least 5 new users
2. ✅ Retrieve users
3. ✅ Update 2 existing users
4. ✅ Delete one user
5. ✅ Retrieving a deleted user returns 404 (`None` at the service layer)
6. ✅ Creating a user with an existing username/email returns 409 Conflict

### Run the tests

```bash
pip install pytest
pytest tests/test_users.py -v
```

These tests run against an in-memory SQLite database, so they work even before PostgreSQL is connected — useful for verifying the logic quickly in VS Code.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Pydantic / pydantic-settings** — data validation & config
- **Alembic** — database migrations
- **passlib[bcrypt]** — password hashing
- **python-jose[cryptography]** — reserved for JWT auth (next module)

## Notes

- `email-validator` and `bcrypt==4.0.1` were added to `requirements.txt` beyond the exact class list — they're required for `EmailStr` validation and for `passlib` to work correctly with newer bcrypt releases (a known compatibility issue). Everything else matches the packages given in class.
- `python-jose[cryptography]` and `passlib[bcrypt]` are already installed and a `hash_password`/`verify_password` helper exists in `app/utils/security.py`, ready for the authentication/JWT module that typically follows User Management.
