import bcrypt
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
# from src.database.db import get_user_by_username
from .jw_tokens import sign_tokens
from .models import UserLoginModel

router = APIRouter()

@router.post('/')
async def login(data: UserLoginModel, response: Response):
    try:
        user = None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    if user is None:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    hashed = user['passwd']
    if hashed is None or bcrypt.checkpw(data.password.encode(), hashed.encode()) is False:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    del user['passwd'], user['oauth_id']
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user
