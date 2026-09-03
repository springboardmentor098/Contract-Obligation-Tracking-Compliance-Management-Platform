# ContractIQ Angular Dashboard

Angular dashboard for Sprint 13. It consumes the FastAPI backend at `http://localhost:8000`.

## Run

```bash
npm install
npm start
```

After login through the backend, save the returned access token as `contractiq_token` in browser local storage. The dashboard then calls `/dashboard/summary` with that bearer token.
