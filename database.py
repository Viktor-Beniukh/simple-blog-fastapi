from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from settings import settings


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
