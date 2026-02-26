from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError

# NOTE: The database is the point of truth in the system, so I explicitly map errors
# to the database errors. Exceptions are tightly coupled with the database. If one
# wants to decople those errors (to use another database, which is unlikely), they shall
# implement both domain models and domain exceptions.


class InternalError(HTTPException):
    def __init__(self, **kwargs):
        self.detail = "An unexpected error occurred"
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured",
            **kwargs,
        )


class DepartmentException(HTTPException): ...


class ParentUniqueName(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_409_CONFLICT,
            detail="A department with such name already exists under this parent.",
            **kwargs,
        )


class ParentIdNotItself(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_409_CONFLICT,
            detail="A department cannot be parent of it's parents or a parent of itself",
            **kwargs,
        )


class CircularReferenceError(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_409_CONFLICT,
            detail="A department cannot be parent of it's parents or a parent of itself",
            **kwargs,
        )


class NoSuchParent(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            detail="Parent department not found.",
            **kwargs,
        )


class DepartmentNotFound(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
            **kwargs,
        )


class DepartmentForEmployeeNotFound(DepartmentException):
    def __init__(self, **kwargs):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            detail="Cannot add employee: Department does not exist.",
            **kwargs,
        )


def register_department_exception_handler(app: FastAPI):
    @app.exception_handler(DepartmentException)
    async def department_exception_handler(request: Request, exc: DepartmentException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(DBAPIError)
    async def sqlalchemy_integrity_handler(request: Request, exc: DBAPIError):
        orig_msg = str(exc.orig)

        if "department_parent_id_unique_name" in orig_msg:
            err = ParentUniqueName()
        elif "department_parent_id_not_itself" in orig_msg:
            err = ParentIdNotItself()
        elif "fk_department_parent_id" in orig_msg:
            err = NoSuchParent()
        elif "fk_employee_department_id" in orig_msg:
            err = DepartmentForEmployeeNotFound()
        elif "Circular" in orig_msg:
            err = CircularReferenceError()
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "A database integrity error occurred."},
            )

        return JSONResponse(status_code=err.status_code, content={"detail": err.detail})

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "An unexpected internal error occurred."})
