# ContractIQ Frontend

Angular frontend for **ContractIQ: Contract Obligation Tracking & Compliance Management Platform**.

This project consolidates the enterprise Stitch UI direction into one Angular application with:

- Angular 20 + TypeScript
- Angular Material-compatible enterprise styling
- FastAPI integration through reusable Angular services
- JWT authentication interceptor
- Protected routing
- Dashboard generated from backend data
- Contract management
- Obligation tracking
- Renewal management
- Compliance monitoring
- Notifications
- Reports & analytics
- Audit/activity history
- Loading, empty and error states
- Responsive desktop/tablet/mobile layout

## 1. Run the frontend

```powershell
cd ContractIQ-Frontend
npm install
ng serve
```

Open:

`http://localhost:4200`

## 2. FastAPI URL

Edit:

`src/environments/environment.ts`

Default:

```ts
apiUrl: 'http://localhost:8000'
```

For production, edit:

`src/environments/environment.prod.ts`

## 3. Expected API routes

The frontend is organized around these existing backend routes:

| Module | Route |
|---|---|
| Authentication | `POST /login` |
| Contracts | `/contracts` |
| Obligations | `/obligations`, `/contracts/{contract_id}/obligations` |
| Renewals | `/renewals` |
| Compliance | `/compliance` |
| Notifications | `/notifications` |
| Reports | `/reports/summary`, `/reports/dashboard` |
| Audit | `/audit` |

If your FastAPI router uses a different prefix for a module, change only that module's Angular service rather than putting HTTP calls inside components.

## 4. Authentication

The login service sends OAuth2-style form data:

- username = email
- password = password

The returned `access_token` is stored as `contractiq_token`.

Every subsequent API request automatically receives:

`Authorization: Bearer <token>`

The route guard redirects unauthenticated users to `/login`.

## 5. Important CORS setting

Your FastAPI backend must allow the Angular development origin:

`http://localhost:4200`

For FastAPI, configure `CORSMiddleware` accordingly.

## 6. Architecture

```text
Angular Component
      ↓
Angular Service
      ↓
HttpClient + JWT Interceptor
      ↓
FastAPI Router
      ↓
SQLAlchemy
      ↓
PostgreSQL
      ↓
Response
      ↓
Angular Service
      ↓
Component
      ↓
UI
```

## 7. Project structure

```text
src/app/
├── core/
│   ├── guards/
│   ├── interceptors/
│   ├── models/
│   └── services/
├── features/
│   ├── auth/
│   ├── dashboard/
│   ├── contracts/
│   ├── obligations/
│   ├── renewals/
│   ├── compliance/
│   ├── notifications/
│   ├── reports/
│   └── audit/
├── layout/
├── shared/
├── app.config.ts
├── app.routes.ts
└── app.component.ts
```

## 8. End-to-end demonstration

Use this order for Sprint 14–15:

```text
Login
  ↓
Dashboard
  ↓
Contracts
  ↓
Create / update contract
  ↓
Obligations
  ↓
Renewal pipeline
  ↓
Compliance
  ↓
Notifications
  ↓
Reports & Analytics
  ↓
Audit / Activity
  ↓
Logout
```

The dashboard does not use hardcoded business totals. It loads contracts, obligations, renewals and compliance records from the configured FastAPI APIs and derives the displayed summary.

## 9. Before GitHub submission

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Open FastAPI Swagger and verify each endpoint.
4. Confirm CORS permits `localhost:4200`.
5. Run `npm install`.
6. Run `ng serve`.
7. Login with an existing backend user.
8. Verify dashboard counts against PostgreSQL/Swagger.
9. Test create/update contract.
10. Test obligation status.
11. Test renewal status.
12. Test notifications read/unread.
13. Test reports and audit pages.
14. Test logout and protected-route redirect.
15. Commit the frontend folder to GitHub.

> Note: the backend remains the source of truth. This Angular project intentionally does not create a duplicate backend or hardcode production records.
