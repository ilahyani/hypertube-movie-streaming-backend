import grpc, os
import src.grpc.hyper_pb2 as hyper_pb2
import src.grpc.hyper_pb2_grpc as hyper_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

def getUserById(id: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.getUserRequest(id=id)
    try:
        res = stub.getUserService(req)
    except Exception as e:
        print(f'[gRPC Client] method getUserById Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None
