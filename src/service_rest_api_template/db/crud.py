from datetime import datetime

from service_rest_api_template.db.models import Message, Client
from sqlalchemy.orm import Session
from service_rest_api_template.db.database import get_session


def add_client(name: str) -> Client:
    db: Session = get_session()
    db_client = Client(name=name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    db.close()
    return db_client

def read_client(client_id: int) -> Client:
    db: Session = get_session()
    result = db.query(Client).filter(Client.id == client_id).first()
    db.close()
    return result

def create_client(name: str) -> Client:
    db: Session = get_session()
    db_client = Client(name=name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    db.close()
    return db_client

def create_message(client_id: int, content: str, timestamp: datetime) -> Message:
    db: Session = get_session()
    db_message = Message(client_id=client_id, content=content, timestamp=timestamp)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    db.close()
    return db_message
