import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.password_handler import PasswordEncrypt
from applications.auth.schemas import LoginResponse
from applications.users.crud import user_manager
from applications.users.models import User
from services.redis_service import redis_service
from settings import settings


class AuthHandler:

    def __init__(self):
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM

    async def get_login_token_pairs(self, data: OAuth2PasswordRequestForm, session: AsyncSession) -> LoginResponse:

        user: User | None = await user_manager.get_item(field=User.email, field_value=data.username, session=session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email not found",
            )
        is_valid_password = await PasswordEncrypt.verify_password(data.password, user.hashed_password)
        if not is_valid_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password is incorrect")
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not verified",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are banned. Please contact support",
            )

        token_pairs: LoginResponse = await self.generate_token_pair(user)
        return token_pairs

    async def generate_token(self, payload: dict, expiry: timedelta) -> str:
        now = datetime.now()
        time_payload = {"exp": now + expiry, "iat": now}
        payload.update(time_payload)
        token_ = jwt.encode(payload, self.secret, self.algorithm)
        return token_

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret, [self.algorithm])
            payload["iat"] = datetime.fromtimestamp(payload.get("iat") or 0)
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Time is out")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    async def generate_token_pair(self, user: User) -> LoginResponse:
        access_token_payload = {
            "sub": str(user.id),
            "email": user.email,
        }
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_TIME_MINUTES)
        access_token = await self.generate_token(access_token_payload, access_token_expires)

        refresh_token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "key": uuid.uuid4().hex,
        }
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_TIME_MINUTES)
        refresh_token = await self.generate_token(refresh_token_payload, refresh_token_expires)
        await redis_service.set_cache(
            key=refresh_token_payload["key"],
            value=user.id,
            ttl=refresh_token_expires.total_seconds(),
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_token_expires.seconds,
        )

    async def get_refresh_token(self, refresh_token: str, session: AsyncSession) -> LoginResponse:
        payload = await self.decode_token(refresh_token)

        refresh_token_key = payload.get("key")
        stored_refresh = await redis_service.get_cache(refresh_token_key)
        if not stored_refresh:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token was used already")

        await redis_service.delete_cache(refresh_token_key)
        user: User = await user_manager.get_item(field=User.id, field_value=int(payload["sub"]), session=session)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        if user.use_token_since > payload["iat"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User forced logout")

        token_pair = await self.generate_token_pair(user)
        return token_pair


auth_handler = AuthHandler()
