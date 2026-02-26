from .core import logger
from .core.config import settings
from .core.setup import create_application
from .presentation import register_exceptions, router

app = create_application(router=router, settings=settings)
register_exceptions(app)
