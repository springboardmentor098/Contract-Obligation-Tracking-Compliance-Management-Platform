from sqlalchemy import Boolean, Column, Integer, String

from app.database.database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    role = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)