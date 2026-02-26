from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.database import Base
from src.app.core.db.values import CreatedAtMixin, IDMixin

if TYPE_CHECKING:
    from src.app.models.department import Department


class Employee(Base, CreatedAtMixin, IDMixin):
    __tablename__ = "employee"

    department_id: Mapped[int | None] = mapped_column(ForeignKey("department.id", ondelete="CASCADE"))

    full_name: Mapped[str] = mapped_column(String(200))
    position: Mapped[str] = mapped_column(String(200))
    hired_at: Mapped[datetime | None] = mapped_column()

    department: Mapped[Department | None] = relationship("Department", back_populates="employees")
