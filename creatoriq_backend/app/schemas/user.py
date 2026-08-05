from pydantic import BaseModel
from typing import Optional

# Used for creating a new user (All fields required)
class User(BaseModel):
    id: int
    name: str
    email: str
    role: str

# Used for updating an existing user (All fields optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None