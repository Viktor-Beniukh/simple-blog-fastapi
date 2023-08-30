from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import (
    ACCESS_TOKEN_EXPIRES_IN,
    REFRESH_TOKEN_EXPIRES_IN,
    SECRET_KEY,
    ALGORITHM,
)
from dependencies import get_async_session
from user import schemas, models
from user.security import get_password_hash


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token/")


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


def create_tokens(data: dict) -> tuple[str, str]:
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    refresh_expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    access_token = jwt.encode(
        {"user_id": data["user_id"], "sub": data["sub"], "exp": access_expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        {"user_id": data["user_id"], "sub": data["sub"], "exp": refresh_expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return access_token, refresh_token


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)
) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user = await get_user_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token"
        )


async def get_user_by_email(db: AsyncSession, email: EmailStr) -> models.User:
    query = select(models.User).where(models.User.email == email)
    user_email = await db.execute(query)
    return user_email.scalar_one_or_none()
