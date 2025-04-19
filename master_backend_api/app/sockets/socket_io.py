from socketio import AsyncServer, ASGIApp

sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://127.0.0.1", "http://localhost:10000"],
)
