from pydantic import BaseModel, Field

from applications.base_schemas import (
    BaseCreatedAtField,
    BaseIdField,
    PaginationResponse,
)


class NewCategory(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["laptops", "phones"])


class SavedCategory(NewCategory, BaseCreatedAtField, BaseIdField):
    class Config:
        from_attributes = True


class PaginationSavedCategoriesResponse(PaginationResponse):
    items: list[SavedCategory]
