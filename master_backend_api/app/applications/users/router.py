from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_queries import SearchParams
from applications.constants.messages import HelpTexts
from applications.users.crud import UserDBManager
from applications.users.models import User
from applications.users.schemas import (PaginationSavedUserResponse,
                                        RegisterUserRequest, SavedUser)
from dependencies.database import get_async_session

user_db_manager = UserDBManager()

router_users = APIRouter(prefix="/users", tags=["Users", "API"], dependencies=[])


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: RegisterUserRequest,
    session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    maybe_user: User | None = await user_db_manager.get_item(
        field=User.email, field_value=new_user.email, session=session
    )
    if maybe_user:
        raise HTTPException(
            detail=f"User {maybe_user.name} with email {maybe_user.email} already exists",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    saved_user = await user_db_manager.create_user(
        name=new_user.name,
        email=new_user.email,
        password=new_user.password,
        session=session,
    )
    # todo: implement email verification
    return SavedUser.from_orm(saved_user)


@router_users.get("/{user_id}")
async def get_user(
    user_id: int = Path(..., title=HelpTexts.ITEM_PATH_ID_PARAM, ge=1),
    session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    user = await user_db_manager.get_item(
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
    result = await user_db_manager.get_items(
        params=params,
        search_fields=[User.name, User.email],
        targeted_schema=SavedUser,
        session=session,
    )

    return result
