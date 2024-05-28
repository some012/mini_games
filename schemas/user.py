from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import Field, BaseModel


class User(BaseModel):
    id: Annotated[int, Field(ge=0)]
    login: Annotated[str, Field(min_length=2, max_length=30)]
    password: Annotated[str, Field(min_length=2, max_length=200)]
    email: Annotated[str, Field(min_length=2, max_length=100)]
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
    password: Annotated[str, Field(min_length=2, max_length=200)]
    email: Annotated[str, Field(min_length=2, max_length=100)]

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
    password: Annotated[str, Field(min_length=2, max_length=200)]
    email: Annotated[str, Field(min_length=2, max_length=100)]
    date_registration: datetime
