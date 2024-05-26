import hashlib
import random
import string
from datetime import datetime, timedelta

from sqlalchemy import and_

from database import get_db
from models.models import Token, User
from schemas import user as user_schema


async def get_random_string(length=12):
    """ Генерирует случайную строку, использующуюся как соль """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


async def hash_password(password: str, salt: str = None):
    """ Хеширует пароль с солью """
    if salt is None:
        salt = await get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


async def validate_password(password: str, hashed_password: str):
    """ Проверяет, что хеш пароля совпадает с хешем из БД """
    salt, hashed = hashed_password.split("$")
    return await hash_password(password, salt) == hashed


async def get_user_by_email(email: str):
    """ Возвращает информацию о пользователе """
    async with get_db() as session:
        query = session.execute(User.select().where(User.c.email == email))
        return await query.fetchone()


async def get_user_by_token(token: str):
    """ Возвращает информацию о владельце указанного токена """
    async with get_db() as session:
        query = session.execute(
            Token.join(User).select().where(
                and_(
                    Token.c.token == token,
                    Token.c.expires > datetime.now()
                )
            )
        )
        return await query.fetchone()


async def create_user_token(user_id: int):
    """ Создает токен для пользователя с указанным user_id """
    async with get_db() as session:
        query = (
            Token.insert()
            .values(expires=datetime.now() + timedelta(weeks=2), user_id=user_id)
            .returning(Token.c.token, Token.c.expires)
        )
        return await session.execute(query)


async def create_user(user: user_schema.CreateUser):
    """ Создает нового пользователя в БД """
    salt = await get_random_string()
    hashed_password = await hash_password(user.password, salt)
    async with get_db() as session:
        query = User.insert().values(
            email=user.email, name=user.name, hashed_password=f"{salt}${hashed_password}"
        )
        user_id = await session.execute(query)
        token = await create_user_token(user_id)
        token_dict = {"token": token["token"], "expires": token["expires"]}
        return {**user.dict(), "id": user_id, "is_active": True, "token": token_dict}
