from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates

from services.api import call_main_api
from services.api_constants import URLS

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index(
    request: Request,
):
    categories = await call_main_api(URLS.ALL_CATEGORIES)
    context = {"request": request, "categories": categories}

    response = templates.TemplateResponse(
        "index.html",
        context=context,
    )
    return response


@router.get("/api/categories/")
def dd():
    return {"h": 5656}
