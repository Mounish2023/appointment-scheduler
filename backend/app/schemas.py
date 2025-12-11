# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str]
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    userid: str
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    created_at: datetime
    updated_at: datetime


class UserInDB(User):
    hashed_password: str
