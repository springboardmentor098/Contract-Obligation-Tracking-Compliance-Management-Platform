from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    contract_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="contracts"
    )

    assigned_to_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_contracts"
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
    compliance_records = relationship(
    "ComplianceRecord",
    back_populates="contract"
)