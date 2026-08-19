# from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func

# from app.database.database import Base


# class Contract(Base):
#     __tablename__ = "contracts"

#     id = Column(
#         BigInteger,
#         primary_key=True,
#         index=True
#     )

#     owner_id = Column(
#         BigInteger,
#         ForeignKey("users.id"),
#         nullable=False
#     )

#     contract_code = Column(
#         String(100),
#         unique=True,
#         nullable=False,
#         index=True
#     )

#     title = Column(
#         String(255),
#         nullable=False
#     )

#     description = Column(
#     String(1000),
#     nullable=True
#     )
    
#     counterparty = Column(
#         String(255),
#         nullable=False
#     )

#     category = Column(
#         String(100),
#         nullable=False
#     )

#     status = Column(
#         String(50),
#         nullable=False
#     )

#     risk_level = Column(
#         String(50),
#         nullable=False
#     )

#     start_date = Column(
#         Date,
#         nullable=False
#     )

#     end_date = Column(
#         Date,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         server_default=func.now(),
#         nullable=False
#     )

#     owner = relationship(
#         "User",
#         backref="contracts"
#     )


from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    owner_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_to = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )

    contract_code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=True
    )

    counterparty = Column(
        String(255),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="Draft"
    )

    risk_level = Column(
        String(50),
        nullable=False
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
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

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        backref="owned_contracts"
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        backref="assigned_contracts"
    )
