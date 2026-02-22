from datetime import datetime

from sqlalchemy import DateTime, Identity, text
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("current_timestamp(0)"))


class IDMixin:
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
