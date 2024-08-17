import bcrypt
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from database.db import get_user_from_db
from jw_tokens import sign_tokens

router = APIRouter()

class UserLoginModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9]+$')
    password: str = Field(..., min_length=8, max_length=16)

@router.post('/api/auth/login')
async def login(data: UserLoginModel, response: Response):
    user = await get_user_from_db(data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    hashed = user['passwd']
    if bcrypt.checkpw(data.password.encode(), hashed.encode()) is False:
        raise HTTPException(status_code=401, detail="Incorrect password")
    del user['passwd']
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user
