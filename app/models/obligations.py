from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from app.database.database import Base

class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    