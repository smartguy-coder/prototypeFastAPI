from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates
import httpx

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index(
    request: Request,
):

    context = {
        "request": request,
    }

    response = templates.TemplateResponse(
        "index.html",
        context=context,
    )
    return response
