from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import get_settings


def get_application() -> FastAPI:
    settings = get_settings()

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.get("/")
def index():
    return {"status": get_settings().DATABASE_URL}
