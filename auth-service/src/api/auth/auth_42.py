import os
import urllib.parse
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from .jw_tokens import sign_tokens
from .register_user import register_user

load_dotenv()
router = APIRouter()

@router.get('/')
def ft_auth():
    client_id = f'client_id={os.getenv("ft_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('ft_redirect_uri')}'
    response_type = 'response_type=code'
    scope = 'scope=public'
    state = f'state='
    ft_auth_url = f'https://api.intra.42.fr/oauth/authorize?{client_id}&{redirect_uri}&{response_type}&{scope}&{state}'
    return RedirectResponse(url=ft_auth_url)

@router.get('/redirect')
async def ft_auth_callback(request: Request, response: Response):
    # state = request.query_params.get('state')
    client_id = f'client_id={os.getenv("ft_client_id")}'
    client_secret = f'client_secret={os.getenv("ft_client_secret")}'
    code = f'code={request.query_params.get("code")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = f'redirect_uri={os.getenv('ft_redirect_uri')}'
    ft_token_url = f'https://api.intra.42.fr/oauth/token?{client_id}&{client_secret}&{code}&{grant_type}&{redirect_uri}'

    async with httpx.AsyncClient() as client:
        token_response = await client.post(ft_token_url)
        if token_response.status_code != 200:
            return HTTPException(status_code=400, content={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://api.intra.42.fr/v2/me",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, content={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    email = user_info.get('email')
    first_name = user_info.get('first_name')
    last_name = user_info.get('last_name')
    username = user_info.get('login')
    picture = user_info.get('image')['link']
    user = await register_user(email, first_name, last_name, username, picture)
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user