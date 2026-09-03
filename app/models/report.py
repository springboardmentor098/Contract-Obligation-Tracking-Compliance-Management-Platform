import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReportType(str, enum.Enum):
    CONTRACT_REPORT = "Contract Report"
    COMPLIANCE_REPORT = "Compliance Report"
    RENEWAL_REPORT = "Renewal Report"
    OBLIGATION_REPORT = "Obligation Report"
    AUDIT_REPORT = "Audit Report"


class ReportFormat(str, enum.Enum):
    PDF = "PDF"
    EXCEL = "Excel"


class Report(Base):
    """Metadata for a generated report file (Reports & Export module)."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum(ReportType), nullable=False)
    report_format = Column(Enum(ReportFormat), nullable=False, default=ReportFormat.PDF)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(500), nullable=True)
    parameters = Column(Text, nullable=True)  # JSON-encoded filter parameters used to build the report

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    generator = relationship("User")
