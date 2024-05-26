from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from models.models import Games, GamesHistory, User
from schemas.games import Games as GameSchema, CreateGames, CheckGames
from utilities.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["games"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/games", response_model=Union[List[CheckGames], List[GameSchema]], status_code=status.HTTP_200_OK)
def read_games(db: Session = Depends(get_db)):
    result = db.execute(select(Games))
    all_games = result.unique().scalars().all()
    return all_games


@router.get("/games/{id}", response_model=Union[GameSchema],
            responses=responses)
def get_games(id: int, response: Response, db: Session = Depends(get_db)):
    game = db.execute(select(Games).filter(Games.id == id))
    this_game = game.scalar_one_or_none()
    if this_game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return this_game


@router.post("/games", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def create_game(games_data: CreateGames, db: Session = Depends(get_db)):
    new_game = Games(
        name=games_data.name,
        status=1,
        complete_time=func.now())

    db.add(new_game)
    db.commit()

    return new_game


@router.post('/users/{user_id}', status_code=status.HTTP_201_CREATED)
def get_and_complete_game(id: int, user_id: int, response: Response, db: Session = Depends(get_db)):
    # Поиск пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="User not found")

    # Поиск игры
    game = db.query(Games).filter(Games.id == id).first()
    if not game:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")

    if game.status == 2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DefaultResponse(success=False, message="Game already completed")

    # Обновление количества сыгранных игр у пользователя
    user.count_games += 1

    # Добавление завершенной игры к активным играм пользователя
    user.active_game.append(game)

    # Обновление статуса и времени завершения игры
    game.status = 2
    game.complete_time = func.now()

    # Создание записи об игре в истории игр
    new_game_history = GamesHistory(
        original_id=game.id,
        name=game.name,
        status=game.status,
        complete_time=game.complete_time,
        user_id=user_id
    )
    db.add(new_game_history)

    # Сохранение изменений в базе данных
    db.commit()

    return DefaultResponse(success=True, status_code=status.HTTP_201_CREATED, message="Game is completed!")
