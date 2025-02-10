from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.auth_handler import auth_handler
from applications.auth.schemas import LoginResponse
from applications.users.models import User
from dependencies.database import get_async_session
from dependencies.security import get_current_user

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


@router_auth.post("/force-logout", description='force logout from all devices')
async def force_logouts(user: User = Depends(get_current_user)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
