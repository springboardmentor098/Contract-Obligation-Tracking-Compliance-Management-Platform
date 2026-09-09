# ContractIQ
## Contract Obligation Tracking & Compliance Management Platform

ContractIQ is a full-stack web application designed to manage contracts, track contractual obligations, monitor renewals, and analyze compliance and risk.

The platform provides a centralized dashboard for viewing contract and compliance information and supports report generation in PDF and Excel formats.

---

## 🚀 Features

### Contract Management
- Create and manage contracts
- Track contract status
- Track contract categories
- Manage contract ownership and assignments
- Monitor contract expiry

### Obligation Tracking
- Create contractual obligations
- Assign obligations to users
- Track obligation status
- Monitor due dates
- Identify overdue obligations

### Renewal Management
- Track contract renewals
- Monitor renewal status
- Track upcoming contract expirations
- Identify renewals requiring attention

### Compliance Monitoring
- Calculate contract compliance
- Track compliance status
- Calculate compliance scores
- Identify non-compliant contracts
- Identify high-risk contracts

### Dashboard & Analytics
- Contract statistics
- Obligation statistics
- Renewal statistics
- Compliance statistics
- Risk analysis
- Interactive charts using Chart.js

### Reports & Exports
- Contract Analytics Report
- Obligation Analytics Report
- Renewal Analytics Report
- Compliance Analytics Report
- PDF report export
- Excel report export

### Authentication
- JWT-based authentication
- Protected API endpoints
- Role-based user information
- Secure frontend token handling

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT Authentication
- ReportLab
- OpenPyXL

### Frontend
- Angular
- TypeScript
- Angular Material
- HTML
- LESS
- Chart.js

### Database
- PostgreSQL

### Development Tools
- VS Code
- Swagger / OpenAPI
- Git & GitHub

---

## 📁 Project Structure

```text
Contract-Obligation-Tracking-Compliance-Management-Platform/
│
├── app/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── dependencies.py
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── frontend/
│   └── contractiq-frontend/
│
├── .env
├── requirements.txt
└── README.md