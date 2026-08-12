from fastapi import FastAPI
from app.database.database import test_database_connection
from app.api import user_api

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    test_database_connection()

# include routers
app.include_router(user_api.router)   

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }
from app.api import auth

app.include_router(auth.router)
