from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter()

# Temporary Storage
users = []
current_id = 1 

# -------------------------
# CREATE USER
# -------------------------
@router.post("/users")
def create_user(user: UserCreate):
    global current_id
    try:
        # 1. Hash the incoming password
        hashed_pw = get_password_hash(user.password)

        # 2. Build the user dictionary
        new_user = {
            "id": current_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "hashed_password": hashed_pw
        }

        # 3. Save to temporary list and update ID
        users.append(new_user)
        current_id += 1

        return {
            "message": "User created successfully",
            "user": new_user
        }
    except Exception as e:
        # If bcrypt or hashing fails, this will tell us exactly why in Swagger!
        raise HTTPException(status_code=500, detail=f"Hashing error: {str(e)}")

# -------------------------
# GET ALL USERS
# -------------------------
@router.get("/users")
def get_users():
    return users

# -------------------------
# GET USER BY ID
# -------------------------
@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:  # 👈 Fixed: changed user.id to user["id"]
            return user

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

# -------------------------
# UPDATE USER
# -------------------------
@router.put("/users/{user_id}")
def update_user(user_id: int, updated_user: UserCreate): 
    for index, user in enumerate(users):
        if user["id"] == user_id:  # 👈 Fixed: changed user.id to user["id"]
            users[index] = {
                "id": user_id,
                "full_name": updated_user.full_name,
                "email": updated_user.email,
                "role": updated_user.role,
                "hashed_password": user["hashed_password"] 
            }
            return {
                "message": "User updated successfully",
                "user": users[index]
            }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

# -------------------------
# DELETE USER
# -------------------------
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user["id"] == user_id:  # 👈 Fixed: changed user.id to user["id"]
            deleted_user = users.pop(index)
            return {
                "message": "User deleted successfully",
                "user": deleted_user
            }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )