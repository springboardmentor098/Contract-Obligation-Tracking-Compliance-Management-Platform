# from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func

# from app.database.database import Base


# class Renewal(Base):
#     __tablename__ = "renewals"

#     id = Column(
#         BigInteger,
#         primary_key=True,
#         index=True
#     )

#     contract_id = Column(
#         BigInteger,
#         ForeignKey("contracts.id"),
#         nullable=False
#     )

#     managed_by = Column(
#         BigInteger,
#         ForeignKey("users.id"),
#         nullable=False
#     )

#     renewal_date = Column(
#         Date,
#         nullable=False
#     )

#     notice_days = Column(
#         Integer,
#         nullable=False
#     )

#     decision = Column(
#         String(30),
#         nullable=False
#     )

#     new_end_date = Column(
#         Date,
#         nullable=True
#     )

#     remarks = Column(
#         Text,
#         nullable=True
#     )

#     created_at = Column(
#         DateTime,
#         server_default=func.now(),
#         nullable=False
#     )

#     contract = relationship(
#         "Contract",
#         backref="renewals"
#     )

#     manager = relationship(
#         "User",
#         backref="managed_renewals"
#     )

from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    contract_id = Column(
        BigInteger,
        ForeignKey("contracts.id"),
        nullable=False
    )

    assigned_to = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    renewal_date = Column(
        Date,
        nullable=False
    )

    notice_days = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="Upcoming"
    )

    new_expiry_date = Column(
        Date,
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    previous_expiry_date = Column(
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

    contract = relationship(
        "Contract",
        backref="renewals"
    )

    assignee = relationship(
        "User",
        backref="assigned_renewals"
    )

    