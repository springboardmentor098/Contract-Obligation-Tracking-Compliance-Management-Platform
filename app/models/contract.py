from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_by_user = relationship(
        "User",
        back_populates="contracts"
    )

    contract_versions = relationship(
        "ContractVersion",
        back_populates="contract"
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract"
    )

    renewals = relationship(
        "Renewal",
        back_populates="contract"
    )

    notifications = relationship(
        "Notification",
        back_populates="contract"
    )

    reports = relationship(
        "Report",
        back_populates="contract"
    )