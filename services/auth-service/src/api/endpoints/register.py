from fastapi import APIRouter, Response, HTTPException, Form, File, UploadFile
from ..jw_tokens import *
from ..upload_to_s3 import upload_avatar_to_s3
from src.grpc.grpc_client import signup
from google.protobuf.json_format import MessageToDict

router = APIRouter()

@router.post('/')
async def register(
    response: Response,
    first_name: str = Form(...),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    passwd: str = Form(...),
    picture: UploadFile = File(...),
):
    if picture.content_type != 'image/jpeg' and picture.content_type != 'image/png':
        raise HTTPException(status_code=400, detail={ "error": "Invalid Type File" })
    picture_content = await picture.read()

    picture_url = await upload_avatar_to_s3(username, picture_content)

    user, error = signup({
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'email': email,
        'passwd': passwd,
        'picture': picture_url,
    })

    if user is None:
        print(f'[register failed]: {error}')
        raise HTTPException(status_code=400, detail={"error": "Failed to register user"})

    user = MessageToDict(user, preserving_proto_field_name=True)

    access_token, refresh_token = sign_tokens(user.get('user'))

    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

    return user.get('user')
