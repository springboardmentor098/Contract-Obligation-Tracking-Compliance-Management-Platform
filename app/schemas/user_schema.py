from pydantic import BaseModel


class UserCreate(BaseModel):
    full_name: str
    email: str
    role: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str

    class Config:
        from_attributes = True