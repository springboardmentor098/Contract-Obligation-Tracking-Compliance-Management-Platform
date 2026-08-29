from fastapi import FastAPI

from backend.app.api import user
from backend.app.api import contracts
from backend.app.api import obligations
from backend.app.api import renewals
from backend.app.api import compliance


app = FastAPI(
    title="Contract Obligation Tracking Compliance Management Platform"
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

@app.get("/")
def root():
    return {"message": "API is running"}