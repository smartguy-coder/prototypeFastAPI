from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from applications.auth.router import router_auth
from applications.users.router import router_users
from services.redis_service import redis_service
from settings import settings


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

    _app.include_router(router_auth, prefix="/auth", tags=["Users", "Auth"])
    _app.include_router(router_users, prefix="/users", tags=["Users"])

    return _app


app = get_application()


@app.get("/")
async def index():

    await redis_service.set_cache("hjhjhjhjhh55555555555555551111111", 45)
    return {"status": settings.DATABASE_URL}
