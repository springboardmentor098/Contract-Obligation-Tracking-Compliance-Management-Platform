# ContractIQ

## Contract Obligation Tracking & Compliance Management Platform

ContractIQ is a full-stack web application designed to manage contracts, track contractual obligations, monitor renewals, evaluate compliance, analyze contract risks, and generate business reports.

The application provides a centralized dashboard where users can manage the complete contract lifecycle through an Angular frontend integrated with a FastAPI backend and PostgreSQL database.

---

## 🚀 Key Features

### 1. Contract Management

- Create contracts
- View contract details
- Update contract information
- Track contract number and category
- Manage contract ownership and assignments
- Track contract start and expiry dates
- Monitor contract status
- Support statuses such as:
  - Draft
  - Under Review
  - Approved
  - Active
  - Expired
  - Terminated

---

### 2. Obligation Management

- Create contractual obligations
- Associate obligations with contracts
- Assign obligations to users
- Track obligation due dates
- Update obligation information
- Track obligation status
- Complete obligations
- Identify overdue obligations
- Support obligation statuses such as:
  - Pending
  - In Progress
  - Completed
  - Delayed
  - Overdue

---

### 3. Renewal Management

- Create renewal records
- Associate renewals with contracts
- Track previous expiry dates
- Track new expiry dates
- Track renewal dates
- Assign renewal responsibilities
- Update renewal information
- Track renewal status
- Identify contracts requiring renewal attention

---

### 4. Compliance Monitoring

ContractIQ provides contract-level compliance analysis based on contractual obligations.

Features include:

- Compliance status tracking
- Compliance score calculation
- Compliant contract identification
- Non-compliant contract identification
- High-risk contract identification
- Overdue obligation analysis
- Compliance summary

---

### 5. Dashboard & Analytics

The dashboard provides real-time information from the backend APIs.

Dashboard includes:

- Total contracts
- Active contracts
- Draft contracts
- Contracts under review
- Approved contracts
- Expired contracts
- Terminated contracts
- Total obligations
- Pending obligations
- In-progress obligations
- Completed obligations
- Delayed obligations
- Overdue obligations
- Upcoming renewals
- Renewed contracts
- Compliance statistics
- High-risk contracts

Interactive visualizations are implemented using Chart.js.

### Dashboard Charts

- Contract status distribution
- Obligation status distribution
- Compliance distribution
- Contract category distribution

All dashboard statistics are loaded dynamically from the FastAPI backend.

---

## 🔔 Notifications

ContractIQ includes notification management functionality.

Features include:

- View user notifications
- View notification details
- Track notification status
- Mark individual notifications as read
- Mark all notifications as read
- Associate notifications with contracts and obligations

Notifications are scoped to the authenticated user.

---

## 📊 Reports & Analytics

ContractIQ provides dedicated analytics APIs and report exports.

### Analytics

- Contract summary
- Obligation summary
- Renewal summary
- Compliance summary
- Risk analysis

### Report Exports

Reports can be exported in:

- PDF
- Excel (.xlsx)

Available reports:

- Contract Report
- Obligation Report
- Renewal Report
- Compliance Report

---

## 📝 Audit History

ContractIQ includes an Audit History module for viewing application activity recorded in the audit log system.

Audit information can include:

- User
- Action
- Entity type
- Entity ID
- Previous values
- New values
- IP address
- Date and time

The frontend displays an appropriate empty state when no audit records are available.

---

## 🔐 Authentication & Authorization

ContractIQ uses JWT-based authentication.

### Authentication Features

- Login
- JWT access token
- Protected frontend routes
- Protected FastAPI endpoints
- Authorization header handling
- Session logout
- Authentication guard
- Login validation
- API authentication error handling

The Angular application automatically attaches the JWT token to authenticated API requests using an HTTP interceptor.

---

## 🏗️ System Architecture

The application follows a layered full-stack architecture:

```text
Angular Frontend
       │
       │ HTTP / REST API
       ▼
Angular Services
       │
       ▼
FastAPI Backend
       │
       ├── Routers
       ├── Services
       ├── Schemas
       ├── Authentication
       │
       ▼
SQLAlchemy ORM
       │
       ▼
PostgreSQL Database