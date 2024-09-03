from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    client_id: str
    content: str
    timestemp: datetime

class User(BaseModel):
    id: int
    name: str

class Document(BaseModel):
    id: int
    name: str,
    content: str

class UploadFileRequest(BaseModel):
    client_id: str
    content: str

class GetDocsRequest(BaseModel):
    user: User

class GetDocsResponse(BaseModel):
    documents = list[Document]