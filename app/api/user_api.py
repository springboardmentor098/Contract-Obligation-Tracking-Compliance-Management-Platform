from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

# Temporary in-memory storage
users: list[UserResponse] = []

# -------------------------
# CREATE USER
# -------------------------
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    # ✅ Check duplicate email instead of ID
    for existing_user in users:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserResponse(
        id=len(users) + 1,  
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=True
    )
    users.append(new_user)
    return new_user

# -------------------------
# GET ALL USERS
# -------------------------
@router.get("/", response_model=list[UserResponse])
def get_users():
    return users

# -------------------------
# GET USER BY ID
# -------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# -------------------------
# UPDATE USER
# -------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserCreate):
    for index, user in enumerate(users):
        if user.id == user_id:
            users[index] = UserResponse(
                id=user_id,
                full_name=updated_user.full_name,
                email=updated_user.email,
                role=updated_user.role,
                is_active=updated_user.is_active
            )
            return users[index]
    raise HTTPException(status_code=404, detail="User not found")

# -------------------------
# DELETE USER
# -------------------------
@router.delete("/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user.id == user_id:
            deleted_user = users.pop(index)
            return {"message": "User deleted successfully", "user": deleted_user}
    raise HTTPException(status_code=404, detail="User not found")
