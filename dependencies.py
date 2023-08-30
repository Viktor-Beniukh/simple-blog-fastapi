from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db


db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
