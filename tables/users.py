from typing import Union, List

from fastapi import APIRouter, status, Response
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import encode
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from config import ALGORITHM, SECRET_KEY
from database import get_db
from models.models import User
from schemas.user import User as UserSchema, CreateUser
from utilities.default_response import DefaultResponse, LoginResponse
from utilities.service import get_current_user

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
    return JSONResponse(content=jsonable_encoder(all_users))


@router.get("/users/{id}", response_model=Union[UserSchema], responses=responses)
def get_user(id: int, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == id))
    this_user = user.scalar_one_or_none()
    if this_user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponse(success=False, message="User not found")

    return JSONResponse(content=jsonable_encoder(this_user))


@router.get("/me", response_model=UserSchema)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserSchema:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return current_user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: CreateUser, db: Session = Depends(get_db)):
    user_in_db = db.execute(select(User).filter(User.login == user_data.login))
    this_user = user_in_db.scalar_one_or_none()
    if this_user:
        return JSONResponse(content={"message": "User with this login already exists."},
                            status_code=status.HTTP_400_BAD_REQUEST)

    new_user = User(
        login=user_data.login,
        password=user_data.password,
        email=user_data.email,
        date_registration=func.now(),
        count_games=0)

    db.add(new_user)
    db.commit()

    return DefaultResponse(success=True, message="User created")


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(or_(User.email == form_data.username, User.login == form_data.username)))
    this_user = user.scalar_one_or_none()
    if not this_user or this_user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": this_user.id}
    access_token = encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(success=True, message="Login successful", access_token=access_token, token_type="bearer")
