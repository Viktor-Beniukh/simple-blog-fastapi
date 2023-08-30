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

    comment = relationship("Comment", lazy="selectin", back_populates="post")
    owner = relationship(User, lazy="selectin", back_populates="post")


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    commentary = Column(String(length=500))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    post_id = Column(Integer, ForeignKey("post.id"))
    author_id = Column(Integer, ForeignKey("user.id"))

    post = relationship(Post, lazy="selectin", back_populates="comment")
    author = relationship(User, lazy="selectin", back_populates="comment")
