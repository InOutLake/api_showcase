from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, insert, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.db.database import async_get_db
from ..models.department import Department
from ..models.employee import Employee
from ..schemas.shared import NOT_ASSIGNED, NotAssigned
from .exceptions import map_errors


# NOTE: usually I separate domain, service and repository levels, but since there are little to none
# logic behind departments I decided to set it all more coupled. You can see more sophisticated solution in my other
# repositories.
class DepartmentRepository:
    def __init__(self, async_db_session: AsyncSession):
        self.db = async_db_session

    @map_errors
    async def create_department(self, name: str, parent_id: int | None, **kwargs) -> Department:
        stmt = insert(Department).values(name=name, parent_id=parent_id, **kwargs).returning(Department)
        result = (await self.db.execute(stmt)).scalars().one()
        return result

    @map_errors
    async def add_employee(
        self, department_id: int, full_name: str, position: str, hired_at: datetime | None, **kwargs
    ) -> Employee:
        stmt = (
            insert(Employee)
            .values(
                department_id=department_id,
                full_name=full_name,
                position=position,
                hired_at=hired_at,
                **kwargs,
            )
            .returning(Employee)
        )
        result = (await self.db.execute(stmt)).scalars().one()
        return result

    @map_errors
    async def get_department(self, department_id: int) -> Department:
        stmt = select(Department).where(Department.id == department_id)
        return (await self.db.execute(stmt)).scalars().one()

    # NOTE: updates are always wacky, especially when youre not using DTOs
    @map_errors
    async def update_department(
        self,
        department_id: int,
        name: str | NotAssigned,
        parent_id: int | None | NotAssigned,
    ):
        updates = {
            "name": name,
            "parent_id": parent_id,
        }

        to_update = {k: v for k, v in updates.items() if v is not NOT_ASSIGNED}

        if not to_update:
            return await self.get_department(department_id)

        stmt = update(Department).where(Department.id == department_id).values(**to_update).returning(Department)

        result = await self.db.execute(stmt)
        return result.scalars().one()

    # NOTE: requirements did not specify whether all the nested employees are accounted as root department employees.
    # I decided to include only direct employees, employee accumulation (summary) shall be implemented
    # in another method.
    async def get_department_nested(self, id: int, depth: int, include_employees: bool) -> Department:
        hierarchy = (
            select(Department, literal(1).label("depth"))
            .where(Department.id == id)
            .cte(name="hierarchy", recursive=True)
        )

        parent_alias = hierarchy.alias()
        hierarchy = hierarchy.union_all(
            select(Department, (parent_alias.c.depth + 1).label("depth"))
            .join(parent_alias, Department.parent_id == parent_alias.c.id)
            .where(parent_alias.c.depth < depth)
        )

        stmt = select(Department).join(hierarchy, Department.id == hierarchy.c.id)

        if include_employees:
            stmt = stmt.options(selectinload(Department.employees))

        return (await self.db.execute(stmt)).scalars().one()

    # NOTE: response is `no content` by requirements but I'd rather include target department details.
    @map_errors
    async def delete_department_reassign(self, id: int, target_id: int) -> None:
        async with self.db.begin():
            await self.db.execute(update(Employee).where(Employee.department_id == id).values(department_id=target_id))

            await self.db.execute(delete(Department).where(Department.id == id))
        return

    @map_errors
    async def delete_department_cascade(self, department_id: int) -> None:
        department = await self.get_department(department_id)
        await self.db.delete(department)
        return


def get_dept_repository(session: Annotated[AsyncSession, Depends(async_get_db)]):
    return DepartmentRepository(session)


DepartmentRepositoryDep = Annotated[DepartmentRepository, Depends(get_dept_repository)]
