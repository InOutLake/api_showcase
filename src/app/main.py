from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import settings
from .core.setup import create_application, lifespan_factory
from .presentation import router


@asynccontextmanager
async def lifespan_with_admin(app: FastAPI) -> AsyncGenerator[None, None]:
    """Custom lifespan that includes admin initialization."""
    default_lifespan = lifespan_factory(settings)

    async with default_lifespan(app):
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan_with_admin)
