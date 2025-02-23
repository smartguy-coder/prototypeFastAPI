from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from applications.base_model_and_mixins.base_mixins import CreateUpdateAtMixin, PKMixin, UUIDMixin
from applications.base_model_and_mixins.base_models import Base
from constants.permissions import UserPermissionsEnum as UPE


class User(PKMixin, CreateUpdateAtMixin, UUIDMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]]
    permissions: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=lambda: [UPE.CAN_SELF_EDIT, UPE.CAN_SELF_DELETE]
    )
    metadata_info: Mapped[dict] = mapped_column(JSONB, server_default=sa.text("'{}'::jsonb"))
    use_token_since: Mapped[datetime] = mapped_column(
        default=func.now(), doc="Used to force logout, not allowing token issued before"
    )

    def __repr__(self) -> str:
        return f"User {self.name} -> #{self.id}"
