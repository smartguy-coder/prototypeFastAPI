from datetime import datetime

from services.redis_service import redis_service
from sockets import socket_utils


from sockets.socket_io import sio
from sockets.socket_utils import get_user_from_data

list_users = []


@sio.event
async def connect(sid, environ):
    list_users.append(sid)

    print(f"Клиент подключился: {sid}")

    await sio.emit("users", {"Кол-во пользователей": len(list_users)})
    await sio.emit("my_messages", {"message": sid}, to=sid)

    await sio.emit("users_list", {"Список пользователей": list_users})


@sio.event
async def disconnect(sid):
    if sid in list_users:
        list_users.remove(sid)

    print(f"Клиент отключился: {sid}")

    await sio.emit("users", {"Кол-во пользователей": len(list_users)})

    await sio.emit("users_list", {"Список пользователей": list_users})


@sio.event
async def get_users(sid, data, *args):
    print(f"Список пользователей: {list_users}")
    print(data, args)

    await sio.emit("users_list", {"Список пользователей": list_users})


@sio.event
async def set_user(sid, data: dict, *args):
    # todo create map for user
    print(f"{data=}", 888888888)

    user = await get_user_from_data(data)
    if not user:
        return

    await socket_utils.set_user_data(sid=sid, user=user)
    await socket_utils.link_sid_with_user(sid=sid, user=user)


@sio.event
async def my_messages(sid, data, *args):
    user_id = await redis_service.get_cache(key=f"socketio:sid:{sid}")
    sids = await redis_service.lrange(f"socketio:user:{user_id}")
    await sio.emit(
        "my_messages", {"title": "new title", "time": str(datetime.now()), "message": "test message"}, to=sids
    )
