from select import select
from sqlalchemy.orm import Session

from models.models import GamesHistory


def get_game_by_user(id: int, model: GamesHistory, db: Session):
    game = db.execute(select(model).filter(model.user_id == id))
    this_game = game.unique().scalars().all()
    return this_game


def get_game_by_original_id(id: int, model: GamesHistory, db: Session):
    game = db.execute(select(model).filter(model.original_id == id))
    this_game = game.unique().scalars().all()
    return this_game
