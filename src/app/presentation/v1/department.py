from fastapi import APIRouter

from ...core.utils.cache import cache
from ...repositories.department import DepartmentRepositoryDep
from ...schemas.department import (
    Department,
    DepartmentCreate,
    DepartmentDeleteQuery,
    DepartmentDeleteQueryCascade,
    DepartmentDeleteQueryReassign,
    DepartmentGetQuery,
    DepartmentNested,
    DepartmentUpdate,
)
from ...schemas.employee import Employee, EmployeeCreate

router = APIRouter(prefix="departments", tags=["department"])


# NOTE: http errors are specified in the repository. It is a tradeoff in terms of layer separaion but
# makes code more appealing. Usually I'd map internal errors to http errors with mapper,
# but in this case it will only bloat the code.
# Technically current implementation handles errors on the border of layers,
# so there are no significant difference whether I catch them here or in repo.


@router.post("/", response_model=Department)
@cache(key_prefix="department_{id}")
async def create_department(data: DepartmentCreate, rep: DepartmentRepositoryDep):
    department = await rep.create_department(**data.model_dump())
    return department


@router.post("/{id}/employees", response_model=Employee)
@cache(key_prefix="department_{department_id}")
async def create_employee(data: EmployeeCreate, rep: DepartmentRepositoryDep):
    employee = await rep.add_employee(**data.model_dump())
    return employee


@router.get("/{id}", response_model=DepartmentNested)
@cache(key_prefix="department_{id}:nested:{depth}:{include_employees}")
async def get_department_details(data: DepartmentGetQuery, rep: DepartmentRepositoryDep):
    department = await rep.get_department_nested(**data.model_dump())
    return department


@router.patch("/{id}", response_model=Department)
@cache(key_prefix="department_{id}")
async def patch_department(data: DepartmentUpdate, rep: DepartmentRepositoryDep):
    department = await rep.update_department(**data.model_dump())
    return department


@router.delete("/{id}", status_code=204)
@cache(key_prefix="department_{id}")
async def delete_department(data: DepartmentDeleteQuery, rep: DepartmentRepositoryDep):
    if isinstance(data, DepartmentDeleteQueryCascade):
        await rep.delete_department_cascade(data.id)
    if isinstance(data, DepartmentDeleteQueryReassign):
        await rep.delete_department_reassign(data.id, data.target_id)
    return
