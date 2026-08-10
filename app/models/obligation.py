from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    due_date = Column(Date, nullable=False)

    status = Column(String(50), nullable=False)

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )