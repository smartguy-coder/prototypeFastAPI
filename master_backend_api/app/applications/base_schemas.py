from datetime import datetime

from pydantic import BaseModel, Field


class BaseIdField(BaseModel):
    id: int = Field(gt=0, examples=[123])


class BaseCreatedAtField(BaseModel):
    created_at: datetime = Field(examples=[datetime.now()])


class InstanceVersion(BaseModel):
    version: int = Field(gt=0, description="Optimistic Offline Lock version")


class PaginationResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    pages: int


class StatusSuccess(BaseModel):
    success: bool = True
