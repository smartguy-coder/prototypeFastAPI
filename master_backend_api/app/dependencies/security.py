from enum import StrEnum

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.auth_handler import AuthHandler
from applications.users.crud import user_manager
from applications.users.models import User
from dependencies.database import get_async_session


class SecurityHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(SecurityHandler.oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    payload = await AuthHandler().decode_token(token)

    user = await user_manager.get_item(
        field=User.email, field_value=payload.get("email"), session=session
    )
    return user


async def get_admin_user(user: User | None = Depends(get_current_user)) -> User:
    if user and user.is_admin:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin user required"
    )


def require_permissions(required_permissions: list[StrEnum]):
    def dependency(user: User | None = Depends(get_current_user)) -> User:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated",
            )

        user_permissions = set(user.permissions)
        required_permissions_set = {perm.value for perm in required_permissions}

        if user.is_admin or required_permissions_set.issubset(user_permissions):
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission(s) {', '.join(required_permissions_set)} required",
        )

    return dependency
