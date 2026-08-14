from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    generated_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=True
    )

    report_type = Column(
        String(50),
        nullable=False
    )

    report_name = Column(
        String(255),
        nullable=False
    )

    filters = Column(
        Text,
        nullable=True
    )

    file_location = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    generator = relationship(
        "User",
        backref="reports"
    )

    contract = relationship(
        "Contract",
        backref="reports"
    )