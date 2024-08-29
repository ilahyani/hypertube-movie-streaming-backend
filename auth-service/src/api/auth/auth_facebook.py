import os
import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from src.database.db import add_user_to_db, fetch_db
from .jw_tokens import sign_tokens

load_dotenv()
router = APIRouter()

@router.get('/')
def fb_auth():
    client_id = f'client_id={os.getenv("fb_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('fb_redirect_uri')}'
    state = f'state='
    fb_auth_url = f'https://www.facebook.com/v20.0/dialog/oauth?{client_id}&{redirect_uri}&{state}'
    return RedirectResponse(url=fb_auth_url)

@router.get('/redirect')
async def fb_auth_callback(request: Request, response: Response):
    client_id = f'client_id={os.getenv("fb_client_id")}'
    client_secret = f'client_secret={os.getenv("fb_client_secret")}'
    code = f'code={request.query_params.get("code")}'
    redirect_uri = f'redirect_uri={os.getenv('fb_redirect_uri')}'
    fb_token_url = f'https://graph.facebook.com/v20.0/oauth/access_token?{client_id}&{redirect_uri}&{client_secret}&{code}'
    async with httpx.AsyncClient() as client:
        token_response = await client.post(fb_token_url)
        if token_response.status_code != 200:
            return JSONResponse(status_code=400, content={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(f"https://graph.facebook.com/v20.0/me/?fields=email%2Cfirst_name%2Clast_name%2Cpicture%7Burl%7D%2Cname&access_token={token_data.get('access_token')}")
        if user_info_response.status_code != 200:
            return JSONResponse(status_code=400, content={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    if (user_info.get('email') == None):
        return JSONResponse(status_code=400, content={"error": "Signup failed: Email is required."})
    query = "SELECT * FROM users WHERE username = %s AND email = %s ;"
    params = (user_info.get('name').replace(" ", "_"), user_info.get('email'))
    user_data = await fetch_db(query, params)
    user = None
    if user_data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, user_data))
    if user is None:
        user = await add_user_to_db({
            'email': user_info.get('email'),
            'first_name': user_info.get('first_name'),
            'last_name': user_info.get('last_name') or user_info.get('given_name'),
            'username': user_info.get('name'),
            'picture': user_info.get('picture.data.url') or None
        }, True)
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user