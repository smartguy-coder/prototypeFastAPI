from pydantic import BaseModel, EmailStr, Field

from applications.base_schemas import (
    BaseCreatedAtField,
    BaseIdField,
    PaginationResponse,
)


class BaseFields(BaseModel):
    email: EmailStr = Field(description="User email", examples=["example@ukr.net"])
    name: str = Field(
        description="Name of user", examples=["John Doe"], min_length=3, max_length=50
    )


class PasswordField(BaseModel):
    password: str = Field(
        description="your unique password", examples=["12345678"], min_length=8
    )


class IsActiveField(BaseModel):
    is_active: bool


class RegisterUserRequest(PasswordField, BaseFields):
    pass


class PatchDetailedUser(BaseFields, IsActiveField):
    class Config:
        from_attributes = True


class SavedUser(PatchDetailedUser, BaseCreatedAtField, BaseIdField):
    pass


class PaginationSavedUserResponse(PaginationResponse):
    items: list[SavedUser]


class UserRegistrationMessage(BaseModel):
    user_name: str
    lang: str
    email: EmailStr
    redirect_url: str
    base_url: str
