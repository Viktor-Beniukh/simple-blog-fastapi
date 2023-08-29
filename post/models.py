from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from user.models import User


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=255), nullable=False)
    content = Column(String(length=500), default="")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("user.id"))

    owner = relationship(User)
