from fastapi import APIRouter

from ...schemas.department import (
    Department,
    DepartmentCreate,
    DepartmentDeleteQuery,
    DepartmentGetQuery,
    DepartmentNested,
    DepartmentUpdate,
)
from ...schemas.employee import Employee, EmployeeCreate

router = APIRouter(prefix="departments", tags=["department"])


@router.post("/", response_model=Department)
def create_department(data: DepartmentCreate):
    department = ...
    return department


@router.post("/{id}/employees", response_model=Employee)
def create_employee(data: EmployeeCreate):
    employee = ...
    return employee


@router.get("/{id}", response_model=DepartmentNested)
def get_department_details(data: DepartmentGetQuery):
    department = ...
    return department


@router.patch("/{id}", response_model=Department)
def patch_department(data: DepartmentUpdate):
    department = ...
    return department


@router.delete("/{id}", status_code=204)
def delete_department(data: DepartmentDeleteQuery):
    department = ...
    return department
