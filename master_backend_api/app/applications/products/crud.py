from applications.base_crud import BaseCRUD
from applications.products.models import Category, Product


class CategoryDBManager(BaseCRUD):

    def __init__(self):
        self.model = Category


class ProductDBManager(BaseCRUD):

    def __init__(self):
        self.model = Product


category_manager = CategoryDBManager()
product_manager = ProductDBManager()
