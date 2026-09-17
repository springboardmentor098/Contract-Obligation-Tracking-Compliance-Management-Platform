# 📑 ContractIQ

### Contract Obligation Tracking & Compliance Management Platform

<p align="center">
  <img src="https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Angular%20Material-UI-757575?style=for-the-badge&logo=angular&logoColor=white" />
</p>

<p align="center">
  <b>A full-stack platform for managing contracts, obligations, renewals, compliance, notifications, reports, and audit activities.</b>
</p>

---

## 🌟 Overview

**ContractIQ** is a full-stack web application designed to simplify and centralize contract lifecycle management and compliance tracking.

The platform enables organizations to create and manage contracts, track contractual obligations, monitor renewals and expiry dates, identify compliance and risk areas, receive notifications, generate reports, and maintain an audit trail of important activities.

ContractIQ combines a modern **Angular frontend**, **FastAPI backend**, and **PostgreSQL database** to provide an integrated and scalable contract management solution.

---

## ✨ Key Features

### 🔐 Authentication & Authorization
- Secure login and logout
- JWT-based authentication
- Protected routes
- Authentication token handling
- Role-based access control
- Role-based navigation
- Session and token expiration handling

### 📊 Dashboard
- Total contracts
- Active contracts
- Expired contracts
- Pending obligations
- Overdue obligations
- Upcoming renewals
- Compliance statistics
- Contract status distribution
- Obligation status distribution
- Interactive charts and summary cards

### 📄 Contract Management
- Create contracts
- View contracts
- View contract details
- Update contracts
- Search contracts
- Filter contracts
- Track contract status
- Track important contract dates
- Contract approval workflow

### 📌 Obligation Management
- Create obligations
- View obligations
- Update obligations
- Track obligation status
- Pending obligations
- Completed obligations
- Overdue obligations
- Contract-obligation association
- Search and filtering

### 🔄 Renewal Management
- Track upcoming renewals
- Monitor contract expiry dates
- Renewal status management
- Previous and new expiry dates
- Search and filtering
- Date-based filtering
- Renewal workflow

### 🛡️ Compliance Management
- Compliance status monitoring
- Compliant and non-compliant records
- Pending compliance items
- High-risk items
- Risk indicators
- Status and risk filtering
- Compliance history

### 🔔 Notifications
- View notifications
- Unread notification tracking
- Notification details
- Mark notifications as read
- Mark all notifications as read
- Notification search and filtering

### 📈 Reports & Analytics
- Contract statistics
- Obligation statistics
- Renewal statistics
- Compliance statistics
- Risk analysis
- Date-range filtering
- Charts and tables
- PDF report generation
- Excel report generation

### 🧾 Audit & Activity History
- Recent activities
- User actions
- Contract-related activities
- Status changes
- Activity descriptions
- Activity timestamps
- Audit history

### 👤 User Profile
- User information
- Email
- Role
- User ID
- Authenticated profile access

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────┐
│          Angular Frontend           │
│      Angular Material + TypeScript  │
└──────────────────┬──────────────────┘
                   │
                   │ REST API
                   ▼
┌─────────────────────────────────────┐
│           FastAPI Backend           │
│        Routers + Business Logic     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│             SQLAlchemy              │
│                 ORM                 │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│             PostgreSQL              │
│              Database               │
└─────────────────────────────────────┘