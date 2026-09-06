# Sprint 13 – Reports, Analytics and Dashboard Development

## 1. Sprint Overview

**Sprint Name:** Sprint 13 – Reports, Analytics and Dashboard Development

**Project:** Contract-Obligation-Tracking-Compliance-Management-Platform

Sprint 13 focuses on developing the reporting, analytics, and dashboard backend functionality for the Contract-Obligation-Tracking-Compliance-Management-Platform.

The main purpose of this sprint is to provide aggregated information about contracts, obligations, renewals, and compliance using the existing application models and database data.

The sprint also provides dashboard-ready API responses that can be consumed by a frontend dashboard.

---

## 2. Sprint Objective

The main objectives of Sprint 13 are:

- Develop Contract Summary APIs.
- Develop Contract Status Distribution APIs.
- Develop Obligation Summary APIs.
- Develop Obligation Status Distribution APIs.
- Develop Renewal Reports.
- Develop Compliance Summary APIs.
- Develop a Dashboard API.
- Implement SQLAlchemy aggregation queries.
- Create Pydantic response schemas.
- Support required filters.
- Handle empty results.
- Handle invalid input and date-range validation.
- Test APIs using Swagger UI.
- Provide Swagger screenshots as implementation evidence.
- Create a dashboard layout/wireframe.
- Document the updated project structure.
- Prepare the Sprint 13 implementation for GitHub submission.

---

## 3. Sprint Requirements

### 3.1 Contract Summary

The system should provide:

- Total contracts.
- Active contracts.
- Expired contracts.
- Contracts pending approval.
- Contracts grouped by status.

### 3.2 Obligation Summary

The system should provide:

- Total obligations.
- Pending obligations.
- Completed obligations.
- Overdue obligations.
- Obligations grouped by status.

### 3.3 Renewal Summary

The system should provide:

- Upcoming renewals.
- Expired contracts.
- Contracts requiring immediate attention.
- Renewals within a selected date range.

### 3.4 Compliance Summary

The system should provide:

- Compliant contracts.
- Non-compliant contracts.
- High-risk contracts.
- High-risk obligations.
- Overall compliance statistics.

### 3.5 Dashboard

The backend should provide:

- Summary cards.
- Contract status distribution.
- Obligation status distribution.
- Upcoming renewals.
- Compliance statistics.
- Chart-ready data.

---

## 4. Sprint 13 Architecture

The Sprint 13 reporting functionality follows the existing application architecture.

```text
Frontend / Dashboard
        |
        v
FastAPI Application
        |
        v
Reports Router
        |
        +-----------------------+
        |                       |
        v                       v
Contract Reports          Obligation Reports
        |
        +-----------------------+
        |
        v
Renewal Reports
        |
        v
Compliance Reports
        |
        v
Dashboard API
        |
        v
SQLAlchemy ORM Queries
        |
        v
Existing Database Models
        |
        +----------------+
        |                |
        v                v
    Contract         Obligation
        |
        +----------------+
        |
        v
      Renewal
        |
        v
    Compliance