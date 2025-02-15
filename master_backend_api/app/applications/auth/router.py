import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.auth_handler import auth_handler
from applications.auth.schemas import LoginResponse, EmailRequest, ResetRequest
from applications.users.crud import user_manager
from applications.users.models import User
from dependencies.database import get_async_session
from dependencies.security import get_current_user
from services.redis_service import redis_service

router_auth = APIRouter()


@router_auth.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponse:
    token_pair = await auth_handler.get_login_token_pairs(data, session)
    return token_pair


@router_auth.post("/refresh")
async def refresh_user_token(
    refresh_token=Header(), session: AsyncSession = Depends(get_async_session)
) -> LoginResponse:
    token_pair = await auth_handler.get_refresh_token(refresh_token, session=session)
    return token_pair


@router_auth.post("/force-logout", description="force logout from all devices")
async def force_logouts(user: User = Depends(get_current_user)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router_auth.post(
    "/forgot-password-email",
    description="Email (sms in future) password recovery, works with reset-password endpoint",
)
async def forgot_password_email(
    data: EmailRequest, session: AsyncSession = Depends(get_async_session)
):
    user: User = await user_manager.get_item(
        field=User.email, field_value=data.email, session=session
    )
    if not user or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your account is not verified. Please check your email inbox to verify your account.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been dactivated. Please contact support.",
        )

    # todo - save token send email - valid link 5 min - next process in reset password
    await redis_service.set_cache(
        f"user:{user.id}:forgot_password_token", value=uuid.uuid4().hex, ttl=5 * 60
    )
    return {"temp_password_send": data.email}


@router_auth.put("/reset-password")
async def reset_password(
    data: ResetRequest, session: AsyncSession = Depends(get_async_session)
):
    # todo - maybe not a put
    user = await user_manager.get_item(
        field=User.email, field_value=data.email, session=session
    )

    if not user or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your account is not verified. Please check your email inbox to verify your account.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )
    saved_token = await redis_service.get_cache(f"user:{user.id}:forgot_password_token")
    if saved_token != data.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    # todo update hashed password
    await redis_service.delete_cache(f"user:{user.id}:forgot_password_token")
    return {"password updated": True}
