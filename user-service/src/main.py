from fastapi import FastAPI
from .api import api as user_api
from .middleware.jwt_middleware import jwt_middleware

app = FastAPI()

app.include_router(user_api.router, prefix='/api/user')

app.middleware('http')(jwt_middleware)

@app.get('/')
def root():
    return { 'message': 'User Service is LIIIVE' }
