


# app/api/user_api.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

users = []

from app.schemas.user import User
@router.get("/")
def get_users():
    return users

@router.get("/{id}")
def get_user(id: int):
    for user in users:
        if user.id == id:
            return user
    return {"error": f"User {id} not found"}

@router.post("/")
def create_user(user: User):
    for existing_user in users:
        if existing_user.id == user.id:
            return {"error": f"User with ID {user.id} already exists"}
    users.append(user)
    return {"message": "User created successfully", "user": user}

@router.put("/{id}")
def update_user(id: int, updated_user: User):
    for index, user in enumerate(users):
        if user.id == id:
            users[index] = updated_user
            return {"message": f"User {id} updated successfully", "user": updated_user}
    return {"error": f"User {id} not found"}

@router.delete("/{id}")
def delete_user(id: int):
    for index, user in enumerate(users):
        if user.id == id:
            deleted_user = users.pop(index)
            return {"message": f"User {id} deleted successfully", "user": deleted_user}
    return {"error": f"User {id} not found"}