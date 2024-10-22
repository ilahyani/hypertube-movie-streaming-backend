import grpc, os
import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

#TODO: Put grpc server name and port in env

def addUser(user):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.addUserStub(channel)
        req = user_pb2.addUserRequest(user=user)
        try:
            res = stub.addUserService(req)
        except Exception as e:
            print(f'[gRPC Client] method getUserById Failed: {e}')
            return None, e
        return res, None