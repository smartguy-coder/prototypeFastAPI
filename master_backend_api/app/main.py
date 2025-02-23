from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from applications.admin.admin_handler import add_sqladmin_interface
from applications.auth.router import router_auth
from applications.products.routers import router_categories, router_products
from applications.users.router import router_users
from services.redis_service import redis_service
from settings import settings
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    from applications.users.crud import user_manager
    from dependencies.database import get_async_session

    session_gen = get_async_session()
    session = await anext(session_gen)
    await user_manager.create_admin(session=session)

    redis_connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        # password=settings.REDIS_PASSWORD,
        # username=settings.RE
        db=settings.REDIS_DATABASES,
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_connection)
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
    _app.include_router(router_products, prefix="/products", tags=["Products"])
    _app.include_router(router_categories, prefix="/categories", tags=["Products", "Categories"])

    add_sqladmin_interface(_app)
    return _app


app = get_application()


@app.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=100))])
async def index():

    await redis_service.set_cache("hjhjhjhjhh55555555555555551111111", 45)
    return {"status": settings.DATABASE_URL}
