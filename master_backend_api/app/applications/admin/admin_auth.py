from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from applications.auth.password_handler import PasswordEncrypt
from applications.users.crud import user_manager
from applications.users.models import User
from services.redis_service import redis_service


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        user_email = form.get("username")
        password = form.get("password")

        from dependencies.database import get_async_session

        session_gen = get_async_session()
        session = await anext(session_gen)

        user: User = await user_manager.get_item(
            field=User.email, field_value=user_email, session=session
        )
        if not user or not user.is_admin:
            return False

        if not PasswordEncrypt.verify_password(password, user.hashed_password):
            return False

        session_token = await PasswordEncrypt.get_password_hash(user_email)

        await redis_service.set_cache(
            f"session:{user.id}", session_token, ttl=60 * 60 * 24
        )

        request.session.update({"token": session_token, "user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        """Remove session from Redis."""
        user_id = request.session.get("user_id")
        if user_id:
            await redis_service.delete_cache(f"session:{user_id}")

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Verify if the session token is valid."""
        session_token = request.session.get("token")
        user_id = request.session.get("user_id")

        if not session_token or not user_id:
            return False  # No session

        # Retrieve the stored token from Redis
        stored_token = await redis_service.get_cache(f"session:{user_id}")

        return session_token == stored_token  # Compare tokens
