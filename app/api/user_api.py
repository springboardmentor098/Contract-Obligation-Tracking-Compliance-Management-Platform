from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import User

router = APIRouter()

users = []

# CREATE
@router.post("/users")
def create_user(user: User):
    for u in users:
        if u.id == user.id:
            raise HTTPException(status_code=400, detail="User ID already exists")

    users.append(user)
    return {
        "message": "User created successfully",
        "user": user
    }

# READ ALL
@router.get("/users")
def get_users():
    return users

# READ ONE
@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# UPDATE
@router.put("/users/{user_id}")
def update_user(user_id: int, updated_user: User):
    for i, user in enumerate(users):
        if user.id == user_id:
            users[i] = updated_user
            return {
                "message": "User updated successfully",
                "user": updated_user
            }

    raise HTTPException(status_code=404, detail="User not found")

# DELETE
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user.id == user_id:
            deleted = users.pop(i)
            return {
                "message": "User deleted successfully",
                "user": deleted
            }

    raise HTTPException(status_code=404, detail="User not found")