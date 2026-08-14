# from sqlalchemy import Boolean, Column, Integer, String

# from app.database.database import Base


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String(100), nullable=False)
#     email = Column(String(255), unique=True, nullable=False, index=True)
#     role = Column(String(50), nullable=False)
#     password = Column(String(255), nullable=False)
#     is_active = Column(Boolean, default=True, nullable=False)

from sqlalchemy import Boolean, Column, BigInteger, String, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)

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

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(40),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
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