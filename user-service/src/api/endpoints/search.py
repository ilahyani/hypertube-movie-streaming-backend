from fastapi import APIRouter, Response, Request
from google.protobuf.json_format import MessageToDict
from src.grpc.grpc_client import searchUsers
from src.grpc import user_pb2 as user_pb2
from google.protobuf.json_format import MessageToDict

router = APIRouter()

@router.get('/')
async def user_search(query: str, request: Request, respose: Response):
    if not query:
        return Response(status_code=400, content='Bad Request')
    results, error = searchUsers(query)
    if results is None:
        print('[Search Router] search failed')
        return Response(status_code=400, content=f'Bad Request: {error.details()}')
    return MessageToDict(results, preserving_proto_field_name=True)