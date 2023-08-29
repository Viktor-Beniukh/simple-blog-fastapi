from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=255), nullable=False, unique=True, index=True)
    username = Column(String(length=255), nullable=False, unique=True)
    first_name = Column(String(length=255))
    last_name = Column(String(length=255))
    password = Column(String(length=1024), nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
