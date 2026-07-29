from fastapi import FastAPI
from app.api.user_api import router as user_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

app.include_router(user_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to ContractIQ API 🚀"
    }