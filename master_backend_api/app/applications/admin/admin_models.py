from sqladmin import ModelView

from applications.products.models import Category, Product
from applications.users.models import User


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


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
    column_labels = {"id": "ID категорії", "name": "Назва категорії"}
    name = "Категорія"
    name_plural = "Категорії"
    form_columns = ["name"]
    category = "products"
    icon = "fa-solid fa-chart-line"


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
