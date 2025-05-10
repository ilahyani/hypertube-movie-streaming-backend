import bcrypt
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from ..models import UserLoginModel
from ..jw_tokens import *
from src.grpc.grpc_client import login_user
from google.protobuf.json_format import MessageToDict

router = APIRouter()

@router.post('/')
async def login(data: UserLoginModel, response: Response):
    user, error = login_user(data.username)
    if user is None:
        print('[login failed]', error)
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    user = MessageToDict(user, preserving_proto_field_name=True)
    user = user['user']
    hashed = user['passwd']
    if hashed is None or bcrypt.checkpw(data.password.encode(), hashed.encode()) is False:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    del user['passwd']
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True, domain=localhost)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, domain=localhost)
    return user
