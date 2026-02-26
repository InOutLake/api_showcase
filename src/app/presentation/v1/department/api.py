from typing import Annotated

from fastapi import APIRouter, Query

from ....repositories.department import DepartmentRepositoryDep
from ....schemas.department import (
    DeleteModeEnum,
    Department,
    DepartmentCreate,
    DepartmentDeleteQuery,
    DepartmentGetQuery,
    DepartmentNested,
    DepartmentUpdate,
)
from ....schemas.employee import Employee, EmployeeCreate

router = APIRouter(prefix="/departments", tags=["department"])


# NOTE: errors are specified explicitly in the excpeptions file.


@router.post("", response_model=Department)
async def create_department(data: DepartmentCreate, rep: DepartmentRepositoryDep):
    department = await rep.create_department(**data.model_dump())
    return department


@router.post("/{department_id}/employees", response_model=Employee)
async def create_employee(department_id: int, data: EmployeeCreate, rep: DepartmentRepositoryDep):
    employee_data = data.model_dump()
    employee_data["department_id"] = department_id
    employee = await rep.add_employee(**employee_data)
    return employee


@router.get("/{id}", response_model=DepartmentNested)
async def get_department_details(id: int, data: Annotated[DepartmentGetQuery, Query()], rep: DepartmentRepositoryDep):
    get_data = data.model_dump()
    get_data["id"] = id
    department = await rep.get_department_nested(**get_data)
    return department


@router.patch("/{id}", response_model=Department)
async def patch_department(data: DepartmentUpdate, rep: DepartmentRepositoryDep):
    department = await rep.update_department(**data.model_dump())
    return department


@router.delete("/{id}", status_code=204)
async def delete_department(id: int, data: Annotated[DepartmentDeleteQuery, Query()], rep: DepartmentRepositoryDep):
    delete_data = data.model_dump()
    delete_data["id"] = id
    if data.mode == DeleteModeEnum.CASCADE:
        await rep.delete_department_cascade(delete_data["id"])
    if data.mode == DeleteModeEnum.REASSIGN:
        await rep.delete_department_reassign(delete_data["id"], delete_data["target_id"])  # type: ignore
    return
