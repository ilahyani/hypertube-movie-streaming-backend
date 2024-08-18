import bcrypt
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from database.db import get_user_from_db
from .jw_tokens import sign_tokens
from .models import UserLoginModel

router = APIRouter()

@router.post('/')
async def login(data: UserLoginModel, response: Response):
    user = await get_user_from_db(data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    hashed = user['passwd']
    if hashed is None or bcrypt.checkpw(data.password.encode(), hashed.encode()) is False:
        raise HTTPException(status_code=401, detail="Incorrect password")
    del user['passwd']
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user
