from fastapi import FastAPI
from app.routers import auth, contracts, users
from app.database.database import test_database_connection


app = FastAPI(
    title="ContractIQ API - Role-Based Access Control (RBAC)",
    description="ContractIQ Compliance & Contract Management Platform with RBAC authorization",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contracts.router)



@app.on_event("startup")
def startup_event():
    try:
        test_database_connection()
    except Exception as e:
        print("Database startup test exception (handled):", e)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend API with Role-Based Access Control (RBAC) is running successfully.",
        "docs": "/docs",
        "roles": [
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        ]
    }