from typing import Optional

from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

import stripe
from settings import settings

from services.api import (
    call_main_api,
    login_and_get_user_with_tokens,
    force_logout_user,
    call_main_api_create_user,
    add_product_to_cart_request,
    change_product_quantity_request,
)
from services.api_constants import URLS, ModeChangeOrderProductQuantityEnum

from services.security import SecurityHandler

from dependencies.user_dependencies import get_current_user_with_tokens

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

templates = Jinja2Templates(directory="templates")


@router.get("/create-payment")
async def create_payment(user_and_tokens=Depends(get_current_user_with_tokens)):
    stripe_url = await call_main_api(
        URLS.PAYMENT_HOOKS,
        path_id="payment-stripe-data",
        params={},
        access_token=user_and_tokens["access_token"],
    )

    return RedirectResponse(stripe_url["url"], status_code=status.HTTP_303_SEE_OTHER)


@router.get("/success-payment")
async def failed_payment(
    request: Request, user_and_tokens=Depends(get_current_user_with_tokens)
):
    context = {"request": request, "title": "success payment", "user": user_and_tokens}
    response = templates.TemplateResponse("success-payment.html", context=context)
    return await SecurityHandler.set_cookies(user_and_tokens, response)


@router.get("/failed-payment")
async def failed_payment(
    request: Request, user_and_tokens=Depends(get_current_user_with_tokens)
):
    context = {"request": request, "title": "failed payment", "user": user_and_tokens}
    response = templates.TemplateResponse("failed-payment.html", context=context)
    return await SecurityHandler.set_cookies(user_and_tokens, response)
