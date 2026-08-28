from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String(500)
    )

    obligation_type = Column(
        String(100),
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL")
    )

    status = Column(
        String(50),
        default="Pending",
        nullable=False
    )

    completion_date = Column(Date)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    contract = relationship(
        "Contract",
        back_populates="obligations"
    )

    user = relationship(
        "User",
        back_populates="obligations"
    )