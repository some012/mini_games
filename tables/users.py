from typing import Union, List

from fastapi import APIRouter, status
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from schemas.user import User as UserSchema, CreateUser, CheckUsers
from services import user_service
from utilities import crud
from utilities.default_response import DefaultResponse
from utilities.hash import (
    verify_password, get_hashed_password
)

router = APIRouter(
    prefix="/api",
    tags=["users"]
)


@router.get("/users", response_model=Union[List[CheckUsers], List[UserSchema]],
            status_code=status.HTTP_200_OK)
def read_users(db: Session = Depends(get_db)):
    return crud.get_all(model=User, db=db)


@router.get("/users/{id}", response_model=Union[CheckUsers])
def get_user(id: int, db: Session = Depends(get_db)):
    user = crud.get_by_id(model=User, id=id, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/register", status_code=status.HTTP_200_OK)
def register_user(username: str, email: EmailStr, password: str, db: Session = Depends(get_db)):
    user = user_service.search_register_user(login=username, email=email, password=password,
                                             db=db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this login already exist"
        )

    user_structure: CreateUser = CreateUser(
        login=username, email=email, password=get_hashed_password(password)
    )

    crud.create(model=User, schema=user_structure, db=db)

    return DefaultResponse(success=True, message="User created")


@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = user_service.search_login_user(username=username, password=password, db=db)

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
