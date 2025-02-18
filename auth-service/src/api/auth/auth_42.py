import os
import urllib.parse
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from .jw_tokens import sign_tokens
from .register_user import register_user
import base64

load_dotenv()
router = APIRouter()

@router.get('/')
def ft_auth():
    if not os.getenv("ft_client_id") or not os.getenv("ft_client_secret") or not os.getenv('ft_redirect_uri') or not os.getenv('oauth_state'):
        return HTTPException(status_code=500, detail={"error": "Missing OAuth environment variables!"})
    client_id = f'client_id={os.getenv("ft_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('ft_redirect_uri')}'
    response_type = 'response_type=code'
    scope = 'scope=public'
    encoded_state = base64.b64encode(os.getenv('oauth_state').encode('utf-8')).decode('utf-8')
    state = f'state={encoded_state}'
    ft_auth_url = f'https://api.intra.42.fr/oauth/authorize?{client_id}&{redirect_uri}&{response_type}&{scope}&{state}'
    return RedirectResponse(url=ft_auth_url)

@router.get('/redirect')
async def ft_auth_callback(request: Request, response: Response):
    state = request.query_params.get('state')
    decoded_state = base64.b64decode(state.encode('utf-8')).decode('utf-8')
    if decoded_state != os.getenv('oauth_state'):
        return HTTPException(status_code=400, detail='State does not match.')
    client_id = f'client_id={os.getenv("ft_client_id")}'
    client_secret = f'client_secret={os.getenv("ft_client_secret")}'
    code = f'code={request.query_params.get("code")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = f'redirect_uri={os.getenv('ft_redirect_uri')}'
    ft_token_url = f'https://api.intra.42.fr/oauth/token?{client_id}&{client_secret}&{code}&{grant_type}&{redirect_uri}'

    async with httpx.AsyncClient() as client:
        token_response = await client.post(ft_token_url)
        if token_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://api.intra.42.fr/v2/me",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    oauth_id = str(user_info.get('id'))
    email = user_info.get('email').lower()
    first_name = user_info.get('first_name')
    last_name = user_info.get('last_name')
    username = user_info.get('login').lower()
    picture = user_info.get('image')['link']
    try:
        user = register_user(oauth_id, email, first_name, last_name, username, picture)
    except Exception as e:
        print('[42_OAUTH]', e)
        return HTTPException(status_code=400, detail={"error": f"Failed to register user: {e}"})
    if user is None:
        return HTTPException(status_code=400, detail={"error": "Failed to register user"})
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user