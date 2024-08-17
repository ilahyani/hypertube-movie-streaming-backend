import os
import urllib.parse
import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from database.db import add_user_to_db, get_user_from_db, fetch_db
from jw_tokens import sign_tokens

load_dotenv()
router = APIRouter()

@router.get('/api/auth/google')
def gl_auth():
    client_id = f'client_id={os.getenv("gl_client_id")}'
    redirect_uri = 'redirect_uri=http://localhost:8000/api/auth/google/redirect'
    response_type = 'response_type=code'
    scope = f"scope={urllib.parse.quote('https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile')}"
    state = f'state='
    gl_auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{client_id}&{redirect_uri}&{response_type}&{scope}&{state}'
    return RedirectResponse(url=gl_auth_url)

@router.get('/api/auth/google/redirect')
async def gl_auth_callback(request: Request, response: Response):
    # state = request.query_params.get('state')
    client_id = f'client_id={os.getenv("gl_client_id")}'
    client_secret = f'client_secret={os.getenv("gl_client_secret")}'
    code = f'code={request.query_params.get("code")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = 'redirect_uri=http://localhost:8000/api/auth/google/redirect'
    gl_token_url = f'https://oauth2.googleapis.com/token?{client_id}&{client_secret}&{code}&{grant_type}&{redirect_uri}'

    async with httpx.AsyncClient() as client:
        token_response = await client.post(gl_token_url)
        token_data = token_response.json()
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            f"https://www.googleapis.com/oauth2/v1/userinfo",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
    user_info = user_info_response.json()
    query = "SELECT * FROM users WHERE username = %s AND email = %s ;"
    params = (user_info.get('name'), user_info.get('email'))
    user_data = await fetch_db(query, params)
    user = None
    if user_data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, user_data))
    if user is None:
        user = await add_user_to_db({
            'email': user_info.get('email'),
            'first_name': user_info.get('given_name'),
            'last_name': user_info.get('family_name') or user_info.get('given_name'),
            'username': user_info.get('name'),
            'picture': user_info.get('picture')
        }, True)
    del user['passwd']
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user