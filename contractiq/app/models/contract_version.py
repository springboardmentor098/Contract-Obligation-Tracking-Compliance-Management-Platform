from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ContractVersion(Base):
    """
    Stores a historical snapshot of a contract each time it is significantly
    updated (title/description/dates/document file changes). Supports version
    control and audit requirements referenced in the project brief.
    """

    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)  # e.g. AWS S3 object key/URL
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_summary = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("Contract", back_populates="versions")
    editor = relationship("User")
