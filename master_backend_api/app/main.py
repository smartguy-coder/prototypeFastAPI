from contextlib import asynccontextmanager
import socketio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from applications.admin.admin_handler import add_sqladmin_interface
from applications.auth.router import router_auth
from applications.products.routers import router_categories, router_products, router_order
from applications.users.router import router_users
from applications.payment.routers import router as payment_router
from services.redis_service import redis_service
from services.socketio_service import SocketIO, sio, NoPrefixNamespace  # ?
from settings import settings
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge
import logging

request_login_counter = Counter("custom_requests_login_total", "Total requests to /api/auth/login")
active_users = Gauge("active_users", "Number of active users")


class CustomMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import random

        active_users.set(random.randint(10, 500))
        if request.url.path == "/api/auth/login":
            request_login_counter.inc()
        response = await call_next(request)
        return response


sentry_sdk.init(
    dsn=settings.SENTRY_DNS,
    send_default_pii=True,
    traces_sample_rate=1.0,
    _experiments={"continuous_profiling_auto_start": True},
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from applications.users.crud import user_manager
    from dependencies.database import get_async_session

    session_gen = get_async_session()
    session = await anext(session_gen)
    await user_manager.create_admin(session=session)
    yield


def get_application() -> FastAPI:

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        root_path="/api",
        root_path_in_servers=True,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # _app.add_middleware(CustomMetricsMiddleware)

    _app.include_router(router_auth, prefix="/auth", tags=["Users", "Auth"])
    _app.include_router(router_users, prefix="/users", tags=["Users"])
    _app.include_router(router_products, prefix="/products", tags=["Products"])
    _app.include_router(router_categories, prefix="/categories", tags=["Products"])
    _app.include_router(router_order, prefix="/orders", tags=["Orders"])
    _app.include_router(payment_router, prefix="/payment-hooks", tags=["Payment"])

    add_sqladmin_interface(_app)

    Instrumentator().instrument(_app).expose(_app)

    _app = socketio.ASGIApp(SocketIO().get_sio_server(), _app, socketio_path="/api/socket.io")
    # _app.mount("/api/socket.io", SocketIO().sio_app)

    return _app


# app = get_application()


# @app.get("/")
# async def index():
#     logging.debug("111111112222222222222")
#     logging.info("111111112222222222222")
#     logging.warning("111111112222222222222")
#     logging.error("111111112222222222222")
#     await redis_service.set_cache("hjhjhjhjhh55555555555555551111111", 45)
#     return {"status": "OK"}
