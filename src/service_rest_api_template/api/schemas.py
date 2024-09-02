from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    client_id: str
    content: str
    timestemp: datetime

class Client(BaseModel):
    id: int
    name: str

class Endpoint1Request(BaseModel):
    client_id: str
    content: str

class Endpoint2Request(BaseModel):
    client_id: str
    content: str

class Endpoint1Response(BaseModel):
    message: str
    timestamp: datetime

class Endpoint2Response(BaseModel):
    message: str
    timestamp: datetime