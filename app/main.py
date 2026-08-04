from fastapi import FastAPI

from app.database.database import test_database_connection
from app.api.user_api import router as user_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    test_database_connection()

# Register User Router
app.include_router(user_router)

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }