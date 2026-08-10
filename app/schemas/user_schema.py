from pydantic import BaseModel

# 1. Schema for CREATING a user
class UserCreate(BaseModel):
    full_name: str
    email: str
    role: str
    password: str

# 2. Schema for RETURNING a user
class UserResponse(BaseModel):
    id: int
    full_name: str  #  Fixed: Changed 'name' to 'full_name'
    email: str
    role: str

    class Config:
        from_attributes = True