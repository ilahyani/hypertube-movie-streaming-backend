from fastapi import FastAPI, Request
from .api import api as user_api
# from .middleware.jwt_middleware import jwt_middleware

app = FastAPI()

app.include_router(user_api.router, prefix='/api/user')

# app.middleware('http')(jwt_middleware)

@app.get('/api/user')
def root(request: Request):
    return { 'message': f'User Service is LIIIVE: {request.headers.get("X-User-ID")}' }
