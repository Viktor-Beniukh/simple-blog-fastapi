from datetime import datetime

from pydantic import BaseModel

from user.schemas import UserSingle, User


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    author_id: int
    author: UserSingle
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PostSingle(PostBase):
    id: int
    author_id: int
    author: User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
