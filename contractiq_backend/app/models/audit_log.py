from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    entity_name = Column(
        String(100),
        nullable=False
    )

    entity_id = Column(
        BigInteger,
        nullable=False
    )

    before_data = Column(
        Text,
        nullable=True
    )

    after_data = Column(
        Text,
        nullable=True
    )

    ip_address = Column(
        String(45),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        backref="audit_logs"
    )

    contract = relationship(
        "Contract",
        backref="audit_logs"
    )