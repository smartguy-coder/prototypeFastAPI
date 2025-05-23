from enum import IntEnum, StrEnum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator


class PaginationParams(IntEnum):
    MAX_RESULTS_PER_PAGE = 50


class SortEnum(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortFields(StrEnum):
    ID = "id"
    UPDATED_AT = "updated_at"
    CREATED_AT = "created_at"


class SearchParams(BaseModel):
    q: Annotated[Optional[str], Field(default=None)] = None
    page: Annotated[int, Field(default=1, ge=1)]
    limit: Annotated[int, Field(default=10, le=PaginationParams.MAX_RESULTS_PER_PAGE.value, ge=1)]
    order_direction: SortEnum = SortEnum.DESC
    sort_by: SortFields = SortFields.ID
    use_sharp_filter: bool = Field(default=False, description="used to search exact q")

    @field_validator("q")
    def strip_q(cls, v):
        return v.strip() if v else v
