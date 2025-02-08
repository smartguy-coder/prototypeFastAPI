from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from applications.users.router import router_users
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from applications.users.crud import UserDBManager
    from applications.users.models import User
    from dependencies.database import get_async_session

    user_manager = UserDBManager()

    session_gen = get_async_session()
    session = await anext(session_gen)
    admin = await user_manager.get(
        field=User.email, field_value=settings.DEFAULT_ADMIN_USER_EMAIL, session=session
    )
    if not admin:
        await user_manager.create_user(
            name=settings.DEFAULT_ADMIN_USER_NAME,
            email=settings.DEFAULT_ADMIN_USER_EMAIL,
            password=settings.DEFAULT_ADMIN_USER_PASSWORD,
            is_verified=True,
            is_admin=True,
            notes="system created user",
            session=session,
        )
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

    _app.include_router(router_users)

    return _app


app = get_application()


@app.get("/")
def index():
    return {"status": settings.DATABASE_URL}
