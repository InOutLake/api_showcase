from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.app.core.schemas import CreatedAtSchema, IDSchema


class EmployeeBase(BaseModel):
    full_name: Annotated[str, Field(min_length=1, max_length=200, examples=["Ivanov Alexandr Pavlovich"])]
    position: str
    hired_at: datetime | None

    class Config:
        str_strip_whitespace = True


class EmployeeCreate(EmployeeBase): ...


class Employee(EmployeeBase, IDSchema, CreatedAtSchema):
    model_config = ConfigDict(from_attributes=True)
