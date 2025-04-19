from main_factory import get_application
from sockets.socket_routers import sio
from socketio import ASGIApp

app = get_application()
socket_app = ASGIApp(sio, app, socketio_path="/api/socket.io")
