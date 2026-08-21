from sqlalchemy import Boolean, Column, Integer, String

from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # Contracts created by this user
    contracts = relationship(
        "Contract",
        foreign_keys="Contract.created_by",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Contracts assigned to this user
    assigned_contracts = relationship(
        "Contract",
        foreign_keys="Contract.assigned_to",
        back_populates="assigned_user"
    )

    # Obligations assigned to this user
    assigned_obligations = relationship(
        "Obligation",
        foreign_keys="Obligation.assigned_to",
        back_populates="assigned_user"
    )