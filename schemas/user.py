from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import Field, BaseModel, EmailStr, UUID4, field_validator


class UserBase(BaseModel):
    id: Annotated[int, Field(ge=0)]
    login: Annotated[str, Field(min_length=2, max_length=30)]
    password: Annotated[str, Field(min_length=2, max_length=50)]
    email: Annotated[EmailStr, Field(min_length=2, max_length=100)]
    date_registration: datetime
    count_games: Annotated[int, Field(ge=0)]
    active_game_id: int
    active_game: Optional[List[dict]]

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "login": "gjsdogjdsjg",
                "password": "1242141",
                "email": "mamulubil2010@gmail.com",
                "date_registration": "2012-12-02 23:12:42",
                "count_games": "0"
            }
        }


class CreateUser(BaseModel):
    login: Annotated[str, Field(min_length=2, max_length=30)]
    password: Annotated[str, Field(min_length=2, max_length=50)]
    email: Annotated[EmailStr, Field(min_length=2, max_length=100)]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "login": "gjsdogjdsjg",
                "password": "1242141",
                "email": "mamulubil2010@gmail.com",
            }
        }


class CheckUsers(BaseModel):
    id: Annotated[int, Field(ge=0)]
    login: Annotated[str, Field(min_length=2, max_length=30)]
    password: Annotated[str, Field(min_length=2, max_length=50)]
    email: Annotated[str, Field(min_length=2, max_length=100)]
    date_registration: datetime


class TokenBase(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True

    @field_validator("token")
    def hexlify_token(cls, value):
        return value.hex


class User(UserBase):
    token: TokenBase = {}
