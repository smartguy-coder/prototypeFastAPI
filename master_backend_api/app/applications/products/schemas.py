from pydantic import BaseModel, Field

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
