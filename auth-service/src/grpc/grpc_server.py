import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
import grpc
from concurrent import futures
from src.database.db import get_user_by_id
import asyncio

class GetUserServicer(user_pb2_grpc.getUserServicer):
    def getUserService(self, request, context):
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('id is required to fetch the user')
            return user_pb2.getUserResponse()
        user = asyncio.run(get_user_by_id(request.id))
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid user id')
            return user_pb2.getUserResponse()
        user_response = user_pb2.User(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            picture=user['picture'],
        )
        return user_pb2.getUserResponse(user=user_response)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    user_pb2_grpc.add_getUserServicer_to_server(GetUserServicer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    print('STARTED SERVER ON 50051')
    server.wait_for_termination()