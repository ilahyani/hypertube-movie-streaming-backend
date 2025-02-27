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

def updateUsername(id: str, username: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updateUsernameRequest(id=id, username=username)
    try:
        res = stub.updateUsernameService(req)
    except Exception as e:
        print(f'[gRPC Client] method updateUsername Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def updateEmail(id: str, email: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updateEmailRequest(id=id, email=email)
    try:
        res = stub.updateEmailService(req)
    except Exception as e:
        print(f'[gRPC Client] method updateEmail Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def updateFirstname(id: str, first_name: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updateFirstnameRequest(id=id, first_name=first_name)
    try:
        res = stub.updateFirstnameService(req)
    except Exception as e:
        print(f'[gRPC Client] method updateFirstname Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def updateLastname(id: str, last_name: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updateLastnameRequest(id=id, last_name=last_name)
    try:
        res = stub.updateLastnameService(req)
    except Exception as e:
        print(f'[gRPC Client] method updateLastname Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def updatePicture(id: str, picture: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updatePictureRequest(id=id, picture=picture)
    try:
        res = stub.updatePictureService(req)
    except Exception as e:
        print(f'[gRPC Client] method updatePicture Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def updatePassword(id: str, old_password: str, new_password: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.updatePasswordRequest(id=id, old_password=old_password, new_password=new_password)
    try:
        res = stub.updatePasswordService(req)
    except Exception as e:
        print(f'[gRPC Client] method updatePassword Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def searchUsers(query: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.searchUsersRequest(query=query)
    try:
        res = stub.searchUsersService(req)
    except Exception as e:
        print(f'[gRPC Client] method searchUsers Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None
