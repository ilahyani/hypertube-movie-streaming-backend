from dotenv import load_dotenv
from concurrent import futures
import grpc_files.user_pb2 as user_pb2
import grpc_files.user_pb2_grpc as user_pb2_grpc
import grpc
import asyncio
import database.db as db
import logging
import os

load_dotenv()

logging.basicConfig(filename='hyper.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.info(f'Received getUserService request: {request}')
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('id is required to fetch the user')
            return user_pb2.getUserResponse()
        try:
            user = asyncio.run(db.get_user_by_id(request.id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[getUserService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.getUserResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid user id')
            return user_pb2.getUserResponse()
        logger.info(f'get_user_by_id: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'getUserService succeeded: {user_response}')
        return user_pb2.getUserResponse(user=user_response)

class updateUsernameServicer(user_pb2_grpc.updateUsernameServicer):
    def updateUsernameService(self, request, context):
        logger.info(f'Received updateUsernameService request: {request}')
        if not request.id or not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateUsernameResponse()
        try:
            user = asyncio.run(db.update_username(request.id, request.username))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateUsernameService] database exception: {e}')
            logger.info(f'database exception: {e}')
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
    def updateEmailService(self, request, context):
        logger.info(f'Received updateEmailServicer request: {request}')
        if not request.id or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateEmailResponse()
        try:
            user = asyncio.run(db.update_email(request.id, request.email))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateEmailService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.updateEmailResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateEmailResponse()
        logger.info(f'updateEmailService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateEmailService succeeded: {user_response}')
        return user_pb2.updateEmailResponse(user=user_response)

class updateFirstnameServicer(user_pb2_grpc.updateFirstnameServicer):
    def updateFirstnameService(self, request, context):
        logger.info(f'Received updateFirstnameServicer request: {request}')
        if not request.id or not request.first_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateFirstnameResponse()
        try:
            user = asyncio.run(db.update_firstname(request.id, request.first_name))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateFirstnameService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.updateFirstnameResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateFirstnameResponse()
        logger.info(f'updateFirstnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateFirstnameService succeeded: {user_response}')
        return user_pb2.updateFirstnameResponse(user=user_response)

class updateLastnameServicer(user_pb2_grpc.updateLastnameServicer):
    def updateLastnameService(self, request, context):
        logger.info(f'Received updateLastnameService request: {request}')
        if not request.id or not request.last_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.updateLastnameResponse()
        try:
            user = asyncio.run(db.update_lastname(request.id, request.last_name))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateLastnameService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.updateLastnameResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return user_pb2.updateLastnameResponse()
        logger.info(f'updateLastnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateLastnameService succeeded: {user_response}')
        return user_pb2.updateLastnameResponse(user=user_response)

class searchUsersServicer(user_pb2_grpc.searchUsersServicer):
    def searchUsersService(self, request, context):
        logger.info(f'Received searchUsersServicer request: {request}')
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.searchUsersResponse()
        try:
            users_data = asyncio.run(db.search_users(request.query))
            if users_data is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Operation Failed')
                return user_pb2.searchUsersResponse()
            logger.info(f'search_users: {users_data}')
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
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[searchUsersService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.searchUsersResponse()
        logger.info(f'searchUsersService succeeded: {results}')
        return user_pb2.searchUsersResponse(users=results)

class addUserServicer(user_pb2_grpc.addUserServicer):
    def addUserService(self, request, context):
        logger.info(f'Received addUserServicer request: {request}')
        if not request.user:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return user_pb2.addUserResponse()
        if request.oauth_id:
            query = "SELECT * FROM Users WHERE oauth_id = %s ;"
            user_data = asyncio.run(db.fetch_db(query, (request.oauth_id, )))
            if user_data is not None:
                user = db.get_user_dict(user_data)
                del user['passwd'], user['oauth_id']
                return user_pb2.addUserResponse(user=user)
        try:
            res = asyncio.run(db.add_user_to_db({
                'email': request.user.email,
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'picture': request.user.picture,
            }, request.oauth_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[addUserServicer] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.addUserResponse()
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
        try:
            res = asyncio.run(db.add_user_to_db({
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'username': request.user.username,
                'passwd': request.user.passwd,
                'picture': request.user.picture,
            }))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[signupService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.signupResponse()
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
        try:
            user = user_pb2.Login_User(
                id=res['id'],
                email=res['email'],
                username=res['username'],
                first_name=res['first_name'],
                last_name=res['last_name'],
                passwd=res['passwd'],
                picture=res['picture'],
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[loginServicer] database exception: {e}')
            logger.info(f'database exception: {e}')
            return user_pb2.loginResponse()
        logger.info(f'loginService succeeded: {user}')
        return user_pb2.loginResponse(user=user)

class MovieServiceServicer(user_pb2_grpc.MovieServiceServicer):
    def addMovie(self, request, context):
        if not request.user_id or not request.movie_id or not request.download_path:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return user_pb2.movieResponse()
        try:
            res = asyncio.run(db.add_movie(request.movie_id, request.user_id, request.download_path))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return user_pb2.movieResponse()
        if not res:
            return user_pb2.movieResponse()
        logger.info(f'addMovie request success: {res}')
        return user_pb2.movieResponse(movie=user_pb2.Movie(
            id = res['id'],
            last_watched =  res['last_watched'],
            watched = res['watched'],
            downloaded = res['downloaded'],
            download_path = res['download_path'],
        ))
    
    def getMovie(self, request, context):
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return user_pb2.movieResponse()
        try:
            res = asyncio.run(db.get_movie(request.movie_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return user_pb2.movieResponse()
        if not res:
            return user_pb2.movieResponse()
        logger.info(f'getMovie request success: {res}')
        return user_pb2.movieResponse(movie=user_pb2.Movie(
            id = res['id'],
            last_watched =  res['last_watched'],
            watched = res['watched'],
            downloaded = res['downloaded'],
            download_path = res['download_path'],
        ))
    
    def getUserMovies(self, request, context):
        logger.info(f'getUserMovies request: {request.movie_ids}')
        logger.info(f'movie_ids list {list(request.movie_ids)}')
        if not request.movie_ids or not request.user_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return user_pb2.getUserMoviesResponse()
        try:
            movies = asyncio.run(db.get_user_movies(list(request.movie_ids), request.user_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return user_pb2.getUserMoviesResponse()
        logger.info(f'getUserMovies request success: {movies}')
        results = []
        for movie in movies:
            results.append(movie[0])
        logger.info(f'results {results}')
        return user_pb2.getUserMoviesResponse(movie_ids=results)

class CommentServiceServicer(user_pb2_grpc.CommentServiceServicer):
    def addComment(self, request, context):
        logger.info(f'addComment request: {request}')
        if not request.movie_id or not request.author_id or not request.comment:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return user_pb2.addCommentResponse()
        try:
            res = asyncio.run(db.add_comment(request.movie_id, request.author_id, request.comment))
            logger.info(f'add_comment res: {res}')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return user_pb2.addCommentResponse()
        logger.info(f'addComment request success')
        return user_pb2.addCommentResponse(success=True)

    def getComments(self, request, context):
        logger.info(f'getComments request: {request}')
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return user_pb2.getCommentsResponse()
        try:
            comments = asyncio.run(db.get_comments(request.movie_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return user_pb2.getCommentsResponse()
        if not comments or len(comments) == 0:
            return user_pb2.getCommentsResponse()
        results = []
        for comment in comments:
            _comment = user_pb2.Comment(
                id = comment[0],
                author_id = comment[1],
                movie_id = comment[2],
                date = comment[3],
                comment = comment[4]
            )
            results.append(_comment)
        logger.info(f'getComments request success: {results}')
        return user_pb2.getCommentsResponse(comments=results)

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    user_pb2_grpc.add_getUserServicer_to_server(getUserServicer(), server)
    user_pb2_grpc.add_updateUsernameServicer_to_server(updateUsernameServicer(), server)
    user_pb2_grpc.add_updateEmailServicer_to_server(updateEmailServicer(), server)
    user_pb2_grpc.add_updateFirstnameServicer_to_server(updateFirstnameServicer(), server)
    user_pb2_grpc.add_updateLastnameServicer_to_server(updateLastnameServicer(), server)
    user_pb2_grpc.add_searchUsersServicer_to_server(searchUsersServicer(), server)
    user_pb2_grpc.add_addUserServicer_to_server(addUserServicer(), server)
    user_pb2_grpc.add_signupServicer_to_server(signupServicer(), server)
    user_pb2_grpc.add_loginServicer_to_server(loginServicer(), server)
    user_pb2_grpc.add_MovieServiceServicer_to_server(MovieServiceServicer(), server)
    user_pb2_grpc.add_CommentServiceServicer_to_server(CommentServiceServicer(), server)

    server.add_insecure_port(f'[::]:{os.getenv('GRPC_SERVER_PORT')}')
    server.start()
    logger.info(f'gRPC server started on {os.getenv('GRPC_SERVER_PORT')}')
    server.wait_for_termination()
