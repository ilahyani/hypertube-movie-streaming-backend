# from fastapi import Request, Response, HTTPException
# import datetime, jwt, os
# from src.grpc.grpc_client import getUserById

# async def jwt_middleware(request: Request, call_next):
#     print('================== JWT MIDDLEWARE ==================')
#     token = request.cookies.get('access_token')
#     if not token:
#         return Response(status_code=403, content='Forbidden')
#     try:
#         payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
#     except jwt.ExpiredSignatureError:
#         print('[JWT MIDDLEWARE] Refreshing Access Token')
#         refresh_token = request.cookies.get('refresh_token')
#         if not refresh_token:
#             return Response(status_code=400, content='REFRESH NOT FOUND, REDIRECT TO LOGIN!!!!!!!')
#         try:
#             refresh_payload = jwt.decode(refresh_token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
#         except jwt.ExpiredSignatureError:
#             return Response(content='TOKEN EXPIRED, REDIRECT TO LOGIN!!!!!!!', status_code=400)
#         except jwt.InvalidTokenError as e:
#             print(f'[JWT MIDDLEWARE] refresh_token error: {e}')
#             return Response(status_code=400, content='Invalid JWT')
#         except Exception as e:
#             print(f'[JWT MIDDLEWARE] refresh_token error: {e}')
#             return Response(status_code=500, content='Internal Server Error')
#         user, error = getUserById(refresh_payload['user_id'])
#         if user is None:
#             print(f'[JWT MIDDLEWARE] user not found: {error}')
#             return Response(status_code=400, content='Forbidden')
#         payload = {
#             'user_id': refresh_payload['user_id'],
#             'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
#         }
#         fresh_access_token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
#         print('[JWT MIDDLEWARE] FreshToken', fresh_access_token)
#         response = Response()
#         response.set_cookie(key='access_token', value=fresh_access_token, httponly=True)
#     except jwt.InvalidTokenError as e:
#         print(f'[JWT MIDDLEWARE] access_token error: {e}')
#         return Response(status_code=400, content='Invalid JWT')
#     except Exception as e:
#         print(f'[JWT MIDDLEWARE] access_token error: {e}')
#         return Response(status_code=500, content='Internal Server Error')
#     user, error = getUserById(payload['user_id'])
#     if user is None:
#         print(f'[JWT MIDDLEWARE] user not found: {error}')
#         return Response(status_code=400, content='Forbidden')
#     request.headers.get("X-User-ID") = payload['user_id']
#     print('[JWT MIDDLEWARE] state.user_id', request.headers.get("X-User-ID"))
#     response = await call_next(request)
#     return response
