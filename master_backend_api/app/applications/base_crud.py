from abc import ABC, abstractmethod
from math import ceil
from typing import Any, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import asc, delete, desc, func, or_, select, update, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute

from applications.base_model_and_mixins.base_models import Base
from applications.base_queries import SearchParams, SortEnum
from applications.base_schemas import PaginationResponse


class BaseCRUD(ABC):
    model: type[Base] = None

    @abstractmethod
    def __init__(self):
        raise NotImplementedError("override in child classes")

    async def create_instance(self, session: AsyncSession, **kwargs) -> Optional[Base]:
        """used for creating most common instances, no additional checking or logic"""

        instance = self.model(**kwargs)
        session.add(instance)
        try:
            await session.commit()
            await session.refresh(instance)
            return instance
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                detail=f"Error has occurred while creating {self.model} with{kwargs=}, {e=}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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

    async def get_items_paginated(
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
            search_filter_condition = [search_field.icontains(params.q) for search_field in search_fields]
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

    async def get_items(
        self,
        *,
        session: AsyncSession,
        field_value: Any,
        field: InstrumentedAttribute,
    ) -> list[Base]:
        query = select(self.model).filter(field == field_value)
        result = await session.execute(query)
        return result.scalars().all()

    async def patch_item(
        self, instance_id: int, *, session: AsyncSession, data_to_patch: BaseModel, exclude_unset: bool = True
    ) -> Optional[Base]:
        """
        exclude_unset is used to show if None or default_factory must be excluded
        """
        item = await self.get_item(field=self.model.id, field_value=instance_id, session=session)
        if not item:
            raise HTTPException(
                detail=f"Item with id #{instance_id} was not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        data_for_updating: dict = data_to_patch.model_dump(exclude={"id"}, exclude_unset=exclude_unset)

        optimistic_offline_lock_version = getattr(item, "version")
        if optimistic_offline_lock_version:
            if optimistic_offline_lock_version != getattr(data_to_patch, "version"):
                raise HTTPException(
                    detail=f"Optimistic Offline Lock for instance enabled, but current version not provided or outdated",
                    status_code=status.HTTP_409_CONFLICT,
                )
            data_for_updating |= {"version": data_to_patch.version + 1}

        query = update(self.model).where(self.model.id == instance_id).values(**data_for_updating)
        await session.execute(query)
        await session.commit()
        await session.refresh(item)
        return item

    async def delete_item(self, instance_id: int, *, session: AsyncSession) -> bool:
        item = await self.get_item(field=self.model.id, field_value=instance_id, session=session)
        if not item:
            raise HTTPException(
                detail=f"Item with id #{instance_id} was not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        query = delete(self.model).where(self.model.id == instance_id)
        await session.execute(query)
        await session.commit()
        return True

    async def any_item_exists(
        self,
        session: AsyncSession,
        field_value: Any,
        field: InstrumentedAttribute,
    ) -> bool:
        query = select(exists().where(field == field_value))
        result = await session.execute(query)
        return result.scalar()

    async def get_or_create(self, session: AsyncSession, only_get: bool = False, defaults: dict = None, **kwargs):

        query = select(self.model).filter_by(**kwargs)
        result = await session.execute(query)
        instance = result.scalar_one_or_none()

        if instance or only_get:
            return instance

        instance = self.model(**kwargs, **(defaults or {}))
        session.add(instance)

        try:
            await session.commit()
            await session.refresh(instance)
            return instance
        except IntegrityError:
            await session.rollback()
            result = await session.execute(query)
            return result.scalar_one_or_none()
