# from fastapi import FastAPI

# from app.database.database import test_database_connection
# # from app.api.user_api import router
# from app.routers.users import router

# app = FastAPI(
#     title="ContractIQ API",
#     version="1.0.0"
# )

# @app.on_event("startup")
# def startup_event():
#     test_database_connection()

# @app.get("/")
# def root():
#     return {
#         "message": "ContractIQ Backend is running successfully."
#     }

# app.include_router(router)
# from fastapi import FastAPI

# from app.database.database import test_database_connection

# from app.routers.users import router

# app.include_router(router)

# app = FastAPI(
#     title="ContractIQ API",
#     version="1.0.0"
# )


# @app.on_event("startup")
# def startup_event():
#     test_database_connection()


# @app.get("/")
# def root():
#     return {
#         "message": "ContractIQ Backend is running successfully."
#     }

from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router
from app.routers.auth import router as auth_router
from app.routers.contracts import router as contracts_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    test_database_connection()

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }

app.include_router(router)
app.include_router(auth_router)
app.include_router(contracts_router)