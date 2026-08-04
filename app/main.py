from fastapi import FastAPI
from app.routers import users
from app.database.database import test_database_connection

app = FastAPI(
    title="ContractIQ API",

    version="1.0.0",
)

app.include_router(users.router)

@app.on_event("startup")

def startup_event():

    test_database_connection()

@app.get("/")

def root():

    return {

        "message": "ContractIQ Backend is running successfully."

    }

