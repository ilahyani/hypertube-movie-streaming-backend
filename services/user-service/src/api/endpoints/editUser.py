import httpx
import boto3
import os
import datetime
from fastapi import APIRouter, Response, Request, Response, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict
from src.grpc.grpc_client import *
from src.grpc import hyper_pb2 as hyper_pb2

router = APIRouter()

# @router.post('/username') # DEPRICATED
async def update_username(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    if not body.get('username'):
        raise HTTPException(status_code=400, detail={'Bad Request'})
    update, error = updateUsername(request.headers.get("X-User-ID"), body.get('username'))
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update

# @router.post('/email') # DEPRICATED
async def update_email(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    if not body.get('email'):
        raise HTTPException(status_code=400, detail={'Bad Request'})
    update, error = updateEmail(request.headers.get("X-User-ID"), body.get('email'))
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update

# @router.post('/first_name') # DEPRICATED
async def update_firstname(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    if not body.get('first_name'):
        raise HTTPException(status_code=400, detail={'Bad Request'})
    update, error = updateFirstname(request.headers.get("X-User-ID"), body.get('first_name'))
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update

# @router.post('/last_name') # DEPRICATED
async def update_lastname(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    if not body.get('last_name'):
        raise HTTPException(status_code=400, detail={'Bad Request'})
    update, error = updateLastname(request.headers.get("X-User-ID"), body.get('last_name'))
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update

@router.post('/data')
async def update_user_data(request: Request):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    
    update = None

    if body.get('username'):
        update, error = updateUsername(request.headers.get("X-User-ID"), body.get('username'))
        if update is None:
            print('[Profile Router] update failed')
            raise HTTPException(status_code=400, detail={ "error": error.details() })
    
    if body.get('first_name'):
        update, error = updateFirstname(request.headers.get("X-User-ID"), body.get('first_name'))
        if update is None:
            print('[Profile Router] update failed')
            raise HTTPException(status_code=400, detail={ "error": error.details() })
    
    if body.get('last_name'):
        update, error = updateLastname(request.headers.get("X-User-ID"), body.get('last_name'))
        if update is None:
            print('[Profile Router] update failed')
            raise HTTPException(status_code=400, detail={ "error": error.details() })
    
    if body.get('email'):
        update, error = updateEmail(request.headers.get("X-User-ID"), body.get('email'))
        if update is None:
            print('[Profile Router] update failed')
            raise HTTPException(status_code=400, detail={ "error": error.details() })

    if update is not None:
        update = MessageToDict(update, preserving_proto_field_name=True)

    return update

@router.post('/passwd')
async def update_password(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    try:
        body = await request.json()
    except Exception as e:
        print(f'[Profile Router] Failed to parse body: {e}')
        raise HTTPException(status_code=400, detail={'Bad Request'})
    if not body.get('old_password') or not body.get('new_password'):
        raise HTTPException(status_code=400, detail={'Bad Request'})
    update, error = updatePassword(request.headers.get("X-User-ID"), body.get('old_password'), body.get('new_password'))
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update

@router.post('/picture')
async def update_picture(request: Request, response: Response, picture: UploadFile = File(...),):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return Response(status_code=403, content='Forbidden')
    if picture.content_type != 'image/jpeg' and picture.content_type != 'image/png':
        raise HTTPException(status_code=400, detail={ "error": "Invalid Type File" })
    picture_content = await picture.read()
    try:
        s3 = boto3.client(
            's3', aws_access_key_id = os.getenv('AWS_KEY'),
            aws_secret_access_key = os.getenv('AWS_SECRET'))
        s3_key = f'avatars/{datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")}_{user_id}_avatar.jpg'
        s3.put_object(Bucket='hyperrrr-bucket', Key=s3_key, Body=picture_content)
        picture_url = f"{os.getenv('S3_bucket')}/{s3_key}"
    except Exception as e:
        print('[Profile Router] s3 upload failed', e)
        raise HTTPException(status_code=400, detail={ "error": "s3 upload failed" })
    update, error = updatePicture(user_id, picture_url)
    if update is None:
        print('[Profile Router] update failed')
        raise HTTPException(status_code=400, detail={ "error": error.details() })
    update = MessageToDict(update, preserving_proto_field_name=True)
    return update
