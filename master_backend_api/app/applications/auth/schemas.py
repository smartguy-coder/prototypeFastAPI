from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str = "Bearer"


class EmailRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    password: str


class ForceLogout(BaseModel):
    use_token_since: datetime = Field(default_factory=datetime.now)


class UserRecoveryPassword(BaseModel):
    user_name: str
    lang: str
    email: EmailStr
    base_url: str
    redirect_url: str
    token: str
