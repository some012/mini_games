from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base


def get_all(model: Base, db: Session):
    result = db.execute(select(model))
    return result.scalars().all()


def get_by_id(model: Base, id: int, db: Session):
    return db.get(model, id)


def create(model: Base, schema: BaseModel, db: Session):
    db_model = model(**schema.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def update(model: Base, schema: BaseModel, db: Session):
    db_model = get_by_id(model, schema.id, db)
    if db_model is None:
        return None

    for var, value in vars(schema).items():
        setattr(db_model, var, value) if value else None

    db.commit()
    db.refresh(db_model)
    return db_model


def delete(model: Base, id: int, db: Session):
    db_user = get_by_id(model, id, db)
    if db_user is None:
        return

    db.delete(db_user)
    db.commit()
