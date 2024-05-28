from datetime import datetime
from typing import Annotated

from pydantic import Field, BaseModel


class GamesHistory(BaseModel):
    original_id: Annotated[int, Field(ge=0)]
    name: Annotated[str, Field(min_length=2, max_length=30)]
    status: Annotated[int, Field(ge=0)]
    complete_time: datetime
    user_id: Annotated[int, Field(ge=0)]

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "name": "Вставь слово!",
                "complete_date": "2012-12-02 23:12:42",
                "status": "1"
            }
        }


class GamesHistoryCreate(GamesHistory):
    pass
