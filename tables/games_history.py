from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import get_db
from models.models import GamesHistory, User
from schemas.games_history import GamesHistory as GameHistorySchema
from utilities.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["games_history"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/games_history", response_model=Union[List[GameHistorySchema]], status_code=status.HTTP_200_OK)
def read_games(db: Session = Depends(get_db)):
    result = db.execute(select(GamesHistory))
    all_games = result.unique().scalars().all()
    return all_games


@router.get("/games_history_by_user/{id}", response_model=Union[List[GameHistorySchema]],
            responses=responses)
def get_games_by_user(id: int, response: Response, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(id == GamesHistory.user_id))
    this_game = game.unique().scalars().all()
    if this_game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return JSONResponse(content=jsonable_encoder(this_game))


@router.get("/games_history/{id}", response_model=Union[List[GameHistorySchema]],
            responses=responses)
def get_game_by_original_id(id: int, response: Response, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(id == GamesHistory.original_id))
    this_game = game.unique().scalars().all()
    if this_game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return JSONResponse(content=jsonable_encoder(this_game))
