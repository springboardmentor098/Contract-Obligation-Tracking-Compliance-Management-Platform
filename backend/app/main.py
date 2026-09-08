from fastapi import FastAPI

from backend.app.api import user
from backend.app.api import contracts
from backend.app.api import obligations
from backend.app.api import renewals
from backend.app.api import compliance
from backend.app.api import notifications
from backend.app.api import reports
from backend.app.api import dashboard
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Contract Obligation Tracking Compliance Management Platform"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Users
app.include_router(
    user.router,
    prefix="/users",
    tags=["Users"]
)


# Contracts
app.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Contracts"]
)


app.include_router(
    obligations.router,
    prefix="/obligations",
    tags=["Obligations"]
)

app.include_router(
    renewals.router
)
app.include_router(
    compliance.router
)
app.include_router(
    notifications.router
)
# Reports
app.include_router(
    reports.router
)
# Dashboard
app.include_router(
    dashboard.router
)
@app.get("/")
def root():
    return {"message": "API is running"}