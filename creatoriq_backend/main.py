from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.users import router as user_router
from app.routers.contracts import router as contract_router
from app.routers.obligations import router as obligation_router
from app.routers.renewals import router as renewal_router
from app.routers.compliance import (
    router as compliance_router,
    contract_compliance_router,
)
from app.routers.notifications import router as notification_router
from app.routers.reports import router as reports_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)

app.include_router(contract_router)

app.include_router(obligation_router)

app.include_router(renewal_router)

app.include_router(compliance_router)

app.include_router(contract_compliance_router)

app.include_router(notification_router)

app.include_router(reports_router)