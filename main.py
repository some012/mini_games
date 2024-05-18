from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import engine, Base
from tables import users, games,games_history


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(games.router)
app.include_router(games_history.router)


@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("<a href=""/docs"" target=""_blank"">Лютый обучающий сайт, с помощью которого ты станешь ну "
                        "просто охуенным программистом</a>")
