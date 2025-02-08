from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from applications.base_models import Base


class BaseCRUD(ABC):
    model: type[Base] = None

    @abstractmethod
    def __init__(self):
        raise NotImplementedError("override in child classes")

    async def get(
        self, *, session: AsyncSession, field_value: Any, field: InstrumentedAttribute
    ) -> Optional[Base]:
        query = select(self.model).filter(field == field_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()
