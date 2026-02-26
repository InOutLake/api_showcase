from fastapi import APIRouter

from .department.api import router as department_router
from .department.exceptions import register_department_exception_handler
from .health import router as health_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(department_router)

__all__ = ["router", "register_department_exception_handler"]
