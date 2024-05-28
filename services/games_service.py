from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.models import Games, GamesHistory, User
from schemas.games import UpdateGames
from schemas.games_history import GamesHistoryCreate
from schemas.user import UpdateUser
from utilities import crud
from utilities.default_response import DefaultResponse


def complete_game(id: int, user_id: int, db: Session):
    user = crud.get_by_id(model=User, id=user_id, db=db)

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

    if not (game and user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User and Game not found"
        )

    all_games = crud.get_all(model=Games, db=db)

    user_update: UpdateUser = UpdateUser(
        id=user.id,
        login=user.login,
        password=user.password,
        email=user.email,
        date_registration=user.date_registration,
        count_games=user.count_games + 1,
        active_game=user.active_game.append(game)
    )

    if user_update.count_games >= len(all_games):
        user_update.count_games = len(all_games)

    crud.update(model=User, schema=user_update, db=db)

    game_update: UpdateGames = UpdateGames(id=game.id, name=game.name,
                                           status=1, complete_time=datetime.now(), user_id=user_id)

    crud.update(model=Games, schema=game_update, db=db)

    new_game_history: GamesHistoryCreate = GamesHistoryCreate(
        original_id=game.id,
        name=game.name,
        status=2,
        complete_time=game.complete_time,
        user_id=user_id
    )
    crud.create(model=GamesHistory, schema=new_game_history, db=db)

    return DefaultResponse(success=True, status_code=status.HTTP_201_CREATED, message="Game is completed!")
