from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from roters.main_page.main_page_routers import router as main_page_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def get_application() -> FastAPI:

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        root_path_in_servers=True,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(main_page_router, tags=["Main page"])

    return _app


app = get_application()


@app.get("/")
async def index():
    return "kjhjhkj"
