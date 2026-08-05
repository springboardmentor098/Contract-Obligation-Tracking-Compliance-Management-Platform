from fastapi import FastAPI
<<<<<<< HEAD
from app.routers.users import router as user_router
from app.database.database import test_database_connection

=======

from app.database.database import test_database_connection


>>>>>>> cb87ace116b09ed98d5d64392b80a596edfa80ce
app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

<<<<<<< HEAD
=======

>>>>>>> cb87ace116b09ed98d5d64392b80a596edfa80ce
@app.on_event("startup")
def startup_event():
    test_database_connection()

<<<<<<< HEAD
app.include_router(user_router)
=======
>>>>>>> cb87ace116b09ed98d5d64392b80a596edfa80ce

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }