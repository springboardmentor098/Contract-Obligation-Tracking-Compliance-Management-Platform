from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    renewal_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    notes = Column(
        Text,
        nullable=True
    )

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )