# Backend Integration Checklist

Use this before your demo.

## FastAPI
- [ ] Backend runs on `http://localhost:8000`
- [ ] `/docs` opens
- [ ] `/login` works in Swagger
- [ ] JWT access token is returned
- [ ] CORS allows `http://localhost:4200`

## Routes used by the Angular frontend
- [ ] `GET /contracts`
- [ ] `POST /contracts`
- [ ] `PUT /contracts/{id}`
- [ ] `DELETE /contracts/{id}`
- [ ] `PATCH /contracts/{id}/status`
- [ ] `GET /obligations`
- [ ] `GET /obligations/contract/{contract_id}`
- [ ] `POST /contracts/{contract_id}/obligations`
- [ ] `PUT /obligations/{id}`
- [ ] `PATCH /obligations/{id}/status`
- [ ] `GET /renewals`
- [ ] `POST /renewals`
- [ ] `PUT /renewals/{id}`
- [ ] `PATCH /renewals/{id}/status`
- [ ] `GET /compliance`
- [ ] `GET /notifications`
- [ ] `GET /notifications/{id}`
- [ ] `PATCH /notifications/{id}/read`
- [ ] `PATCH /notifications/{id}/unread`
- [ ] `GET /reports/summary` or adjust `report.service.ts`
- [ ] `GET /reports/dashboard` or adjust `report.service.ts`
- [ ] `GET /audit` or adjust `audit.service.ts`

If your backend uses different paths, update only the relevant service under:

`src/app/core/services/`
