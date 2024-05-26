from fastapi import FastAPI
from starlette.responses import HTMLResponse

from config import POSTGRES_DATABASE_URL
from database import db_manager
from tables import users, games, games_history

db_manager.init(POSTGRES_DATABASE_URL)

app = FastAPI()

app.include_router(users.router)
app.include_router(games.router)
app.include_router(games_history.router)


@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("<a href=""/docs"" target=""_blank"">Лютый обучающий сайт, с помощью которого ты станешь ну "
                        "просто охуенным программистом</a>")
