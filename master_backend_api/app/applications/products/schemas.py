import nh3
from pydantic import BaseModel, Field, field_validator

from applications.base_schemas import BaseCreatedAtField, BaseIdField, PaginationResponse, InstanceVersion

from utils.camel_case import to_camel
from utils.images import ensure_full_url


class NewCategory(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["laptops", "phones"])


class PatchCategorySchema(InstanceVersion, NewCategory):
    pass


class SavedCategory(NewCategory, BaseCreatedAtField, BaseIdField, InstanceVersion):
    class Config:
        from_attributes = True


class PaginationSavedCategoriesResponse(PaginationResponse):
    items: list[SavedCategory]


class SavedProduct(BaseIdField):
    title: str
    description: str
    price: float
    category_id: int
    images: list[str]
    main_image: str

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True

    @field_validator("images", "main_image", mode="before")
    @classmethod
    def validate_images(cls, value):

        if isinstance(value, list):
            return [ensure_full_url(img) for img in value]
        return ensure_full_url(value)

    @field_validator("title", "description", mode="before")
    @classmethod
    def sanitize_html(cls, v):
        #  for xss security

        if isinstance(v, str):
            return nh3.clean(v, tags=set())
        return v


class PaginationSavedProductsResponse(PaginationResponse):
    items: list[SavedProduct]


class ProductSchema(BaseModel):
    id: int
    title: str
    price: float = Field(..., alias="currentPrice")
    main_image: str
    images: list[str]
    description: str = ""

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True


class OrderProductSchema(BaseModel):
    price: float
    quantity: int
    total: float
    product: ProductSchema

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True


class OrderSchema(BaseCreatedAtField):
    is_closed: bool
    user_id: int
    cost: float
    order_products: list[OrderProductSchema]

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True

    def filter_zero_quantity_products(self):
        self.order_products = [item for item in self.order_products if item.quantity > 0]

    def get_filtered_order(self):
        self.filter_zero_quantity_products()
        self.order_products.sort(key=lambda item: item.product.id)
        return self
