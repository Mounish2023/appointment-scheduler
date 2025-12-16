from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Conversation(BaseModel):
    conversationid: str
    document_ids: list[str] = []
    query: str
    response: str
    # citations: list[str] = []
    created_at: datetime
    updated_at: datetime

class Session(BaseModel):
    sessionid: str
    userid: str
    conversations: list[Conversation]
    document_ids: list[str] = []
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# class User(BaseModel):
#     userid: str
#     name: str
#     email: str
#     password: str
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True