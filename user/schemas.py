from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    registered_at: str
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    access_token: str
    token_type: str


class UserSingle(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
