import socketio


class SocketIO:

    def __init__(self):
        self.sio_server = socketio.AsyncServer(
            async_mode="asgi", cors_allowed_origins=["*"], transports=["websocket", "polling"]
        )
        self.sio_app = socketio.ASGIApp(
            self.sio_server,
            socketio_path="/api/socket.io/",
        )

    def get_sio_server(self):
        return self.sio_server


sio = SocketIO().sio_server


class NoPrefixNamespace(socketio.AsyncNamespace):
    # recheck this internet code
    # how does it should works?
    def on_connect(self, sid, environ):
        print("connect ", sid)

    async def on_message(self, sid, data):
        print("message ", data)
        await sio.emit("response", "hi " + data)

    def on_disconnect(self, sid):
        print("disconnect ", sid)
