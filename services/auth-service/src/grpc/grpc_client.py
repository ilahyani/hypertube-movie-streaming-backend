import grpc, os
import src.grpc.hyper_pb2 as hyper_pb2
import src.grpc.hyper_pb2_grpc as hyper_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

def addUser(user, oauth_id):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 
    stub = hyper_pb2_grpc.AuthServiceStub(channel)
    user_req = hyper_pb2.User(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        first_name=user['first_name'],
        last_name=user['last_name'],
        picture=user['picture'],
    )
    req = hyper_pb2.addUserRequest(user=user_req, oauth_id=oauth_id)
    try:
        res = stub.addUserService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method addUser Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def signup(user):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 
    stub = hyper_pb2_grpc.AuthServiceStub(channel)
    user_req = hyper_pb2.Signup_User(
        email = user['email'],
        first_name = user['first_name'],
        last_name = user['last_name'],
        username = user['username'],
        passwd = user['passwd'],
        picture = user['picture'],
    )
    req = hyper_pb2.signupRequest(user=user_req)
    try:
        res = stub.signupService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method signup Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def login_user(username):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 
    stub = hyper_pb2_grpc.AuthServiceStub(channel)
    req = hyper_pb2.loginRequest(username=username)
    try:
        res = stub.loginService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method login Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

def getUserByEmail(email: str):
    channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}')
    stub = hyper_pb2_grpc.UserServiceStub(channel)
    req = hyper_pb2.getUserByEmailRequest(email=email)
    try:
        res = stub.getUserByEmailService(req)
    except Exception as e:
        print(f'[gRPC Client] method getUserByEmail Failed: {e}')
        channel.close()
        return None, e
    channel.close()
    return res, None

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