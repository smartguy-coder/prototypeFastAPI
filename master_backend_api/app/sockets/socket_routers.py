import json
from datetime import datetime

from services.redis_service import redis_service
from sockets import socket_utils


from sockets.socket_io import sio
from sockets.socket_utils import get_user_from_data


@sio.event
async def connect(sid, environ):
    await socket_utils.store_users_data(sid, user={"id": -1, "name": "-", "email": "-"})

    print(f"Клиент подключился: {sid}")
    users = await redis_service.hgetall("socketio:users")

    await sio.emit("users", {"Кол-во пользователей": len(users)})
    await sio.emit("users_list", {"users_list": users})
    await sio.emit("my_messages", {"message": sid}, to=sid)


@sio.event
async def disconnect(sid):
    await redis_service.hdel("socketio:users", sid)
    await redis_service.delete_cache(sid)

    print(f"Клиент отключился: {sid}")

    users = await redis_service.hgetall("socketio:users")

    await sio.emit("users", {"Кол-во пользователей": len(users)})
    await sio.emit("users_list", {"users_list": users})


@sio.event
async def get_users(sid, data, *args):
    users = await redis_service.hgetall("socketio:users")
    print(data, args)

    await sio.emit("users_list", {"users_list": users})


@sio.event
async def set_user(sid, data: dict | str, *args):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return

    user = await get_user_from_data(data)
    if not user:
        return

    await socket_utils.set_user_data(sid=sid, user=user)
    await socket_utils.store_users_data(sid=sid, user=user)
    await socket_utils.link_sid_with_user(sid=sid, user=user)
    users = await redis_service.hgetall("socketio:users")
    await sio.emit("users_list", {"users_list": users})


@sio.event
async def my_messages(sid, data, *args):
    user_id = await redis_service.get_cache(key=f"socketio:sid:{sid}")
    print(user_id, 66666666666666666666666666666)
    sids = await redis_service.lrange(f"socketio:user:{user_id}")
    await sio.emit(
        "my_messages", {"title": "new title", "time": str(datetime.now()), "message": "test message"}, to=sids
    )
    users = await redis_service.hgetall("socketio:users")
    print(users, 88888888888888888888888)
    await sio.emit("users_list", {"users_list": users})
    return """callback as a response in socket.emit("my_messages", {}, (response) => {
        console.log("my_messages:", response);});
    """
