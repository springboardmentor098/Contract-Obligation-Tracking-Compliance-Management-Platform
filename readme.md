# 📄 ContractIQ – Contract Obligation Tracking & Compliance Management Platform

A full-stack **Contract Lifecycle Management (CLM)** platform developed using **FastAPI, React (TanStack Start), PostgreSQL, and Tailwind CSS**. ContractIQ helps organizations efficiently manage contracts, track obligations, monitor renewals, ensure compliance, generate business insights, and maintain audit trails through a secure and user-friendly interface.

---

# 🌐 Live Demo

**Application URL**

👉 **https://contractiq-beryl.vercel.app/**

---

# 👤 Demo Login Credentials

Use the following accounts to explore the application.

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@contractiq.com | Admin@123 |
| **Legal Manager** | legal@contractiq.com | Legal@123 |
| **Contract Manager** | contract@contractiq.com | Contract@123 |
| **Compliance Officer** | compliance@contractiq.com | Compliance@123 |
| **Viewer** | viewer@contractiq.com | Viewer@123 |

> **Note:** Passwords are securely stored in PostgreSQL using **bcrypt hashing**. These credentials are intended for demonstration and testing purposes.

---

# 📌 Project Overview

ContractIQ is an enterprise Contract Lifecycle Management (CLM) platform that centralizes the management of contracts throughout their lifecycle—from creation to expiration.

The system enables organizations to:

- Manage contracts
- Track contractual obligations
- Monitor renewal dates
- Analyze compliance status
- Generate reports
- Maintain audit logs
- Receive important notifications
- Manage users securely

---

# ✨ Features

## 📊 Dashboard

- Total Contracts
- Active Contracts
- Expired Contracts
- Pending Obligations
- Overdue Obligations
- Upcoming Renewals
- Compliance Summary
- Interactive Charts

---

## 📁 Contract Management

- Create Contracts
- Edit Contracts
- Upload Contracts
- Search Contracts
- Department-wise Classification
- Contract Status Tracking
- Contract Lifecycle Management

---

## ✅ Obligation Management

- Create Obligations
- Assign Responsibilities
- Due Date Tracking
- Priority Management
- Pending & Completed Status
- Overdue Monitoring

---

## 🔄 Renewal Management

- Upcoming Renewals
- Expired Contracts
- Renewal Status
- Renewal Alerts
- Date-based Filtering

---

## 🛡 Compliance Management

- Compliance Dashboard
- Compliance Statistics
- Risk Level Monitoring
- Compliance Score
- Contract Compliance History

---

## 📑 Reports

Generate reports for:

- Contract Summary
- Obligations
- Renewals
- Compliance
- Audit History

---

## 🔔 Notifications

- Upcoming Deadlines
- Contract Alerts
- Renewal Notifications
- Compliance Alerts

---

## 📜 Activity Logs

Automatically records:

- User Login
- User Logout
- Contract Creation
- Contract Updates
- Contract Deletion
- Report Generation
- User Activities

---

## 🔐 Authentication

- JWT Authentication
- Secure Login
- Password Hashing using bcrypt
- Protected Routes
- Session Management

---

# 🛠 Tech Stack

## Frontend

- React
- TanStack Start
- TanStack Router
- React Query
- TypeScript
- Tailwind CSS
- Chart.js
- React ChartJS 2
- Lucide React Icons

---

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- JWT Authentication
- bcrypt Password Hashing

---

## Database

- PostgreSQL

---

## Deployment

Frontend is deployed on **Vercel**.

Live Application:

👉 **https://contractiq-beryl.vercel.app/**

---

# 📂 Project Structure

```
Contract-Obligation-Tracking-Compliance-Management-Platform
│
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

# 🚀 Local Setup

## 1. Clone Repository

```bash
git clone https://github.com/<your-github-username>/Contract-Obligation-Tracking-Compliance-Management-Platform.git
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

## 3. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:8080
```

---

# 📦 Deployment Process

The original project repository belonged to the project owner.

Since deployment permissions were unavailable from the original repository, the following workflow was used:

1. Forked the original repository into my GitHub account.
2. Cloned the fork locally.
3. Worked on my development branch (`saivarun`).
4. Pushed the latest commits to the fork.
5. Connected the forked repository to **Vercel**.
6. Configured the build settings.
7. Successfully deployed the frontend.

This workflow preserved the original repository while enabling independent deployment and testing.

---

# 📈 Sprint Coverage

## ✅ Sprint 13 – Reports, Analytics & Dashboard APIs

Implemented:

- Contract Summary APIs
- Obligation Summary APIs
- Renewal Summary APIs
- Compliance Summary APIs
- Dashboard Statistics
- Chart-ready API Responses
- SQLAlchemy Aggregation Queries
- Swagger Tested APIs

---

## ✅ Sprint 14 – Frontend Foundation & Dashboard Integration

Implemented using **React (TanStack Start)** instead of Angular.

Completed:

- Responsive Application Layout
- Sidebar Navigation
- Header
- Dashboard UI
- Dashboard API Integration
- Authentication
- Login
- Logout
- Protected Routes
- API Services
- Loading States
- Error Handling
- Responsive Design

---

# 🔒 Security Features

- JWT Authentication
- bcrypt Password Hashing
- Protected API Routes
- Input Validation using Pydantic
- SQLAlchemy ORM
- PostgreSQL Data Storage

---

# 📋 Git Workflow

```bash
git checkout saivarun

git add .

git commit -m "Sprint 14: Frontend foundation, dashboard, authentication and API integration"

git push origin saivarun
```

---

# 🚀 Future Enhancements

- Role-Based Access Control (RBAC)
- PDF Report Generation
- Report Downloads
- Email Notifications
- Digital Signature Support
- Contract Version History
- Document Preview
- Advanced Analytics
- Export to Excel
- Audit Report Downloads

---

# 👨‍💻 Author

**Sai Varun**

**B.Tech – Big Data Analytics**

**SRM Institute of Science and Technology, Ramapuram**

GitHub:
https://github.com/SaiVarun-26

---

# 📄 License

This project was developed for academic and educational purposes as part of the **ContractIQ – Contract Obligation Tracking & Compliance Management Platform** project.

---

# 🙏 Acknowledgements

Special thanks to the project mentors and team members for their guidance throughout the development of the ContractIQ platform.
