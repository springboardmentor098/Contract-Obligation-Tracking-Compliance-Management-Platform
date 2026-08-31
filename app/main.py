from fastapi import FastAPI

from app.api import users
from app.database.database import Base, engine, test_database_connection
import app.models  # noqa: F401 (registers models with Base before create_all)

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()
    Base.metadata.create_all(bind=engine)


app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }
