from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.types import DateTime

from ..config import settings


class CreatedAtMixin:
    created_at: Mapped[DateTime] = mapped_column(default=datetime.now())


ID_TYPE = Mapped[int]
ID: Mapped[int] = mapped_column(primary_key=True)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Department(Base, CreatedAtMixin):
    __tablename__ = "department"
    id = ID_TYPE
    name: Mapped[str] = mapped_column()
    parent_id: ID_TYPE = mapped_column(nullable=True)


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db
