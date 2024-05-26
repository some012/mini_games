from typing import Union, List

from fastapi import APIRouter, status, Response, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from database import get_db
from models.models import Games
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
async def read_games(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Games))
    all_games = result.scalars().unique().all()
    return all_games


@router.get("/games/{id}", response_model=Union[GameSchema],
            responses=responses)
async def get_games(id: int, response: Response, db: AsyncSession = Depends(get_db)):
    game = await db.execute(select(Games).filter(Games.id == id))
    this_game = game.scalar_one_or_none()
    if this_game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="Game not found")
    return JSONResponse(content=jsonable_encoder(this_game))


@router.post("/games", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
async def create_game(games_data: CreateGames, db: AsyncSession = Depends(get_db)):
    new_game = Games(
        name=games_data.name,
        status=1,
        complete_time=func.now())

    db.add(new_game)
    await db.commit()

    return DefaultResponse(success=True, message="Game created successfully")
