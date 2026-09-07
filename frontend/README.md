# ContractIQ — Frontend

Angular 18 (standalone components) client for the ContractIQ contract
obligation tracking & compliance platform, built against the FastAPI backend
in the parent directory.

## Modules implemented

- Authentication (login / register) with JWT stored client-side, role-aware navigation
- Dashboard — contract, obligation, renewal, and compliance summary
- Contract repository — search/filter, create/edit, lifecycle actions (submit for
  review, approve, activate)
- Obligation tracking — register, filter, mark complete
- Renewal management — track renewal records, mark renewed
- Compliance monitoring — score/status per contract, high-risk list
- Notifications — read/unread, mark all read
- Reports — per-module summaries with Excel/PDF export
- User management (Administrator only) — role changes, deactivation

## Run locally

```bash
npm install
npm start        # ng serve, http://localhost:4200
```

The API base URL is set in `src/app/core/api-base.ts` (defaults to
`http://localhost:8000`, matching the FastAPI backend's default `uvicorn`
port). Update it if your backend runs elsewhere.

## Build

```bash
npm run build     # outputs to dist/contractiq-dashboard
```
