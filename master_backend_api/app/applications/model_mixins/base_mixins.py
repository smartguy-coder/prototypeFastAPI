import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class PKMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )


class CreateUpdateAtMixin(CreatedAtMixin, UpdatedAtMixin):
    pass


class UUIDMixin:
    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
