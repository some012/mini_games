from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from database import get_db
from models.models import User, Games, GamesHistory
from schemas.user import User as UserSchema, CreateUser, CheckUsers
from utilities.default_response import DefaultResponse

router = APIRouter(
    prefix="/api",
    tags=["users"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}


@router.get("/users", response_model=Union[List[UserSchema]],
            status_code=status.HTTP_200_OK)
def read_users(db: Session = Depends(get_db)):
    result = db.execute(select(User))
    all_users = result.unique().scalars().all()
    return JSONResponse(content=jsonable_encoder(all_users))


@router.get("/users/{id}", response_model=Union[UserSchema], responses=responses)
def get_user(id: int, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == id))
    this_user = user.scalar_one_or_none()
    if this_user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="User not found")

    return JSONResponse(content=jsonable_encoder(this_user))


@router.post("/users", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def register_user(user_data: CreateUser, db: Session = Depends(get_db)):
    new_user = User(
        login=user_data.login,
        password=user_data.password,
        email=user_data.email,
        date_registration=func.now(),
        count_games=0
    )

    db.add(new_user)
    db.commit()

    return DefaultResponse(success=True, message="User created successfully")


@router.post('/users/{id}', status_code=status.HTTP_201_CREATED)
def get_and_complete_game(id: int, game_id: int, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == id))
    this_user = user.scalar_one_or_none()

    game = db.execute(select(Games).filter(Games.id == game_id))
    this_game = game.scalar_one_or_none()

    result = db.execute(select(Games))
    all_games = result.unique().scalars().all()

    if not this_game:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")

    if not this_user:  # не нашли, так и не нашли
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="User not found")

    if this_user and this_game:

        if this_user.count_games >= len(all_games):
            this_user.count_games = len(all_games)
        else:
            this_user.count_games += 1

        this_user.active_game += [this_game]
        this_game.status = 2
        this_game.complete_time = func.now()

        new_game = GamesHistory(  # создаем копию и отправляем в отдельную таблицу для статистики
            original_id=this_game.id,
            name=this_game.name,
            status=this_game.status,
            complete_time=this_game.complete_time,
            user_id=this_game.user_id)

        db.add(new_game)
        db.commit()

        return DefaultResponse(success=True, status_code=201, message="Game is completed!")
    else:
        return DefaultResponse(success=False, status_code=404, message="Error")


