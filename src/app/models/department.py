from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.database import Base
from src.app.core.db.values import CreatedAtMixin, IDMixin

if TYPE_CHECKING:
    from src.app.models.employee import Employee


class Department(Base, IDMixin, CreatedAtMixin):
    __tablename__ = "department"

    name: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("department.id", ondelete="CASCADE"))

    parent: Mapped[Department | None] = relationship(
        "Department", remote_side="Department.id", back_populates="children"
    )
    children: Mapped[list[Department]] = relationship("Department", back_populates="parent")
    employees: Mapped[list[Employee]] = relationship("Employee", back_populates="department")

    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="depratment_parent_id_unique_name"),
        CheckConstraint("parent_id <> id", name="department_parent_id_not_itself"),
    )
