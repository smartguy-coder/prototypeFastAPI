import json
from typing import Union

from applications.auth.auth_handler import AuthHandler
from applications.users.crud import user_manager
from dependencies.database import get_async_session_instance, get_async_session

from applications.users.models import User

from services.redis_service import redis_service


async def get_user_from_data(user_data: dict):

    token = user_data.get("user", {}).get("access_token")
    if not token:
        return
    payload = await AuthHandler().decode_token(token)

    user = await user_manager.get_item(
        field=User.email, field_value=payload.get("email"), session=await get_async_session_instance()
    )
    return user


async def store_users_data(sid: str, user: Union["User", dict]):
    if isinstance(user, dict):
        data = user
    else:
        data = {"id": user.id, "name": str(user.name), "email": str(user.email)}
    key = "socketio:users"
    await redis_service.hset(key=key, field=sid, value=json.dumps(data), ttl=60 * 60 * 24)


async def set_user_data(sid: str, user: "User"):
    key = f"socketio:user:{user.id}"
    await redis_service.lpush(key=key, value=sid, ttl=60 * 60 * 24)


async def link_sid_with_user(sid: str, user: "User"):
    key = f"socketio:sid:{sid}"
    await redis_service.set_cache(key=key, value=str(user.id))
