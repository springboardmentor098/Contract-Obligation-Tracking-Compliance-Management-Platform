from sqlalchemy import Column, Date, ForeignKey, Integer, String
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

    renewal_date = Column(Date, nullable=False)

    renewal_status = Column(String(50), nullable=False)

    contract = relationship(
        "Contract",
        back_populates="renewals"
    )