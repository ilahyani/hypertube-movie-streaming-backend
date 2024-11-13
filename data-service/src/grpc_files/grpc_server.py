from dotenv import load_dotenv
from concurrent import futures
import grpc_files.user_pb2 as user_pb2
import grpc_files.user_pb2_grpc as user_pb2_grpc
import grpc
import asyncio
import database.db as db
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='hyper.log', encoding='utf-8', level=logging.DEBUG)

#TODO: did too many copy pasta double check req and res objects

def user_dict_to_pb2_user(user_dict):
    return user_pb2.User(
        id=user_dict['id'],
        email=user_dict['email'],
        username=user_dict['username'],
        first_name=user_dict['first_name'],
        last_name=user_dict['last_name'],
        picture=user_dict['picture'],
    )

class getUserServicer(user_pb2_grpc.getUserServicer):
    async def getUserService(self, request, context):
        logger.info(f'Received getUserService request: {request}')
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('id is required to fetch the user')
            return user_pb2.getUserResponse()
        user = await db.get_user_by_id(request.id)
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid user id')
            return user_pb2.getUserResponse()
        logger.info(f'get_user_by_id: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'getUserService succeeded: {user_response}')
        return user_pb2.getUserResponse(user=user_response)

class updateUsernameServicer(user_pb2_grpc.updateUsernameServicer):
    async def updateUsernameService(self, request, context):
        logger.info(f'Received updateUsernameService request: {request}')
        if not request.id or not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateUsernameResponse()
        try:
            user = await db.update_username(request.id, request.username)
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'Failed to update username: {e}')
            return user_pb2.getUserResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateUsernameResponse()
        logger.info(f'update_username: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateUsernameService succeeded: {user_response}')
        return user_pb2.updateUsernameResponse(user=user_response)

class updateEmailServicer(user_pb2_grpc.updateEmailServicer):
    async def updateEmailService(self, request, context):
        logger.info(f'Received updateEmailServicer request: {request}')
        if not request.id or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateEmailResponse()
        user = await db.update_email(request.id, request.email)
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateEmailResponse()
        logger.info(f'updateEmailService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateEmailService succeeded: {user_response}')
        return user_pb2.updateEmailResponse(user=user_response)

class updateFirstnameServicer(user_pb2_grpc.updateFirstnameServicer):
    async def updateFirstnameService(self, request, context):
        logger.info(f'Received updateFirstnameServicer request: {request}')
        if not request.id or not request.first_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateFirstnameResponse()
        user = await db.update_firstname(request.id, request.first_name)
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateFirstnameResponse()
        logger.info(f'updateFirstnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateFirstnameService succeeded: {user_response}')
        return user_pb2.updateFirstnameResponse(user=user_response)

class updateLastnameServicer(user_pb2_grpc.updateLastnameServicer):
    async def updateLastnameService(self, request, context):
        logger.info(f'Received updateLastnameService request: {request}')
        if not request.id or not request.last_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateLastnameResponse()
        user = await update_lastname(request.id, request.last_name)
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateLastnameResponse()
        logger.info(f'updateLastnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateLastnameService succeeded: {user_response}')
        return user_pb2.updateLastnameResponse(user=user_response)

class searchUsersServicer(user_pb2_grpc.searchUsersServicer):
    async def searchUsersService(self, request, context):
        logger.info(f'Received searchUsersServicer request: {request}')
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.searchUsersResponse()
        users_data = await db.search_users(request.query)
        logger.info(f'search_users: {user}')
        results = []
        try:
            for user in users_data:
                user_message = user_pb2.User(
                    id=user[0],
                    email=None,
                    username=user[2],
                    first_name=user[3],
                    last_name=user[4],
                    picture=user[6],
                )
                results.append(user_message)
            logger.info(f'searchUsersService succeeded: {results}')
            return user_pb2.searchUsersResponse(users=results)
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'searchUsersService Failed: {e}')
            return user_pb2.getUserResponse()

class addUserServicer(user_pb2_grpc.addUserServicer):
    def addUserService(self, request, context):
        logger.info(f'Received addUserServicer request: {request}')
        if not request.user:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.addUserResponse()
        if request.oauth_id:
            query = "SELECT * FROM users WHERE oauth_id = %s ;"
            user_data = asyncio.run(db.fetch_db(query, (request.oauth_id, )))
            if user_data is not None:
                user = db.get_user_dict(user_data)
                del user['passwd'], user['oauth_id']
                return user_pb2.addUserResponse(user=user)
        res = asyncio.run(db.add_user_to_db({
            'email': request.user.email,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'picture': request.user.picture,
        }, request.oauth_id))
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.addUserResponse()
        logger.info(f'add_user_to_db: {res}')
        user = user_dict_to_pb2_user(res)
        logger.info(f'addUserService succeeded: {user}')
        return user_pb2.addUserResponse(user=user)

class signupServicer(user_pb2_grpc.signupServicer):
    def signupService(self, request, context):
        logger.info(f'Received signupServicer request: {request}')
        if not request.user:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.signupResponse()
        res = asyncio.run(db.add_user_to_db({
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'username': request.user.username,
            'passwd': request.user.passwd,
            'picture': request.user.picture,
        }))
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.signupResponse()
        logger.info(f'add_user_to_db: {res}')
        user = user_dict_to_pb2_user(res)
        logger.info(f'signupServicer succeeded: {user}')
        return user_pb2.signupResponse(user=user)

class loginServicer(user_pb2_grpc.loginServicer):
    def loginService(self, request, context):
        logger.info(f'Received loginServicer request: {request}')
        if not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.loginResponse()
        res = asyncio.run(db.get_user_by_username(request.username))
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.loginResponse()
        logger.info(f'get_user_by_username: {res}')
        # user = user_dict_to_pb2_user(res)
        user = user_pb2.Login_User(
            id=res['id'],
            email=res['email'],
            username=res['username'],
            first_name=res['first_name'],
            last_name=res['last_name'],
            passwd=res['passwd'],
            picture=res['picture'],
        )
        logger.info(f'loginService succeeded: {user}')
        return user_pb2.loginResponse(user=user)

def serve():

    server = grpc.server(futures.ThreadPoolExecutor())

    user_pb2_grpc.add_getUserServicer_to_server(getUserServicer(), server)
    user_pb2_grpc.add_updateUsernameServicer_to_server(updateUsernameServicer(), server)
    user_pb2_grpc.add_updateEmailServicer_to_server(updateEmailServicer(), server)
    user_pb2_grpc.add_updateFirstnameServicer_to_server(updateFirstnameServicer(), server)
    user_pb2_grpc.add_updateLastnameServicer_to_server(updateLastnameServicer(), server)
    user_pb2_grpc.add_searchUsersServicer_to_server(searchUsersServicer(), server)
    user_pb2_grpc.add_addUserServicer_to_server(addUserServicer(), server)
    user_pb2_grpc.add_signupServicer_to_server(signupServicer(), server)
    user_pb2_grpc.add_loginServicer_to_server(loginServicer(), server)

    #TODO: grpc port env variable
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server started on 50051')
    server.wait_for_termination()