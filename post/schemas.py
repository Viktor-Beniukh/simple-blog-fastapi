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
    owner_id: int
    owner: User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PostSingle(PostBase):
    id: int
    owner_id: int
    owner: UserSingle
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    post_id: int
    commentary: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    commentary: str

    class Config:
        orm_mode = True


class Comment(CommentBase):
    id: int
    author_id: int
    author: UserSingle
    created_at: datetime
    updated_at: datetime
    post: PostSingle

    class Config:
        orm_mode = True
