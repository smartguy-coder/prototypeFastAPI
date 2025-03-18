from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates

from services.api import call_main_api
from services.api_constants import URLS

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
@router.post("/")
async def index(request: Request, page: int = 1, query: str = Form("")):

    products_data = await call_main_api(
        URLS.ALL_PRODUCTS, params={"limit": 8, "page": page, "q": query}
    )

    context = {
        "request": request,
        "products": products_data["items"],
        "page": products_data["page"],
        "total": products_data["total"],
        "pages": products_data["pages"],
        "imagePrefix": request.url_for("index"),
    }

    response = templates.TemplateResponse("index.html", context=context)
    return response


@router.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int):
    product = await call_main_api(URLS.ALL_PRODUCTS, params={}, path_id=product_id)
    context = {
        "request": request,
        "product": product,
        "imagePrefix": request.url_for("index"),
    }

    response = templates.TemplateResponse("product_detail.html", context=context)
    return response
