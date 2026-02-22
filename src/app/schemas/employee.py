from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.types import PastDate

from src.app.core.schemas import CreatedAtSchema, IDSchema


class EmployeeBase(BaseModel):
    department_id: int
    full_name: Annotated[str, Field(min_length=1, max_length=200, examples=["Ivanov Alexandr Pavlovich"])]
    position: str
    hired_at: PastDate | None


class EmployeeCreate(EmployeeBase): ...


class Employee(EmployeeBase, IDSchema, CreatedAtSchema): ...
