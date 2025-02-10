import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_queries import SearchParams
from applications.base_schemas import StatusSuccess
from applications.users.crud import user_manager
from applications.users.models import User
from applications.users.schemas import (PaginationSavedUserResponse,
                                        PatchDetailedUser, RegisterUserRequest,
                                        SavedUser)
from constants.messages import HelpTexts
from constants.permissions import UserPermissionsEnum
from dependencies.database import get_async_session
from dependencies.security import require_permissions

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: RegisterUserRequest,
        session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    maybe_user: User | None = await user_manager.get_item(
        field=User.email, field_value=new_user.email, session=session
    )
    if maybe_user:
        raise HTTPException(
            detail=f"User {maybe_user.name} with email {maybe_user.email} already exists",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    saved_user = await user_manager.create_user(
        name=new_user.name,
        email=new_user.email,
        password=new_user.password,
        session=session,
    )
    # todo: implement email verification (host rout ready)
    return SavedUser.from_orm(saved_user)


@router_users.get("/verify/{user_uuid}", description='verification via email expected')
async def verify_user(user_uuid: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> StatusSuccess:
    await user_manager.activate_user_account(user_uuid, session)
    return StatusSuccess()


@router_users.get("/{id}")
async def get_user(
        user_id: int = Path(
            ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
        ),
        session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    user = await user_manager.get_item(
        field=User.id, field_value=user_id, session=session
    )
    if not user:
        raise HTTPException(
            detail=f"User with id #{user_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SavedUser.from_orm(user)


@router_users.get("/")
async def get_users(
        params: Annotated[SearchParams, Depends()],
        session: AsyncSession = Depends(get_async_session),
) -> PaginationSavedUserResponse:
    result = await user_manager.get_items(
        params=params,
        search_fields=[User.name, User.email],
        targeted_schema=SavedUser,
        session=session,
    )
    return result


@router_users.patch("/{id}")
async def update_user(
        user_data: PatchDetailedUser,
        user_id: int = Path(
            ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
        ),
        session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    user_updated = await user_manager.patch_item(
        user_id, data_to_patch=user_data, session=session
    )
    return SavedUser.from_orm(user_updated)


@router_users.delete("/{id}", dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_DELETE_USER]))])
async def delete_user(
        user_id: int = Path(
            ..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"
        ),
        session: AsyncSession = Depends(get_async_session),
) -> StatusSuccess:
    await user_manager.delete_item(user_id, session=session)
    return StatusSuccess()
