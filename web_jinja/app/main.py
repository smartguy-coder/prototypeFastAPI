from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates

from settings import settings
from routers.main_page_routers import router as main_page_products_router
from routers.payment_routers import router as payment_routers
from dependencies.user_dependencies import get_current_user_with_tokens


templates = Jinja2Templates(directory="templates")


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


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(
    request: Request,
    exc: StarletteHTTPException,
    user_and_tokens=Depends(get_current_user_with_tokens),
):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": user_and_tokens}, status_code=404
        )
    return HTMLResponse(content="Помилка", status_code=exc.status_code)
