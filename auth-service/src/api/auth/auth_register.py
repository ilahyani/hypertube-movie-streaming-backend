from fastapi import APIRouter, Response, HTTPException
from .models import UserRegistrationModel
from src.database.db import add_user_to_db
from .jw_tokens import sign_tokens
# import jw_tokens

router = APIRouter()

@router.post('/')
async def register_user(user: UserRegistrationModel, response: Response):
    user = await add_user_to_db(user.dict(), False)
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user