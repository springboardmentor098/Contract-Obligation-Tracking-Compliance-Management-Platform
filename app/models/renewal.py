from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    renewal_date = Column(
        Date,
        nullable=True
    )

    previous_expiry_date = Column(
        Date,
        nullable=False
    )

    new_expiry_date = Column(
        Date,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="Upcoming"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Contract relationship
    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    # Assigned user relationship
    assigned_user = relationship(
        "User",
        back_populates="renewals"
    )