from typing import Union, List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.models import Games
from schemas.games import Games as GameSchema, CreateGames, CheckGames
from services import games_service
from utilities import crud
from utilities.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["games"]
)


@router.get("/games", response_model=Union[List[CheckGames], List[GameSchema]], status_code=status.HTTP_200_OK)
def read_games(db: Session = Depends(get_db)):
    return crud.get_all(db=db, model=Games)


@router.get("/games/{id}", response_model=Union[GameSchema])
def get_games(id: int, db: Session = Depends(get_db)):
    game = crud.get_by_id(db=db, id=id, model=Games)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game


@router.post("/games", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def create_game(name: str, db: Session = Depends(get_db)):
    crud.create(model=Games, schema=CreateGames(name=name), db=db)
    return DefaultResponse(success=True, message="Game created")


@router.post('/complete/{id}', status_code=status.HTTP_201_CREATED)
def get_and_complete_game(id: int, user_id: int, db: Session = Depends(get_db)):
    return games_service.complete_game(id=id, user_id=user_id, db=db)
