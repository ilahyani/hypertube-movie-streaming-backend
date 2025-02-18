import os
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
async def discord_auth(request: Request, response: Response):
    if not os.getenv("ft_client_id") or not os.getenv("ft_client_secret") or not os.getenv('ft_redirect_uri') or not os.getenv('oauth_state'):
        return HTTPException(status_code=500, detail={"error": "Missing OAuth environment variables!"})
    client_id = f'client_id={os.getenv('dscrd_client_id')}'
    redirect_uri = f'redirect_uri={os.getenv('dscrd_redirect_uri')}'
    encoded_state = base64.b64encode(os.getenv('oauth_state').encode('utf-8')).decode('utf-8')
    state = f'state={encoded_state}'
    url = f"https://discord.com/oauth2/authorize?{client_id}&response_type=code&{redirect_uri}&{state}&scope=email%20identify&"
    return RedirectResponse(url)

@router.get('/redirect')
async def discord_auth_callback(request: Request, response: Response):
    state = request.query_params.get('state')
    decoded_state = base64.b64decode(state.encode('utf-8')).decode('utf-8')
    if decoded_state != os.getenv('oauth_state'):
        return HTTPException(status_code=400, detail='State does not match.')
    data = {
        'client_id': os.getenv('dscrd_client_id'),
        'client_secret': os.getenv('dscrd_client_secret'),
        'redirect_uri': os.getenv('dscrd_redirect_uri'),
        'code': request.query_params.get("code"),
        'grant_type': 'authorization_code'
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post("https://discord.com/api/v10/oauth2/token", data=data)
        if token_response.status_code != 200:
            print(token_response)
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://discord.com/api/v10/users/@me",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    oauth_id = user_info.get('id')
    email = user_info.get('email').lower()
    name = user_info.get('global_name')
    username = user_info.get('username').lower()
    avatar = f'https://cdn.discordapp.com/avatars/{user_info.get('id')}/{user_info.get('avatar')}?size=256'
    try:
        user = register_user(oauth_id, email, name, name, username, avatar)
    except Exception as e:
        print('[D_OAUTH]', e)
        return HTTPException(status_code=400, detail={"error": f"Failed to register user: {e}"})
    if user is None:
        return HTTPException(status_code=400, detail={"error": "Failed to register user"})
    access_token, refresh_token = sign_tokens(user)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return user