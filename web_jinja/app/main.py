from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from routers.main_page_routers import router as main_page_products_router
from routers.payment_routers import router as payment_routers


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

    _app.mount("/static", StaticFiles(directory="static"), name="static")

    _app.include_router(main_page_products_router, tags=["Main page"])
    _app.include_router(payment_routers, prefix="/payment", tags=["Main page"])

    return _app


app = get_application()
