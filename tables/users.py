from typing import Union, List

from fastapi import APIRouter, status, Response
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from schemas.user import User as UserSchema, CreateUser
from utilities import service
from utilities.default_response import DefaultResponse
from utilities.hash import get_hashed_password
from utilities.hash import (
    verify_password
)

router = APIRouter(
    prefix="/api",
    tags=["users"]
)

responses = {
    status.HTTP_404_NOT_FOUND: {"model": DefaultResponse, "description": "Item not found"}
}

security = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/users", response_model=Union[List[UserSchema]],
            status_code=status.HTTP_200_OK)
def read_users(db: Session = Depends(get_db)):
    result = db.execute(select(User))
    all_users = result.unique().scalars().all()
    return all_users


@router.get("/users/{id}", response_model=Union[UserSchema], responses=responses)
def get_user(id: int, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == id))
    this_user = user.scalar_one_or_none()
    if this_user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="User not found")

    return this_user


@router.post("/register", status_code=status.HTTP_200_OK)
def register_user(user_data: CreateUser, db: Session = Depends(get_db)):
    user_in_db = db.execute(select(User).filter(User.login == user_data.login))
    this_user = user_in_db.scalar_one_or_none()
    if this_user:
        return JSONResponse(content={"message": "User with this login already exists."},
                            status_code=status.HTTP_400_BAD_REQUEST)

    new_user = User(
        login=user_data.login,
        password=get_hashed_password(user_data.password),
        email=user_data.email,
        date_registration=func.now(),
        count_games=0)

    db.add(new_user)
    db.commit()

    return DefaultResponse(success=True, message="User created")


@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = service.search_login_user(username=username, password=password, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect login or password"
        )

    hashed_pass = user.password
    if not verify_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect login or password"
        )

    return DefaultResponse(success=True, message="Login success")
