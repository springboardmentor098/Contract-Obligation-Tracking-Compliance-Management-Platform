from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True
    )

    action = Column(String(100), nullable=False)

    entity_type = Column(String(100), nullable=True)

    entity_id = Column(Integer, nullable=True)

    old_value = Column(JSON, nullable=True)

    new_value = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=True)

    # Relationship with User
    user = relationship(
        "User",
        back_populates="audit_logs"
    )

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="audit_logs"
    )
    