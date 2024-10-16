from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict
from src.grpc.grpc_client import getUserById
from src.grpc import user_pb2 as user_pb2

router = APIRouter()

@router.get('/public')
async def get_public_profile(id: str, request: Request, response: Response):
    if not id:
        return HTTPException(status_code=403, detail={'error', 'Forbidden'})
    user = getUserById(id)
    if user is None:
        print('user not found')
        return HTTPException(status_code=400, detail={'error': 'Bad Request'})
    # print('protobuf', user)
    user = MessageToDict(user, preserving_proto_field_name=True)
    del user['user']['email']
    return user

@router.get('/private')
async def get_private_profile(request: Request, response: Response):
    if not request.state.user_id:
        return HTTPException(status_code=403, detail={'error', 'Forbidden'})
    user = getUserById(request.state.user_id)
    if user is None:
        print('user not found')
        return HTTPException(status_code=400, detail={'error': 'Bad Request'})
    # print('protobuf', user)
    user = MessageToDict(user, preserving_proto_field_name=True)
    return user

@router.post('/update/username')
async def update_username(request: Request, response: Response):
    if not request.state.user_id:
        return HTTPException(status_code=403, detail={'error', 'Forbidden'})
    body = request.body.json()
    if not body.username:
        return HTTPException(status_code=400, detail={'error', 'Bad Request'})
    # [regenerate rpc shit]
    # [call grpc method with request.state.user_id AND body.username]

@router.post('/update/avatar')
async def update_profile_data(request: Request, response: Response):
    # [call grpc method]
    avatar = ''
    return avatar