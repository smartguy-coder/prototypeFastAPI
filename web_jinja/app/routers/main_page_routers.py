from typing import Optional

from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

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

templates = Jinja2Templates(directory="templates")


@router.get("/")
@router.post("/")
async def index(
    request: Request,
    page: int = 1,
    query: str = Form(""),
    user_and_tokens=Depends(get_current_user_with_tokens),
):

    products_data = await call_main_api(
        URLS.PRODUCTS, params={"limit": 8, "page": page, "q": query}
    )

    context = {
        "request": request,
        "products": products_data["items"],
        "page": products_data["page"],
        "total": products_data["total"],
        "pages": products_data["pages"],
        "user": user_and_tokens,
    }

    response = templates.TemplateResponse("index.html", context=context)
    return await SecurityHandler.set_cookies(user_and_tokens, response)


@router.get("/product/{product_id}")
async def product_detail(
    request: Request,
    product_id: int,
    user_and_tokens=Depends(get_current_user_with_tokens),
):
    product = await call_main_api(URLS.PRODUCTS, params={}, path_id=product_id)
    context = {
        "request": request,
        "product": product,
        "user": user_and_tokens,
    }

    response = templates.TemplateResponse("product_detail.html", context=context)
    return response


@router.get("/login")
@router.post("/login")
async def login(
    request: Request,
    login_param: str = Form(None),
    password: str = Form(None),
    user_and_tokens=Depends(get_current_user_with_tokens),
):
    context = {"request": request}
    if user_and_tokens:
        redirect_url = request.url_for("index")
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return await SecurityHandler.set_cookies(user_and_tokens, response)

    if request.method == "GET":
        return templates.TemplateResponse("login.html", context=context)

    user = await SecurityHandler.authenticate_user_web(login_param, password or "")
    if user:
        redirect_url = request.url_for("index")
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return await SecurityHandler.set_cookies(user, response)
    return templates.TemplateResponse(
        "login.html",
        context={
            "request": request,
            "email": login_param,
            "errors": ["Incorrect email or password"],
        },
    )


@router.get("/register")
@router.post("/register")
async def register(
    request: Request, user_and_tokens=Depends(get_current_user_with_tokens)
):
    context = {"request": request}
    if user_and_tokens:
        redirect_url = request.url_for("index")
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return await SecurityHandler.set_cookies(user_and_tokens, response)

    if request.method == "GET":
        return templates.TemplateResponse("registration.html", context=context)

    class UserCreateForm:
        def __init__(self, request: Request):
            self.request: Request = request
            self.errors: list = []
            self.email: Optional[str] = None
            self.name: Optional[str] = None
            self.password: Optional[str] = None
            self.password_confirm: Optional[str] = None

        async def load_data(self):
            form = await self.request.form()
            self.email = form.get("email") or ""
            self.name = form.get("name") or ""
            self.password = form.get("password") or ""
            self.password_confirm = form.get("password_confirm") or ""

        async def is_valid(self):
            if not self.email or "@" not in self.email:
                self.errors.append("Please, enter valid email")

            users_found = await call_main_api(
                URLS.USERS, params={"q": self.email, "use_sharp_filter": True}
            )
            if users_found.get("total", 0) > 0:
                self.errors.append("User with this email  already exists")

            if not self.name or len(str(self.name)) < 3:
                self.errors.append("Please, enter valid name")
            if not self.password or len(str(self.password)) < 8:
                self.errors.append("Please, enter password at least 8 symbols")
            if self.password != self.password_confirm:
                self.errors.append("Confirm password did not match!")
            if not self.errors:
                return True
            return False

    new_user_form = UserCreateForm(request)
    await new_user_form.load_data()
    if await new_user_form.is_valid():
        user = await call_main_api_create_user(new_user_form)
        if not user:
            raise ValueError
        response = RedirectResponse(
            request.url_for("registered_success"), status_code=status.HTTP_303_SEE_OTHER
        )
        return response
    else:
        return templates.TemplateResponse(
            "registration.html", context=new_user_form.__dict__
        )


@router.get("/registered-success")
async def registered_success(request: Request):
    response = templates.TemplateResponse(
        "user_registered_success.html", context={"request": request}
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(
        url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/force-logout")
async def force_logout(
    request: Request, user_and_tokens=Depends(get_current_user_with_tokens)
):
    await force_logout_user(user_and_tokens["access_token"])
    response = RedirectResponse(
        url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
    )
    #  delete cookies just to clean storage
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/add-product-to-cart/")
@router.post("/add-product-to-cart/")
async def add_product_to_cart(
    request: Request,
    product_id: int = Form(default=0),
    product_title: str = Form(default=""),
    user_and_tokens=Depends(get_current_user_with_tokens),
):
    if not user_and_tokens:
        response = RedirectResponse(
            url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

    # be sure open the same page
    query_params = dict(request.query_params)
    products_data = await call_main_api(
        URLS.PRODUCTS,
        params={
            "limit": 8,
            "page": query_params.get("page") or 1,
            "q": query_params.get("query") or "",
        },
    )

    context = {
        "request": request,
        "products": products_data["items"],
        "page": products_data["page"],
        "total": products_data["total"],
        "pages": products_data["pages"],
        "user": user_and_tokens,
    }
    if product_title:
        context |= {
            # popup
            "type": "success",
            "message": f"Продукт {product_title} успішно добавлено в кошик",
        }
    response = templates.TemplateResponse("index.html", context=context)

    if request.method == "GET":
        return await SecurityHandler.set_cookies(user_and_tokens, response)

    await add_product_to_cart_request(
        quantity=1, product_id=product_id, access_token=user_and_tokens["access_token"]
    )

    return await SecurityHandler.set_cookies(user_and_tokens, response)


@router.get("/cart")
async def cart(request: Request, user_and_tokens=Depends(get_current_user_with_tokens)):
    if not user_and_tokens:
        response = RedirectResponse(
            url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

    cart_data = await call_main_api(
        URLS.ORDERS, params={}, access_token=user_and_tokens["access_token"]
    )

    context = {
        "request": request,
        "cart": cart_data,
        "user": user_and_tokens,
    }
    response = templates.TemplateResponse("cart.html", context=context)
    return await SecurityHandler.set_cookies(user_and_tokens, response)


@router.post("/quantity-product-change")
async def quantity_product_change(
    request: Request,
    product_id: int = Form(),
    mode: ModeChangeOrderProductQuantityEnum = Form(),
    user_and_tokens=Depends(get_current_user_with_tokens),
):
    if not user_and_tokens:
        response = RedirectResponse(
            url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

    await change_product_quantity_request(
        product_id, mode, user_and_tokens["access_token"]
    )

    cart_data = await call_main_api(
        URLS.ORDERS, params={}, access_token=user_and_tokens["access_token"]
    )
    context = {
        "request": request,
        "cart": cart_data,
        "user": user_and_tokens,
    }
    response = templates.TemplateResponse("cart.html", context=context)
    return await SecurityHandler.set_cookies(user_and_tokens, response)
