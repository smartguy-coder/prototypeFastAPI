from applications.products.crud import category_manager
from applications.products.models import Category
from applications.products.shemas import (
    NewCategory,
    SavedCategory,
    PaginationSavedCategoriesResponse,
)
from applications.users.crud import user_manager
from applications.users.models import User
from fastapi import status, APIRouter
from applications.users.schemas import (
    PaginationSavedUserResponse,
    PatchDetailedUser,
    RegisterUserRequest,
    SavedUser,
    UserRegistrationMessage,
)
from constants.messages import HelpTexts
from constants.permissions import UserPermissionsEnum
from dependencies.database import get_async_session
from dependencies.security import require_permissions
from services.rabbit.constants import SupportedQueues
from services.rabbit.rabbitmq_service import rabbitmq_producer
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_queries import SearchParams
from applications.base_schemas import StatusSuccess

router_categories = APIRouter()


@router_categories.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))
    ],
)
async def create_category(
    new_category: NewCategory,
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:
    maybe_category: Category | None = await category_manager.get_item(
        field=Category.name, field_value=new_category.name, session=session
    )
    if maybe_category:
        raise HTTPException(
            detail=f"Category {maybe_category.name} already exists",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    saved_category = await category_manager.create_category(
        name=new_category.name,
        session=session,
    )

    return SavedCategory.from_orm(saved_category)


@router_categories.get("/{id}")
async def get_user(
    category_id: int = Path(
        ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
    ),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:
    user = await category_manager.get_item(
        field=Category.id, field_value=category_id, session=session
    )
    if not user:
        raise HTTPException(
            detail=f"Category with id #{category_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SavedCategory.from_orm(user)


@router_categories.get("/")
async def get_categories(
    params: Annotated[SearchParams, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginationSavedCategoriesResponse:
    result = await category_manager.get_items(
        params=params,
        search_fields=[Category.name],
        targeted_schema=SavedCategory,
        session=session,
    )
    return result


@router_categories.patch(
    "/{id}",
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))
    ],
)
async def update_category(
    category_data: NewCategory,
    category_id: int = Path(
        ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
    ),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:
    category_updated = await category_manager.patch_item(
        category_id, data_to_patch=category_data, session=session
    )
    return SavedCategory.from_orm(category_updated)


@router_categories.delete(
    "/{id}",
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))
    ],
)
async def delete_category(
    category_id: int = Path(
        ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
    ),
    session: AsyncSession = Depends(get_async_session),
) -> StatusSuccess:
    # todo check deleting with products in it
    await category_manager.delete_item(category_id, session=session)
    return StatusSuccess()
