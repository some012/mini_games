from typing import Union, List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.models import GamesHistory
from schemas.games_history import GamesHistory as GameHistorySchema
from utilities import crud

router = APIRouter(
    prefix="/api",
    tags=["games_history"]
)


@router.get("/games_history", response_model=Union[List[GameHistorySchema]], status_code=status.HTTP_200_OK)
def read_games(db: Session = Depends(get_db)):
    return crud.get_all(model=GamesHistory, db=db)


@router.get("/games_history/user/{user_id}", response_model=Union[List[GameHistorySchema]])
def read_games_by_user(user_id: int, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(GamesHistory.user_id == user_id))
    this_game = game.scalars().unique().all()
    if this_game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return this_game


@router.get("/games_history/original_id/{original_id}", response_model=Union[List[GameHistorySchema]])
def read_game_by_original_id(original_id: int, db: Session = Depends(get_db)):
    game = db.execute(select(GamesHistory).filter(GamesHistory.original_id == original_id))
    this_game = game.scalars().unique().all()
    if this_game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return this_game
