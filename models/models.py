from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func, FetchedValue, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(40), unique=True, index=True, nullable=False)
    login = Column(String(100))
    hashed_password = Column(String(), nullable=False)
    is_active = Column(Boolean(), server_default=FetchedValue(), nullable=False)
    date_registration = Column(DateTime, default=func.now(), nullable=False)
    count_games = Column(Integer, index=True, nullable=False, default=0)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    active_game = relationship("Games", cascade="all, delete-orphan")


class Token(BaseModel):
    __tablename__ = "tokens"

    token = Column(UUID(as_uuid=False), server_default=FetchedValue(), unique=True, nullable=False, index=True)
    expires = Column(DateTime(), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tokens")


class Games(BaseModel):
    __tablename__ = "games"

    name = Column(String(30), index=True)
    status = Column(Integer, index=True, nullable=False, default=1)
    complete_time = Column(DateTime, index=True, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    id_user = relationship("User", back_populates="active_game", lazy="selectin")


class GamesHistory(BaseModel):
    __tablename__ = "games_history"

    original_id = Column(Integer, index=True, nullable=False, default=1)
    name = Column(String(30), index=True)
    status = Column(Integer, index=True, nullable=False)
    complete_time = Column(DateTime, index=True, nullable=False, default=func.now())
    user_id = Column(Integer, index=True, nullable=False, default=1)
