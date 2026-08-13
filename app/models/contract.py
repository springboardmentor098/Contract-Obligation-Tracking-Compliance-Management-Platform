from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    contract_number = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    description = Column(Text, nullable=True)

    party_name = Column(String(255), nullable=True)

    start_date = Column(Date, nullable=True)

    end_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    owner = relationship(
        "User",
        back_populates="contracts"
    )