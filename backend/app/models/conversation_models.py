from pydantic import BaseModel
from datetime import datetime

class Conversation(BaseModel):
    conversationid: str
    query: str
    response: str
    created_at: datetime
    updated_at: datetime

class Session(BaseModel):
    sessionid: str
    userid: str
    conversations: list[Conversation]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

