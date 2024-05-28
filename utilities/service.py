from fastapi import Depends
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from utilities.hash import get_hashed_password


def search_login_user(username: str, password: str, db: Session = Depends(get_db)) -> User | None:
    user_in_db = db.execute(select(User).filter(
        or_((User.login == username and User.password == get_hashed_password(password)),
            (User.email == username and User.password == get_hashed_password(password)))))
    this_user = user_in_db.scalar_one_or_none()
    return this_user
