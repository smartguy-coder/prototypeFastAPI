from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from applications.base_model_and_mixins.base_mixins import (
    CreateUpdateAtMixin, PKMixin, UUIDMixin)
from applications.base_model_and_mixins.base_models import Base


class User(PKMixin, CreateUpdateAtMixin, UUIDMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"User {self.name} -> #{self.id}"
