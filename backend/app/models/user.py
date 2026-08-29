from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100)
    )

    email = Column(
        String(100),
        unique=True,
        index=True
    )

    hashed_password = Column(
        String(255)
    )

    department = Column(
        String(50)
    )

    salary = Column(
        String
    )

    role = Column(
        String(50),
        nullable=False,
        default="Employee"
    )

    # Contracts owned/created by this user
    owned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.owner_id",
        back_populates="owner"
    )

    # Contracts assigned to this user
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assigned_user"
    )
        # Renewals assigned to this user
    assigned_renewals = relationship(
        "Renewal",
        foreign_keys="Renewal.assigned_to",
        back_populates="assigned_user"
    )
        # Contracts owned/created by this user
    owned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.owner_id",
        back_populates="owner"
    )

    # Contracts assigned to this user
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assigned_user"
    )

    # Renewals assigned to this user
    assigned_renewals = relationship(
        "Renewal",
        foreign_keys="Renewal.assigned_to",
        back_populates="assigned_user"
    )