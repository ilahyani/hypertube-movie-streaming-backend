from dotenv import load_dotenv
from concurrent import futures
import grpc_files.hyper_pb2 as hyper_pb2
import grpc_files.hyper_pb2_grpc as hyper_pb2_grpc
import grpc
import asyncio
import database.db as db
import logging
import os

load_dotenv()

logging.basicConfig(filename='hyper.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def user_dict_to_pb2_user(user_dict):
    return hyper_pb2.User(
        id=user_dict['id'],
        email=user_dict['email'],
        username=user_dict['username'],
        first_name=user_dict['first_name'],
        last_name=user_dict['last_name'],
        picture=user_dict['picture'],
    )

class UserServiceServicer(hyper_pb2_grpc.UserServiceServicer):
    def getUserService(self, request, context):
        logger.info(f'Received getUserService request: {request}')
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('id is required to fetch the user')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.get_user_by_id(request.id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[getUserService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.userResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid user id')
            return hyper_pb2.userResponse()
        logger.info(f'get_user_by_id: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'getUserService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)

    def searchUsersService(self, request, context):
        logger.info(f'Received searchUsersServicer request: {request}')
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.searchUsersResponse()
        try:
            users_data = asyncio.run(db.search_users(request.query))
            if users_data is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Operation Failed')
                return hyper_pb2.searchUsersResponse()
            logger.info(f'search_users: {users_data}')
            results = []
            for user in users_data:
                user_message = hyper_pb2.User(
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
            return hyper_pb2.searchUsersResponse()
        logger.info(f'searchUsersService succeeded: {results}')
        return hyper_pb2.searchUsersResponse(users=results)
    
    def updateUsernameService(self, request, context):
        logger.info(f'Received updateUsernameService request: {request}')
        if not request.id or not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.update_username(request.id, request.username))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateUsernameService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.getUserResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.userResponse()
        logger.info(f'update_username: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateUsernameService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)

    def updateEmailService(self, request, context):
        logger.info(f'Received updateEmailServicer request: {request}')
        if not request.id or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.update_email(request.id, request.email))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateEmailService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.userResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.userResponse()
        logger.info(f'updateEmailService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateEmailService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)

    def updateFirstnameService(self, request, context):
        logger.info(f'Received updateFirstnameServicer request: {request}')
        if not request.id or not request.first_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.update_firstname(request.id, request.first_name))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateFirstnameService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.userResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.userResponse()
        logger.info(f'updateFirstnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateFirstnameService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)

    def updateLastnameService(self, request, context):
        logger.info(f'Received updateLastnameService request: {request}')
        if not request.id or not request.last_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.update_lastname(request.id, request.last_name))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updateLastnameService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.userResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.userResponse()
        logger.info(f'updateLastnameService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updateLastnameService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)
    
    def updatePasswordService(self, request, context):
        logger.info(f'Received updatePasswordService request: {request}')
        if not request.id or not request.old_password or not request.new_password:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.userResponse()
        try:
            user = asyncio.run(db.update_password(request.id, request.old_password, request.new_password))
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'[updatePasswordService] database exception: {e}')
            logger.info(f'database exception: {e}')
            return hyper_pb2.userResponse()
        if user is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.userResponse()
        logger.info(f'updatePasswordService: {user}')
        user_response = user_dict_to_pb2_user(user)
        logger.info(f'updatePasswordService succeeded: {user_response}')
        return hyper_pb2.userResponse(user=user_response)

class AuthServiceServicer(hyper_pb2_grpc.AuthServiceServicer):
    def loginService(self, request, context):
        logger.info(f'Received loginService request: {request}')
        if not request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.loginResponse()
        res = asyncio.run(db.get_user_by_username(request.username))
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.loginResponse()
        logger.info(f'get_user_by_username: {res}')
        try:
            user = hyper_pb2.Login_User(
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
            return hyper_pb2.loginResponse()
        logger.info(f'loginService succeeded: {user}')
        return hyper_pb2.loginResponse(user=user)
    
    def signupService(self, request, context):
        logger.info(f'Received signupServicer request: {request}')
        if not request.user:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.signupResponse()
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
            return hyper_pb2.signupResponse()
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.signupResponse()
        logger.info(f'add_user_to_db: {res}')
        user = user_dict_to_pb2_user(res)
        logger.info(f'signupServicer succeeded: {user}')
        return hyper_pb2.signupResponse(user=user)
    
    def addUserService(self, request, context):
        logger.info(f'Received addUserServicer request: {request}')
        if not request.user:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: missing data')
            return hyper_pb2.addUserResponse()
        if request.oauth_id:
            query = "SELECT * FROM Users WHERE oauth_id = %s ;"
            user_data = asyncio.run(db.fetch_db(query, (request.oauth_id, )))
            if user_data is not None:
                user = db._convert_to_user_dict(user_data)
                del user['passwd'], user['oauth_id']
                return hyper_pb2.addUserResponse(user=user)
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
            return hyper_pb2.addUserResponse()
        if res is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: invalid data')
            return hyper_pb2.addUserResponse()
        logger.info(f'add_user_to_db: {res}')
        user = user_dict_to_pb2_user(res)
        logger.info(f'addUserService succeeded: {user}')
        return hyper_pb2.addUserResponse(user=user)

class MovieServiceServicer(hyper_pb2_grpc.MovieServiceServicer):
    def addMovie(self, request, context):
        if not request.user_id or not request.movie_id or not request.download_path or not request.file_size:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.movieResponse()
        try:
            res = asyncio.run(db.add_movie(request.movie_id, request.user_id, request.download_path, request.file_size))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.movieResponse()
        if not res:
            return hyper_pb2.movieResponse()
        logger.info(f'addMovie request success: {res}')
        return hyper_pb2.movieResponse(movie=hyper_pb2.Movie(
            id = res['id'],
            last_watched =  res['last_watched'],
            watched = res['watched'],
            downloaded = res['downloaded'],
            download_path = res['download_path'],
            file_size = res['file_size'],
        ))
    
    def getMovie(self, request, context):
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.movieResponse()
        try:
            res = asyncio.run(db.get_movie(request.movie_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.movieResponse()
        if not res:
            return hyper_pb2.movieResponse()
        logger.info(f'getMovie request success: {res}')
        return hyper_pb2.movieResponse(movie=hyper_pb2.Movie(
            id = res['id'],
            last_watched =  res['last_watched'],
            watched = res['watched'],
            downloaded = res['downloaded'],
            download_path = res['download_path'],
            file_size = res['file_size'],
        ))
    
    def getUserMovies(self, request, context):
        logger.info(f'getUserMovies request: {request}')
        if not request.movie_ids or not request.user_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.getUserMoviesResponse()
        try:
            movies = asyncio.run(db.get_user_movies(list(request.movie_ids), request.user_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.getUserMoviesResponse()
        logger.info(f'getUserMovies request success: {movies}')
        results = []
        for movie in movies:
            results.append(movie[0])
        logger.info(f'results {results}')
        return hyper_pb2.getUserMoviesResponse(movie_ids=results)
    
    def getMovies(self, request, context):
        logger.info(f'getMovies request: {request}')
        try:
            movies = asyncio.run(db.get_movies())
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.getUserMoviesResponse()
        logger.info(f'getMovies request success: {movies}')
        results = []
        for movie in movies:
            _movie = hyper_pb2.Movie(
                id = movie[0],
                last_watched =  movie[1],
                watched = movie[2],
                downloaded = movie[3],
                download_path = movie[4],
                file_size = movie[5],
            )
            results.append(_movie)
        logger.info(f'results {results}')
        return hyper_pb2.moviesResponse(movies=results)

    def updateMovie(self, request, context):
        logger.info(f'updateMovie request: ${request}')
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.movieResponse()
        try:
            movie = asyncio.run(db.update_movie(request.movie_id, request.downloaded or None, request.last_watched or None))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.movieResponse()
        _movie = hyper_pb2.Movie(
            id = movie['id'],
            last_watched =  movie['last_watched'],
            watched = movie['watched'],
            downloaded = movie['downloaded'],
            download_path = movie['download_path'],
            file_size = movie['file_size'],
        )
        return hyper_pb2.movieResponse(movie=_movie)

    def deleteMovie(self, request, context):
        logger.info(f'deleteMovie request: ${request}')
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.movieResponse()
        try:
            asyncio.run(db.delete_movie(request.movie_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.movieResponse()
        logger.info(f'deleteMovie request success')
        return hyper_pb2.deleteMovieResponse(success=True)


class CommentServiceServicer(hyper_pb2_grpc.CommentServiceServicer):
    def addComment(self, request, context):
        logger.info(f'addComment request: {request}')
        if not request.movie_id or not request.author_id or not request.comment:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.addCommentResponse()
        try:
            res = asyncio.run(db.add_comment(request.movie_id, request.author_id, request.comment))
            # logger.info(f'add_comment res: {res}')
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.addCommentResponse()
        logger.info(f'addComment request success')
        return hyper_pb2.addCommentResponse(success=True)

    def getComments(self, request, context):
        logger.info(f'getComments request: {request}')
        if not request.movie_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operation Failed: Missing data')
            return hyper_pb2.getCommentsResponse()
        try:
            comments = asyncio.run(db.get_comments(request.movie_id))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Operation Failed: database exception: {e}')
            logger.error(f'Operation Failed: database exception: {e}')
            return hyper_pb2.getCommentsResponse()
        if not comments or len(comments) == 0:
            return hyper_pb2.getCommentsResponse()
        results = []
        for comment in comments:
            _comment = hyper_pb2.Comment(
                id = comment[0],
                author_id = comment[1],
                movie_id = comment[2],
                date = comment[3],
                comment = comment[4]
            )
            results.append(_comment)
        logger.info(f'getComments request success: {results}')
        return hyper_pb2.getCommentsResponse(comments=results)

def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_connection_age_ms', 60000),
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
        ]
    )

    hyper_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    hyper_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    hyper_pb2_grpc.add_MovieServiceServicer_to_server(MovieServiceServicer(), server)
    hyper_pb2_grpc.add_CommentServiceServicer_to_server(CommentServiceServicer(), server)

    server.add_insecure_port(f'[::]:{os.getenv('GRPC_SERVER_PORT')}')
    server.start()
    logger.info(f'gRPC server started on {os.getenv('GRPC_SERVER_PORT')}')
    server.wait_for_termination()
