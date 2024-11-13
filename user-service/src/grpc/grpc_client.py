import grpc, os
import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

def getUserById(id: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.getUserStub(channel)
        req = user_pb2.getUserRequest(id=id)
        try:
            res = stub.getUserService(req)
        except Exception as e:
            print(f'[gRPC Client] method getUserById Failed: {e}')
            return None, e
        return res, None

def updateUsername(id: str, username: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.updateUsernameStub(channel)
        req = user_pb2.updateUsernameRequest(id=id, username=username)
        try:
            res = stub.updateUsernameService(req)
        except Exception as e:
            print(f'[gRPC Client] method updateUsername Failed: {e}')
            return None, e
        return res, None

def updateEmail(id: str, email: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.updateEmailStub(channel)
        req = user_pb2.updateEmailRequest(id=id, email=email)
        try:
            res = stub.updateEmailService(req)
        except Exception as e:
            print(f'[gRPC Client] method updateEmail Failed: {e}')
            return None, e
        return res, None

def updateFirstname(id: str, first_name: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.updateFirstnameStub(channel)
        req = user_pb2.updateFirstnameRequest(id=id, first_name=first_name)
        try:
            res = stub.updateFirstnameService(req)
        except Exception as e:
            print(f'[gRPC Client] method updateFirstname Failed: {e}')
            return None, e
        return res, None

def updateLastname(id: str, last_name: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.updateLastnameStub(channel)
        req = user_pb2.updateLastnameRequest(id=id, last_name=last_name)
        try:
            res = stub.updateLastnameService(req)
        except Exception as e:
            print(f'[gRPC Client] method updateLastname Failed: {e}')
            return None, e
        return res, None

def searchUsers(query: str):
    with grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') as channel:
        stub = user_pb2_grpc.searchUsersStub(channel)
        req = user_pb2.searchUsersRequest(query=query)
        try:
            res = stub.searchUsersService(req)
        except Exception as e:
            print(f'[gRPC Client] method searchUsers Failed: {e}')
            return None, e
        return res, None
