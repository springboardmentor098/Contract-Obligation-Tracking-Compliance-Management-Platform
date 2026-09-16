from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )

    contract = relationship(
        "Contract",
        back_populates="audit_logs"
    )
