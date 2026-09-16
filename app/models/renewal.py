from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    renewal_date = Column(Date, nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="upcoming"
    )

    renewal_terms = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )