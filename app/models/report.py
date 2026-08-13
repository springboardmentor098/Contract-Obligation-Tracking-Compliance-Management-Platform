from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    report_type = Column(String(100), nullable=False)

    report_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, nullable=True)

    # Relationship with Contract
    contract = relationship(
        "Contract",
        back_populates="reports"
    )

    # Relationship with User
    generator = relationship(
        "User",
        back_populates="reports"
    )