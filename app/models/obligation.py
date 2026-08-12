from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    due_date = Column(Date, nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    priority = Column(
        String(50),
        nullable=False,
        default="medium"
    )

    responsible_party = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )