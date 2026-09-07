from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.api.contracts import router as contracts_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(contracts_router)


@app.get("/")
def root():
    return {"message": "ContractIQ API is running"}
