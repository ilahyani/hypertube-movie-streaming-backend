from fastapi import APIRouter, Response, HTTPException
from .models import UserRegistrationModel
# from src.database.db import add_user_to_db
from .jw_tokens import sign_tokens
# import jw_tokens
from src.grpc.grpc_client import signup
from google.protobuf.json_format import MessageToDict

router = APIRouter()

@router.post('/')
async def register_user(user: UserRegistrationModel, response: Response):
    user, error = signup(user.dict())
    if user is None:
        print(f'[auth_register failed]: {error}')
        return HTTPException(status_code=400, detail={"error": "Failed to register user"})
    user = MessageToDict(user, preserving_proto_field_name=True)
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user