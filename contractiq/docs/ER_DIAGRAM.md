# ContractIQ ER Diagram

```mermaid
erDiagram
 USERS ||--o{ CONTRACTS : creates
 USERS ||--o{ CONTRACTS : assigned_to
 CONTRACTS ||--o{ CONTRACT_VERSIONS : versions
 CONTRACTS ||--o{ OBLIGATIONS : has
 USERS ||--o{ OBLIGATIONS : assigned_to
 CONTRACTS ||--o{ RENEWALS : has
 USERS ||--o{ RENEWALS : assigned_to
 USERS ||--o{ NOTIFICATIONS : receives
 CONTRACTS ||--o{ NOTIFICATIONS : relates
 OBLIGATIONS ||--o{ NOTIFICATIONS : relates
 CONTRACTS ||--o{ COMPLIANCE_RECORDS : evaluated
 USERS ||--o{ REPORTS : generates
 USERS ||--o{ AUDIT_LOGS : performs
 USERS ||--o{ ACTIVITIES : performs
```

The core relationship is `users -> contracts -> obligations/renewals`, with notifications, compliance history, reports, audit logs and activities supporting the operational modules.
