from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.api.contracts import router as contracts_router
from app.api.reports import router as reports_router
from app.api.renewals import router as renewals_router
from app.api.obligations import router as obligations_router
from app.api.notifications import router as notifications_router
from app.api.audit_history import router as audit_history_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(contracts_router)
app.include_router(reports_router)
app.include_router(renewals_router)
app.include_router(obligations_router)
app.include_router(notifications_router)
app.include_router(audit_history_router)


@app.get("/")
def root():
    return {"message": "ContractIQ API is running"}
