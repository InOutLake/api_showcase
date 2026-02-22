from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ..core.schemas import CreatedAtSchema, IDSchema
from .employee import Employee

DEPARTMENT_NAME_TYPE = Annotated[str, Field(min_length=1, max_length=200, examples=["Development"])]


class DepartmentBase(BaseModel):
    name: DEPARTMENT_NAME_TYPE
    parent_id: int | None

    model_config = {"str_strip_whitespace": True}


class Department(DepartmentBase, CreatedAtSchema, IDSchema): ...


class DepartmentCreate(DepartmentBase): ...


class DepartmentGetQuery(IDSchema):
    depth: Annotated[int, Field(default=1, ge=1, le=5)]
    include_employees: bool = True


class DepartmentNested(BaseModel):
    department: Department
    children: list[DepartmentNested]
    employees: list[Employee] | None = None


class DepartmentUpdate(BaseModel):
    name: DEPARTMENT_NAME_TYPE | None
    parent_id: int | None


class DepartmentDeleteQueryCascade(IDSchema):
    mode: Literal["cascade"]


class DepartmentDeleteQueryReassign(IDSchema):
    mode: Literal["reassign"]
    reassign_to_department_id: int


DepartmentDeleteQuery = DepartmentDeleteQueryCascade | DepartmentDeleteQueryReassign
