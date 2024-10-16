import grpc
import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc

def getUserById(id: str):
    with grpc.insecure_channel('auth-service:50051') as channel:
        stub = user_pb2_grpc.getUserStub(channel)
        req = user_pb2.getUserRequest(id=id)
        res = stub.getUserService(req)
        return res

def updateUser(id: str):
    with grpc.insecure_channel('auth-service:50051') as channel:
        stub = user_pb2_grpc.updateUserStub(channel)
        req = user_pb2.updateUserRequest(id=id)
        res = stub.updateUserService(req)
        return res