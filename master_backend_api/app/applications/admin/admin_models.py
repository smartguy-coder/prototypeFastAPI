from typing import TYPE_CHECKING

from sqladmin import ModelView

from applications.products.models import Category, Product
from applications.users.models import User
from applications.products.crud import category_manager
from dependencies.database import get_async_session
from applications.base_schemas import InstanceVersion
from starlette.requests import Request

if TYPE_CHECKING:
    from applications.base_model_and_mixins.base_models import Base


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email]
    icon = "fa-solid fa-users"
    category = "accounts"
    column_default_sort = [(User.email, True), (User.name, False)]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.id]
    form_excluded_columns = [User.hashed_password]
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True


class OptimisticOfflineLockValidator:
    @classmethod
    async def check_version(cls, model: "Base", provided_version: int) -> None:
        """if concurrency occurs - will raise hard error (in sentry), but let it be"""
        session_gen = get_async_session()
        session = await anext(session_gen)
        data_to_patch = InstanceVersion(version=provided_version)
        await category_manager.patch_item(instance_id=model.id, session=session, data_to_patch=data_to_patch)


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
    column_labels = {"id": "ID категорії", "name": "Назва категорії"}
    name = "Категорія"
    name_plural = "Категорії"
    form_columns = ["name", "version"]
    category = "products"
    icon = "fa-solid fa-chart-line"

    async def on_model_change(self, data: dict, model: "Base", is_created: bool, request: Request) -> None:
        await OptimisticOfflineLockValidator.check_version(model=model, provided_version=data["version"])


class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.title, Product.price]
    column_labels = {
        "id": "ID продукту",
        "title": "Назва продукту",
        "price": "Ціна",
        "category": "Категорія",
        "images": "Зображення",
        "main_image": "Головне зображення",
    }
    name = "Продукт"
    name_plural = "Продукти"
    form_columns = ["title", "price", "category"]
    category = "products"
    icon = "fa-solid fa-box"
