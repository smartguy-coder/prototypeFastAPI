from pydantic import BaseModel, EmailStr


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str = "Bearer"


class EmailRequest(BaseModel):
    email: EmailStr


class ResetRequest(EmailRequest):
    token: str
    password: str
