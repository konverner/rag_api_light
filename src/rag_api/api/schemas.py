from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    client_id: str
    content: str
    timestemp: datetime

class User(BaseModel):
    id: Optional[int]
    name: str

class Document(BaseModel):
    id: int
    name: str
    content: str

class UploadFileRequest(BaseModel):
    client_id: str
    content: str

class GetDocsRequest(BaseModel):
    user: User

class GetDocsResponse(BaseModel):
    documents: list[Document]

class QueryRequest(BaseModel):
    user: User
    query: str

class QueryResponse(BaseModel):
    response: str
    source: Document
