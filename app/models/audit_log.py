from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    action = Column(String(100), nullable=False)

    entity_type = Column(String(100), nullable=False)

    entity_id = Column(Integer, nullable=True)

    old_value = Column(JSONB, nullable=True)

    new_value = Column(JSONB, nullable=True)

    ip_address = Column(String(45), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship with User
    user = relationship(
        "User",
        back_populates="audit_logs"
    )