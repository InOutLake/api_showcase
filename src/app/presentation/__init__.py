from fastapi import APIRouter, FastAPI

from .v1 import register_department_exception_handler
from .v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)


def register_exceptions(app: FastAPI):
    register_department_exception_handler(app)
