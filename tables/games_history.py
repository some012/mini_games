from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from database import get_db
from models.models import GamesHistory
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
async def read_games(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GamesHistory))
    all_games = result.scalars().unique().all()
    return all_games


@router.get("/games_history_by_user/{id}", response_model=Union[List[GameHistorySchema]], responses=responses)
async def get_games_by_user(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    game = await db.execute(select(GamesHistory).filter(GamesHistory.user_id == id))
    this_game = game.scalars().unique().all()
    if not this_game:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return JSONResponse(content=jsonable_encoder(this_game))


@router.get("/games_history/{id}", response_model=Union[List[GameHistorySchema]], responses=responses)
async def get_game_by_original_id(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    game = await db.execute(select(GamesHistory).filter(GamesHistory.original_id == id))
    this_game = game.scalars().unique().all()
    if not this_game:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return JSONResponse(content=jsonable_encoder(this_game))
