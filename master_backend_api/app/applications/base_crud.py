from abc import ABC, abstractmethod
from math import ceil
from typing import Any, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from applications.base_model_and_mixins.base_models import Base
from applications.base_queries import SearchParams, SortEnum
from applications.base_schemas import PaginationResponse


class BaseCRUD(ABC):
    model: type[Base] = None

    @abstractmethod
    def __init__(self):
        raise NotImplementedError("override in child classes")

    async def get_item(
        self,
        *,
        session: AsyncSession,
        field_value: Any,
        field: InstrumentedAttribute,
    ) -> Optional[Base] | None:
        query = select(self.model).filter(field == field_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_items(
        self,
        *,
        session: AsyncSession,
        params: SearchParams,
        targeted_schema: type[BaseModel],
        search_fields: list[InstrumentedAttribute] = None,
    ) -> PaginationResponse:
        order_direction = desc if params.order_direction == SortEnum.DESC else asc
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if params.q and search_fields:
            search_filter_condition = [
                search_field.icontains(params.q) for search_field in search_fields
            ]
            query = query.filter(or_(*search_filter_condition))
            count_query = count_query.filter(or_(*search_filter_condition))

        sort_field = getattr(self.model, params.sort_by, None)
        if sort_field is not None:
            query = query.order_by(order_direction(sort_field))

        offset = (params.page - 1) * params.limit
        query = query.offset(offset).limit(params.limit)

        result = await session.execute(query)

        result_count = await session.execute(count_query)
        total_count = result_count.scalar()

        return PaginationResponse(
            items=[targeted_schema.from_orm(item) for item in result.scalars().all()],
            total=total_count,
            page=params.page,
            limit=params.limit,
            pages=ceil(total_count / params.limit),
        )

    async def patch_item(
        self, instance_id: int, *, session: AsyncSession, data_to_patch: BaseModel
    ) -> Optional[Base]:
        item = await self.get_item(
            field=self.model.id, field_value=instance_id, session=session
        )
        if not item:
            raise HTTPException(
                detail=f"Item with id #{instance_id} was not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        data_for_updating: dict = data_to_patch.model_dump(
            exclude={"id"}, exclude_unset=True
        )
        query = (
            update(self.model)
            .where(self.model.id == instance_id)
            .values(**data_for_updating)
        )
        await session.execute(query)
        await session.commit()
        await session.refresh(item)
        return item

    async def delete_item(self, instance_id: int, *, session: AsyncSession) -> bool:
        item = await self.get_item(
            field=self.model.id, field_value=instance_id, session=session
        )
        if not item:
            raise HTTPException(
                detail=f"Item with id #{instance_id} was not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        query = delete(self.model).where(self.model.id == instance_id)
        await session.execute(query)
        await session.commit()
        return True
