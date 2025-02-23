import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.auth_handler import auth_handler
from applications.auth.schemas import EmailRequest, LoginResponse, ResetRequest, ForceLogout, UserRecoveryPassword
from applications.base_schemas import StatusSuccess
from applications.users.crud import user_manager
from applications.users.models import User
from dependencies.database import get_async_session
from dependencies.security import get_current_user
from services.rabbit.constants import SupportedQueues
from services.rabbit.rabbitmq_service import rabbitmq_producer
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
async def force_logouts(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
) -> StatusSuccess:

    await user_manager.patch_item(user.id, data_to_patch=ForceLogout(), exclude_unset=False, session=session)
    return StatusSuccess()


@router_auth.post(
    "/forgot-password",
    description="Email (sms in future) password recovery, works with reset-password endpoint",
)
async def forgot_password(request: Request, data: EmailRequest, session: AsyncSession = Depends(get_async_session)):
    user: User = await user_manager.get_item(field=User.email, field_value=data.email, session=session)
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

    token = uuid.uuid4().hex
    await redis_service.set_cache(f"user:{token}:forgot_password_token", value=user.id, ttl=5 * 60)
    await rabbitmq_producer.send_message(
        UserRecoveryPassword(
            user_name=user.name,
            lang="uk",
            email=user.email,
            base_url=str(request.base_url),
            redirect_url=f"{str(request.base_url)}docs#/Auth/reset_password_auth_reset_password__user_recovery_password_token__post",
            token=token,
        ).dict(),
        queue_name=SupportedQueues.USER_RECOVERY_PASSWORD,
    )
    return {"temp_password_send": data.email}


@router_auth.post("/reset-password/{user_recovery_password_token}")
async def reset_password(
    user_recovery_password_token: str, data: ResetRequest, session: AsyncSession = Depends(get_async_session)
):
    user_id = await redis_service.get_cache(f"user:{user_recovery_password_token}:forgot_password_token")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your token is invalid or expired",
        )
    user = await user_manager.get_item(field=User.id, field_value=int(user_id), session=session)

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

    await redis_service.delete_cache(f"user:{user_recovery_password_token}:forgot_password_token")

    await user_manager.change_user_password(user_id=user.id, new_password=data.password, session=session)
    return {"password updated": True}
