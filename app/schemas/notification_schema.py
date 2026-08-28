from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int
    message: str
    notification_type: str
    is_read: bool = False


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: int
    message: str
    notification_type: str
    is_read: bool

    class Config:
        from_attributes = True