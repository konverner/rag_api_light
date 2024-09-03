from datetime import datetime

from rag_api.db.database import get_session
from rag_api.db.models import DbMessage, DbUser
from sqlalchemy.orm import Session


def add_user(name: str) -> DbUser:
    db: Session = get_session()
    db_user = DbUser(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

def read_user(name: str) -> DbUser:
    db: Session = get_session()
    result = db.query(DbUser).filter(DbUser.name == name).first()
    db.close()
    return result

def delete_user(name: str) -> None:
    db: Session = get_session()
    user = db.query(DbUser).filter(DbUser.name == name).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

def get_all_users() -> list[DbUser]:
    db: Session = get_session()
    users = db.query(DbUser).all()
    db.close()
    return users

def create_message(user_id: int, content: str, timestamp: datetime) -> DbMessage:
    db: Session = get_session()
    db_message = DbMessage(user_id=user_id, content=content, timestamp=timestamp)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    db.close()
    return db_message
