from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(30), index=True, nullable=False)
    password = Column(String(50), index=True, nullable=False)
    email = Column(String(100), index=True, nullable=False)
    date_registration = Column(DateTime, default=func.now(), nullable=False)
    count_games = Column(Integer, index=True, nullable=False, default=0)

    active_game = relationship("Games", cascade="all, delete-orphan")


class Games(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), index=True)
    status = Column(Integer, index=True, nullable=False, default=1)
    complete_time = Column(DateTime, index=True, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    id_user = relationship("User", back_populates="active_game", lazy="selectin")


class GamesHistory(Base):
    __tablename__ = "games_history"

    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer, index=True, nullable=False, default=1)
    name = Column(String(30), index=True)
    status = Column(Integer, index=True, nullable=False)
    complete_time = Column(DateTime, index=True, nullable=False, default=func.now())
    user_id = Column(Integer, index=True, nullable=False, default=1)

