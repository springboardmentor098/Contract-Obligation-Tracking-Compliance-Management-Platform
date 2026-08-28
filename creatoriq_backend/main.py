from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.contracts import router as contract_router
from app.routers.obligations import router as obligation_router
from app.routers.renewals import router as renewal_router


app = FastAPI()

app.include_router(user_router)
app.include_router(contract_router)
app.include_router(obligation_router)
app.include_router(renewal_router)