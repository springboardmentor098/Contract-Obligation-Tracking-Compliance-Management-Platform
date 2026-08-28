from sqlalchemy import Column, Integer, Date, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False
    )

    renewal_date = Column(Date, nullable=False)

    previous_expiry_date = Column(Date, nullable=False)

    new_expiry_date = Column(Date, nullable=False)

    status = Column(
        String(50),
        default="Upcoming",
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL")
    )

    notes = Column(String(500))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )

    user = relationship(
        "User",
        back_populates="renewals"
    )