from fastapi import FastAPI
from app.routers import users  #  Back to your working Postgres router!
from app.routers import auth
from app.database.database import test_database_connection
from app.routers import contracts 
from app.routers import obligations

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)

app.include_router(users.router) # Connected back to your real file!
app.include_router(auth.router) # Connected back to your authentication router!
app.include_router(contracts.router)
app.include_router(obligations.router)

@app.on_event("startup")
def startup_event():
    test_database_connection()

@app.get("/")
def root():
    return {"message": "ContractIQ Backend is running successfully."}