from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict
from src.grpc.grpc_client import getUserById
from src.grpc import user_pb2 as user_pb2

router = APIRouter()

@router.get('/public')
async def get_public_profile(id: str, request: Request, response: Response):
    if not id:
        return Response(status_code=403, content='Forbidden')
    user, error = getUserById(id)
    if user is None:
        print('[Profile Router] user not found')
        return Response(status_code=400, content=f'Bad Request: {error.details()}')
    user = MessageToDict(user, preserving_proto_field_name=True)
    del user['user']['email']
    return user

@router.get('/private')
async def get_private_profile(request: Request, response: Response):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')
    user, error = getUserById(request.headers.get("X-User-ID"))
    if user is None:
        print('[Profile Router] user not found')
        return Response(status_code=400, content=f'Bad Request: {error.details()}')
    user = MessageToDict(user, preserving_proto_field_name=True)
    return user
