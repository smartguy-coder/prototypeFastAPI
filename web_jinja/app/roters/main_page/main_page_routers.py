from fastapi import APIRouter, Request, Form, status, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from services.api import call_main_api, login_and_get_user_with_tokens
from services.api_constants import URLS

from services.security import SecurityHandler

from dependencies.user_dependencies import get_current_user_with_tokens

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# class UserCreateForm:
#     def __init__(self, request: Request):
#         self.request: Request = request
#         self.errors: list = []
#         self.email: Optional[str] = None
#         self.name: Optional[str] = None
#         self.password: Optional[str] = None
#         self.password_confirm: Optional[str] = None
#         self.hashed_password: str = ""
#
#     async def load_data(self):
#         form = await self.request.form()
#         self.email = form.get("email")
#         self.name = form.get("name") or ""
#         self.password = form.get("password")
#         self.password_confirm = form.get("password_confirm")
#
#     async def is_valid(self, session: AsyncSession):
#         if not self.email or "@" not in self.email:
#             self.errors.append("Please? enter valid email")
#
#         maybe_user = await dao.get_user_by_email(self.email, session)
#         if maybe_user:
#             self.errors.append("User with this email  already exists")
#
#         if not self.name or len(str(self.name)) < 3:
#             self.errors.append("Please? enter valid name")
#         if not self.password or len(str(self.password)) < 8:
#             self.errors.append("Please? enter password at least 8 symbols")
#         if self.password != self.password_confirm:
#             self.errors.append("Confirm password did not match!")
#         if not self.errors:
#             return True
#         return False


@router.get("/")
@router.post("/")
async def index(
    request: Request,
    page: int = 1,
    query: str = Form(""),
    user_and_tokens=Depends(get_current_user_with_tokens),
):

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
    product = await call_main_api(URLS.ALL_PRODUCTS, params={}, path_id=product_id)
    context = {
        "request": request,
        "product": product,
        "imagePrefix": request.url_for("index"),
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

    # new_user_form = UserCreateForm(request)
    # await new_user_form.load_data()
    # if await new_user_form.is_valid(session):
    #     hashed_password = await PasswordEncrypt.get_password_hash(
    #         new_user_form.password
    #     )
    #
    #     saved_user = await dao.create_user(
    #         name=new_user_form.name,
    #         email=new_user_form.email,
    #         hashed_password=hashed_password,
    #         session=session,
    #     )
    #     background_tasks.add_task(
    #         send_email_verification,
    #         user_email=saved_user.email,
    #         user_uuid=saved_user.user_uuid,
    #         user_name=saved_user.name,
    #         host=request.base_url,
    #     )
    #     redirect_url = request.url_for("index")
    #     response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    #     return await SecurityHandler.set_cookies_web(saved_user, response)
    # else:
    #     return templates.TemplateResponse(
    #         "registration.html", context=new_user_form.__dict__
    #     )


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(
        url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
