from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    message = Column(String(500))
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications", passive_deletes=True)
    contract = relationship("Contract", back_populates="notifications")