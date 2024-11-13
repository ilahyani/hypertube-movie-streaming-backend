import grpc, os
import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

channel = grpc.insecure_channel(f'{os.getenv('GRPC_SERVER_HOST')}:{os.getenv('GRPC_SERVER_PORT')}') 

def addUser(user, oauth_id):
    stub = user_pb2_grpc.addUserStub(channel)
    user_req = user_pb2.User(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        first_name=user['first_name'],
        last_name=user['last_name'],
        picture=user['picture'],
    )
    req = user_pb2.addUserRequest(user=user_req, oauth_id=oauth_id)
    try:
        res = stub.addUserService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method addUser Failed: {e}')
        return None, e
    return res, None

def signup(user):
    stub = user_pb2_grpc.signupStub(channel)
    user_req = user_pb2.Signup_User(
        email = user['email'],
        first_name = user['first_name'],
        last_name = user['last_name'],
        username = user['username'],
        passwd = user['passwd'],
        picture = user['picture'],
    )
    req = user_pb2.signupRequest(user=user_req)
    try:
        res = stub.signupService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method signup Failed: {e}')
        return None, e
    return res, None

def login_user(username):
    stub = user_pb2_grpc.loginStub(channel)
    req = user_pb2.loginRequest(username=username)
    try:
        res = stub.loginService(req)
    except Exception as e:
        print(f'[gRPC auth Client] method login Failed: {e}')
        return None, e
    return res, None