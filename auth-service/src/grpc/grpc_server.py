import src.grpc.user_pb2 as user_pb2
import src.grpc.user_pb2_grpc as user_pb2_grpc
import grpc
from concurrent import futures
from src.database.db import get_user_by_id, update_username, update_email, update_firstname, update_lastname, search_users
import asyncio

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
        user_response = user_dict_to_pb2_user(user)
        return user_pb2.getUserResponse(user=user_response)

class updateUsernameServicer(user_pb2_grpc.updateUsernameServicer):
    def updateUsernameService(self, request, context):
        if not request.id or not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateUsernameResponse()
        user = asyncio.run(update_username(request.id, request.username))
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateUsernameResponse()
        user_response = user_dict_to_pb2_user(user)
        return user_pb2.updateUsernameResponse(user=user_response)

class updateEmailServicer(user_pb2_grpc.updateEmailServicer):
    def updateEmailService(self, request, context):
        if not request.id or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateEmailResponse()
        user = asyncio.run(update_email(request.id, request.email))
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateEmailResponse()
        user_response = user_dict_to_pb2_user(user)
        return user_pb2.updateEmailResponse(user=user_response)

class updateFirstnameServicer(user_pb2_grpc.updateFirstnameServicer):
    def updateFirstnameService(self, request, context):
        if not request.id or not request.first_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateFirstnameResponse()
        user = asyncio.run(update_firstname(request.id, request.first_name))
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateFirstnameResponse()
        user_response = user_dict_to_pb2_user(user)
        return user_pb2.updateFirstnameResponse(user=user_response)

class updateLastnameServicer(user_pb2_grpc.updateLastnameServicer):
    def updateLastnameService(self, request, context):
        if not request.id or not request.last_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateLastnameResponse()
        user = asyncio.run(update_lastname(request.id, request.last_name))
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateLastnameResponse()
        user_response = user_dict_to_pb2_user(user)
        return user_pb2.updateLastnameResponse(user=user_response)

class searchUsersServicer(user_pb2_grpc.searchUsersServicer):
    def searchUsersService(self, request, context):
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.searchUsersResponse()
            # return None???
        users_data = asyncio.run(search_users(request.query))
        results = []
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
        return user_pb2.searchUsersResponse(users=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    user_pb2_grpc.add_getUserServicer_to_server(getUserServicer(), server)
    user_pb2_grpc.add_updateUsernameServicer_to_server(updateUsernameServicer(), server)
    user_pb2_grpc.add_updateEmailServicer_to_server(updateEmailServicer(), server)
    user_pb2_grpc.add_updateFirstnameServicer_to_server(updateFirstnameServicer(), server)
    user_pb2_grpc.add_updateLastnameServicer_to_server(updateLastnameServicer(), server)
    user_pb2_grpc.add_searchUsersServicer_to_server(searchUsersServicer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()