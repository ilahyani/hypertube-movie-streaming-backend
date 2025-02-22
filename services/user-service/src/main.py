from fastapi import FastAPI, Request
from .api import api as user_api

app = FastAPI()

app.include_router(user_api.router, prefix='/api/user')

@app.get('/api/user')
def root(request: Request):
    return { 'message': f'User Service is LIIIVE: {request.headers.get("X-User-ID")}' }
