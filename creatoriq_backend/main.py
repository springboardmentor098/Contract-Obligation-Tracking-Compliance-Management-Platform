from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.contracts import router as contract_router

app = FastAPI()

app.include_router(user_router)
app.include_router(contract_router)