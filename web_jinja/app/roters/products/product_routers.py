from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

templates = Jinja2Templates(directory="app\\templates")


@router.post("/")
@router.get("/")
async def get_menu(
    request: Request,
):

    context = {
        "request": request,
    }

    return templates.TemplateResponse(
        "menu.html",
        context=context,
    )
