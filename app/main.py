from fastapi import FastAPI
from app.routers import users  
from app.routers import auth
from app.database.database import test_database_connection
from app.routers import contracts 
from app.routers import obligations
from app.routers import renewals
from app.routers import compliance
from app.routers import notifications
from app.routers import reports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)



app = FastAPI(title="ContractIQ API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router) # Connected back to your real file!
app.include_router(auth.router) # Connected back to your authentication router!
app.include_router(contracts.router)
app.include_router(obligations.router)
app.include_router(renewals.router)
app.include_router(compliance.router)
app.include_router(notifications.router)
app.include_router(reports.router)


@app.on_event("startup")
def startup_event():
    test_database_connection()

@app.get("/")
def root():
    return {"message": "ContractIQ Backend is running successfully."}