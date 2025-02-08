from typing import Optional
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from applications.base import Base
from applications.model_mixins.base_mixins import PKMixin, CreatedAtMixin


class User(PKMixin, CreatedAtMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str]
    user_uuid: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
    is_active: Mapped[bool] = mapped_column(default=True)
    verified_at: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f'User {self.name} -> #{self.id}'
