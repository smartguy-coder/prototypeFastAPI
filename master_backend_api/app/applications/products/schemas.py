from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_serializer

from applications.base_schemas import BaseCreatedAtField, BaseIdField, PaginationResponse
from utils.camel_case import to_camel


class NewCategory(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["laptops", "phones"])


class SavedCategory(NewCategory, BaseCreatedAtField, BaseIdField):
    class Config:
        from_attributes = True


class PaginationSavedCategoriesResponse(PaginationResponse):
    items: list[SavedCategory]


class SavedProduct(BaseIdField):
    title: str
    price: float
    category_id: int
    images: list[str]
    main_image: str

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True


class PaginationSavedProductsResponse(PaginationResponse):
    items: list[SavedProduct]


class ProductSchema(BaseModel):
    id: int
    title: str
    price: float = Field(..., alias="currentPrice")
    main_image: str
    images: list[str]

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


class AddOrderProductBodySchema(BaseModel):
    quantity: Annotated[Optional[int], Field(default=1, ge=1, le=5000)] = 1
    product_id: Annotated[int, Field(ge=1)]
