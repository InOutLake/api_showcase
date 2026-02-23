import inspect
import logging
from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# NOTE: usually it is benefitial to separate repositories layer and presentation level errors.
# Since this is a rather simple example I set up simple mapper here.


class InternalError(HTTPException):
    def __init__(self, **kwargs):
        self.status_code = (status.HTTP_500_INTERNAL_SERVER_ERROR,)
        self.detail = "An unexpected error occurred"
        super().__init__(**kwargs)


class DepartmentException(HTTPException): ...


class ParentUniqueName(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = (status.HTTP_400_CONFLICT,)
        self.detail = "A department with such name already exists under this parent."
        super().__init__(**kwargs)


class ParentIdNotItself(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = (status.HTTP_400_CONFLICT,)
        self.detail = "A department cannot be parent of it's parents or a parent of itself"
        super().__init__(**kwargs)


class CircularReferenceError(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = (status.HTTP_400_CONFLICT,)
        self.detail = "A department cannot be parent of it's parents or a parent of itself"
        super().__init__(**kwargs)


class NoSuchParent(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Parent department not found."
        super().__init__(**kwargs)


class DepartmentNotFound(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Department not found."
        super().__init__(**kwargs)


class DepartmentForEmployeeNotFound(DepartmentException):
    def __init__(self, **kwargs):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Cannot add employee: Department does not exist."
        super().__init__(**kwargs)


def map_errors(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except IntegrityError as e:
            diag = getattr(e.orig, "diag", None)
            if not diag:
                raise e

            constraint = diag.constraint_name

            sig = inspect.signature(func)
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()

            match constraint:
                case "depratment_parent_id_unique_name":
                    raise ParentUniqueName()

                case "department_parent_id_not_itself":
                    raise ParentIdNotItself()

                case "fk_department_parent_id":
                    raise NoSuchParent()

                case "fk_employee_department_id":
                    raise DepartmentForEmployeeNotFound()

            if diag.sqlstate == "P0001":
                if "Circular referene" in diag.message_primary:
                    raise CircularReferenceError()

            raise e

        except Exception as e:
            logging.error(f"Error occured in function {func.__name__}: {e}")
            raise InternalError()

    return wrapper
