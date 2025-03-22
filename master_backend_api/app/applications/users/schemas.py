import re
from pydantic import BaseModel, EmailStr, Field, model_validator

from applications.base_schemas import BaseCreatedAtField, BaseIdField, PaginationResponse


class BaseFields(BaseModel):
    email: EmailStr = Field(description="User email", examples=["example@ukr.net"])
    name: str = Field(description="Name of user", examples=["John Doe"], min_length=3, max_length=50)


class PasswordField(BaseModel):
    password: str = Field(description="your unique password", examples=["JKghg565*-JK"], min_length=8)

    @model_validator(mode="before")
    def validate_password_strength(cls, values: dict) -> dict:
        """FastAPI converts ValueError to irs 422 error"""
        password = values.get("password")

        if password:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long.")

            if " " in password:
                raise ValueError("Password cannot contain spaces.")

            if not re.search(r"[A-Z]", password):
                raise ValueError("Password must contain at least one uppercase letter.")

            if not re.search(r"[0-9]", password):
                raise ValueError("Password must contain at least one digit.")

            if not re.search(r"[\W_]", password):
                raise ValueError("Password must contain at least one special character.")

        return values


class IsActiveField(BaseModel):
    is_active: bool


class RegisterUserRequest(PasswordField, BaseFields):
    pass


class PatchDetailedUser(BaseFields, IsActiveField):
    class Config:
        from_attributes = True


class SavedUser(PatchDetailedUser, BaseCreatedAtField, BaseIdField):
    is_admin: bool = False


class PaginationSavedUserResponse(PaginationResponse):
    items: list[SavedUser]


class UserRegistrationMessage(BaseModel):
    user_name: str
    lang: str
    email: EmailStr
    redirect_url: str
    base_url: str


class UserHashedPassword(BaseModel):
    hashed_password: str
