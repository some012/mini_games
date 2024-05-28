from typing import Union, List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.models import Games, GamesHistory
from schemas.games import Games as GameSchema, CreateGames, CheckGames, UpdateGames
from schemas.games_history import GamesHistoryCreate
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
def create_game(games_data: CreateGames, db: Session = Depends(get_db)):
    game_structure: CreateGames = CreateGames(
        name=games_data.name,
        status=1,
        complete_time=func.now())

    new_game = crud.create(model=Games, schema=game_structure, db=db)

    return new_game


@router.post('/users/{user_id}', status_code=status.HTTP_201_CREATED)
def get_and_complete_game(id: int, user_id: int, db: Session = Depends(get_db)):
    user = crud.get_by_id(model=Games, id=id, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    game = crud.get_by_id(db=db, id=id, model=Games)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    if game.status == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already completed!"
        )

    user.count_games += 1
    user.active_game.append(game)
    game_update: UpdateGames = UpdateGames(
        status=2, complete_time=func.now(), user_id=user_id)
    game.status = 2
    game.complete_time = func.now()
    crud.update(model=user, schema=game_update, db=db)
    # Создание записи об игре в истории игр
    new_game_history = GamesHistoryCreate(
        original_id=game.id,
        name=game.name,
        status=game.status,
        complete_time=game.complete_time,
        user_id=user_id
    )
    crud.create(model=GamesHistory, schema=new_game_history, db=db)

    return DefaultResponse(success=True, status_code=status.HTTP_201_CREATED, message="Game is completed!")
