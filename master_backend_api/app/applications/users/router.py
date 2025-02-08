from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from applications.users.crud import UserDBManager
from applications.users.models import User
from applications.users.schemas import RegisterUserRequest, SavedUser
from dependencies.database import get_async_session

user_db_manager = UserDBManager()

router_users = APIRouter(prefix="/users", tags=["Users", "API"], dependencies=[])


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    new_user: RegisterUserRequest,
    session: AsyncSession = Depends(get_async_session),
) -> SavedUser:
    maybe_user: User | None = await user_db_manager.get(
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
