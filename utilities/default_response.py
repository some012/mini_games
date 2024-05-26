from typing import Optional

from pydantic import BaseModel


class DefaultResponse(BaseModel):
    success: bool
    message: str


class LoginResponse(DefaultResponse):
    access_token: Optional[str]
    token_type: Optional[str] = None
