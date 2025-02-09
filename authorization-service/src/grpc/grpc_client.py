import grpc, os
import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 

def getUserById(id: str):
    stub = user_pb2_grpc.getUserStub(channel)
    req = user_pb2.getUserRequest(id=id)
    try:
        res = stub.getUserService(req)
    except Exception as e:
        print(f'[gRPC Client] method getUserById Failed: {e}')
        return None, e
    return res, None
