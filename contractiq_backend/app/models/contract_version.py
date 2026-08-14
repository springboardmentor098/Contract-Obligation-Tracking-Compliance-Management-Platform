from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

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

    version_no = Column(
        Integer,
        nullable=False
    )

    document_name = Column(
        String(255),
        nullable=False
    )

    document_uri = Column(
        Text,
        nullable=False
    )

    checksum = Column(
        String(128),
        nullable=False
    )

    change_note = Column(
        Text,
        nullable=True
    )

    uploaded_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    contract = relationship(
        "Contract",
        backref="versions"
    )

    uploader = relationship(
        "User",
        backref="uploaded_versions"
    )