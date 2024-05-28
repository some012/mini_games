from typing import Union, List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.models import GamesHistory
from schemas.games_history import GamesHistory as GameHistorySchema

router = APIRouter(
    prefix="/api",
    tags=["games_history"]
)


@router.get("/games_history", response_model=Union[List[GameHistorySchema]], status_code=status.HTTP_200_OK)
def read_games(db: Session = Depends(get_db)):
    result = db.execute(select(GamesHistory))
    all_games = result.unique().scalars().all()
    return all_games


@router.get("/games_history_by_user/{id}", response_model=Union[List[GameHistorySchema]])
def get_games_by_user(id: int, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(id == GamesHistory.user_id))
    this_game = game.unique().scalars().all()
    if this_game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return this_game


@router.get("/games_history/{id}", response_model=Union[List[GameHistorySchema]])
def get_game_by_original_id(id: int, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(id == GamesHistory.original_id))
    this_game = game.unique().scalars().all()
    if this_game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return this_game
