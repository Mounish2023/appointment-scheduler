from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import uuid
from datetime import datetime, timedelta
import jwt
from app.database import MongoDBClient
from app import schemas, auth
# from app.models.conversation_models import User
from app.schemas import TokenData, User
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from app.schemas import Token, UserInDB
from app.auth import oauth2_scheme, verify_password, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import os


router = APIRouter(prefix="/auth", tags=["auth"])

def get_users_collection():
    client = MongoDBClient()
    return client.get_collection(collection_name="users")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    users_collection = get_users_collection()
    user = await users_collection.find_one({"username": token_data.username})
    if not user:
        raise credentials_exception
    user = UserInDB(**user)
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def authenticate_user(username: str, password: str):
    users_collection = get_users_collection()
    user = await users_collection.find_one({"username": username})
    if not user:
        return False
    user = UserInDB(**user)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        sub=user.username, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return current_user


@router.post("/register", response_model=dict)
async def register(
    payload: schemas.UserCreate
):
    users_collection = get_users_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"username": payload.username})
    # existing_user = UserInDB(**existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    now = datetime.utcnow()
    user = UserInDB(
        userid=str(uuid.uuid4()),
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name or payload.email.split("@")[0],
        hashed_password=auth.get_password_hash(payload.password), # storing hashed password in password field as per model
        created_at=now,
        updated_at=now
    )
    
    await users_collection.insert_one(user.model_dump())
    
    return {"msg": "User registered successfully"}

# @router.post("/login", response_model=schemas.Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends()
# ):
#     users_collection = get_users_collection()
    
#     # Find user by email
#     user_data = await users_collection.find_one({"username": form_data.username})
    
#     if not user_data:
#          raise HTTPException(status_code=400, detail="Incorrect credentials")
         
#     user = User(**user_data)
    
#     # Verify password
#     # Note: User model has 'password' field, which should store the hash
#     if not auth.verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=400, detail="Incorrect credentials")
    
#     # Create and return access token
#     token = auth.create_access_token(user.email)
#     return {"access_token": token, "token_type": "bearer"}
