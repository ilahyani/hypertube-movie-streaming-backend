import os
import urllib.parse
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from .jw_tokens import sign_tokens
from .register_user import register_user
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='../hyper.log', encoding='utf-8', level=logging.DEBUG)
load_dotenv()
router = APIRouter()

@router.get('/')
def gl_auth():
    client_id = f'client_id={os.getenv("gl_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('gl_redirect_uri')}'
    response_type = 'response_type=code'
    scope = f"scope={urllib.parse.quote('https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile')}"
    state = f'state='
    gl_auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{client_id}&{redirect_uri}&{response_type}&{scope}&{state}'
    return RedirectResponse(url=gl_auth_url)

@router.get('/redirect')
async def gl_auth_callback(request: Request, response: Response):
    # state = request.query_params.get('state')
    client_id = f'client_id={os.getenv("gl_client_id")}'
    client_secret = f'client_secret={os.getenv("gl_client_secret")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = f'redirect_uri={os.getenv('gl_redirect_uri')}'
    code = f'code={request.query_params.get("code")}'
    gl_token_url = f'https://oauth2.googleapis.com/token?{client_id}&{client_secret}&{code}&{grant_type}&{redirect_uri}'

    async with httpx.AsyncClient() as client:
        token_response = await client.post(gl_token_url)
        if token_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://www.googleapis.com/oauth2/v1/userinfo",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    # print('[G_OAUTH] info:', user_info)
    oauth_id = user_info.get('id')
    email = user_info.get('email').lower()
    first_name = user_info.get('given_name')
    last_name = user_info.get('family_name') or user_info.get('given_name')
    username = user_info.get('name').replace(" ", "_").lower()
    picture = user_info.get('picture')
    try:
        user = register_user(oauth_id, email, first_name, last_name, username, picture)
    except Exception as e:
        print('[G_OAUTH]', e)
        return HTTPException(status_code=400, detail={"error": f"Failed to register user: {e}"})
    if user is None:
        return HTTPException(status_code=400, detail={"error": "Failed to register user"})
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user