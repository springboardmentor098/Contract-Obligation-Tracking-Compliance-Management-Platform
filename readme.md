# ContractIQ – Contract Obligation Tracking & Compliance Management Platform

A full-stack Contract Lifecycle Management (CLM) platform developed to streamline contract administration, obligation tracking, renewals, compliance monitoring, reporting, and user management.

## 🌐 Live Demo

**Deployed Application**

👉 https://contractiq-beryl.vercel.app/

---

# Project Overview

ContractIQ is an enterprise Contract Lifecycle Management (CLM) system that enables organizations to efficiently manage contracts from creation to expiration.

The platform provides modules for:

- Dashboard & Analytics
- Contract Management
- Obligation Tracking
- Renewal Management
- Compliance Monitoring
- Notifications
- Reports
- Activity Logs
- User Management
- Authentication & Authorization

---

# Features

## Dashboard

- Contract summary cards
- Active / Expired contracts
- Pending obligations
- Upcoming renewals
- Compliance overview
- Interactive charts

---

## Contract Management

- Create contracts
- Edit contracts
- Upload contracts
- Search & filter
- Department categorization
- Contract lifecycle tracking

---

## Obligation Management

- Create obligations
- Assign owners
- Track completion
- Due dates
- Priority management
- Status tracking

---

## Renewal Management

- Upcoming renewals
- Renewal reminders
- Expired contracts
- Renewal status tracking

---

## Compliance Management

- Compliance dashboard
- Compliance score
- Risk level monitoring
- Contract compliance tracking
- Compliance history

---

## Reports

Generate reports for:

- Compliance
- Contracts
- Obligations
- Renewals
- Audit Logs

---

## Notifications

- Upcoming deadlines
- Contract reminders
- Renewal alerts
- Compliance alerts

---

## Activity Logs

Tracks major system events including:

- User Login
- User Logout
- Contract Creation
- Contract Updates
- Contract Deletion
- Report Generation
- User Management Actions

---

## Authentication

- JWT Authentication
- Secure Login
- Protected Routes
- Session Management
- Password Hashing (bcrypt)

---

## Tech Stack

### Frontend

- React
- TanStack Router
- React Query
- TypeScript
- Tailwind CSS
- Chart.js
- React ChartJS 2
- Lucide Icons

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT Authentication
- bcrypt Password Hashing

### Database

- PostgreSQL

### Deployment

Frontend:
- Vercel

Backend:
- FastAPI

---

# Project Structure

```
Contract-Obligation-Tracking-Compliance-Management-Platform

├── backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│
└── README.md
```

---

# Local Installation

## Clone Repository

```bash
git clone <repository-url>
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```

Backend runs on

```
http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on

```
http://localhost:3000
```

(or the configured Vite port)

---

# Deployment

Frontend is deployed on **Vercel**.

Live URL:

https://contractiq-beryl.vercel.app/

---

# Deployment Notes

The original project repository belonged to the project owner.

Since Vercel only allows deployment from repositories accessible under the connected GitHub account, the deployment process was:

1. Fork the original repository into my GitHub account.
2. Clone the fork locally.
3. Switch to my development branch (`saivarun`).
4. Push the latest changes to my fork.
5. Import the forked repository into Vercel.
6. Configure the project settings.
7. Deploy the frontend.

This preserves the original repository while allowing independent deployment and testing.

---

# Git Workflow

```bash
git checkout saivarun

git add .

git commit -m "Sprint 14: Frontend foundation, dashboard, authentication and API integration"

git push origin saivarun
```

---

# Sprint Coverage

### Sprint 13

- Reports & Analytics APIs
- Dashboard data aggregation
- Compliance summary
- Contract statistics
- Renewal summary
- Obligation summary
- Chart-ready backend data

### Sprint 14

- Frontend foundation
- Dashboard implementation
- API integration
- Authentication
- Protected routes
- Responsive layout
- Navigation
- Dashboard visualization

---

# Future Improvements

- PDF report generation
- Report downloads
- Email notifications
- RBAC (Role-Based Access Control)
- Contract document preview
- Digital signatures
- Advanced analytics
- Audit exports

---

# Author

**Sai Varun**

B.Tech – Big Data Analytics

SRM Institute of Science and Technology, Ramapuram

GitHub:
https://github.com/SaiVarun-26

---

# License

This project was developed for educational and academic purposes as part of the ContractIQ Contract Lifecycle Management project.
