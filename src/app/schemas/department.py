from __future__ import annotations

from enum import Enum, StrEnum, auto
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.app.schemas.shared import NOT_ASSIGNED

from ..core.schemas import CreatedAtSchema, IDSchema
from .employee import Employee

DEPARTMENT_NAME_TYPE = Annotated[str, Field(min_length=1, max_length=200, examples=["Development"])]


class DepartmentBase(BaseModel):
    name: DEPARTMENT_NAME_TYPE
    parent_id: int | None

    model_config = ConfigDict(str_strip_whitespace=True)


class Department(DepartmentBase, CreatedAtSchema, IDSchema):
    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(DepartmentBase): ...


class DepartmentGetQuery(BaseModel):
    depth: Annotated[int, Field(default=1, ge=1, le=5)]
    include_employees: bool = True


class DepartmentNested(BaseModel):
    department: Department
    children: list[DepartmentNested] = Field(default_factory=list)
    employees: list[Employee] | None = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentUpdate(IDSchema):
    name: DEPARTMENT_NAME_TYPE | NOT_ASSIGNED = NOT_ASSIGNED.NOT_ASSIGNED
    parent_id: int | None | NOT_ASSIGNED = NOT_ASSIGNED.NOT_ASSIGNED

    model_config = ConfigDict(str_strip_whitespace=True)


class DeleteModeEnum(StrEnum):
    CASCADE = auto()
    REASSIGN = auto()


class DepartmentDeleteQuery(BaseModel):
    mode: DeleteModeEnum
    target_id: int | None = None

    @model_validator(mode="after")
    def check_reassign_params(self) -> DepartmentDeleteQuery:
        if self.mode == "reassign" and self.target_id is None:
            raise ValueError("target_id is required when mode is 'reassign'")
        return self
