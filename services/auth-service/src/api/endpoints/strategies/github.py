import os
import urllib.parse
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
import base64
import json
import secrets
from ....api.save_user import *
from ....api.jw_tokens import *
from ....api.redis import *

load_dotenv()
router = APIRouter()

@router.get('/')
async def gh_auth():
    if not os.getenv("gh_client_id") or not os.getenv("gh_client_secret") or not os.getenv('gh_redirect_uri'):
        return HTTPException(status_code=500, detail={"error": "Missing OAuth environment variables!"})
    client_id = f'client_id={os.getenv("gh_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('gh_redirect_uri')}'
    response_type = 'response_type=code'
    scope = 'scope=read:user'
    user_key = secrets.token_urlsafe(32)
    state_data = {
        'state': secrets.token_urlsafe(32),
        'key': f"state:{user_key}"
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    await add_key_value_redis(state_data.get("key"), state_data.get("state"), 600)
    state = f'state={encoded_state}'
    gh_auth_url = f"https://github.com/login/oauth/authorize?{client_id}&{redirect_uri}&{state}&{scope}"
    return RedirectResponse(url=gh_auth_url)

@router.get('/redirect')
async def gh_auth_callback(request: Request):
    encoded_state = request.query_params.get('state')
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
    state_record = await get_value_redis(state_data.get("key"))
    if (state_record != state_data.get("state")):
        return HTTPException(status_code=400, detail='State does not match.')
    await delete_key_redis(state_data.get("key"))
    client_id = f'client_id={os.getenv("gh_client_id")}'
    client_secret = f'client_secret={os.getenv("gh_client_secret")}'
    code = f'code={request.query_params.get("code")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = f'redirect_uri={os.getenv('gh_redirect_uri')}'
    gh_token_url = f"https://github.com/login/oauth/access_token?{client_id}&{client_secret}&{code}&{redirect_uri}"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(gh_token_url, headers={ 'Accept': 'application/json' })
        if token_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://api.github.com/user",
            headers = {
                'Authorization': f"Bearer { token_data.get('access_token') }"
            }
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve user info"})
    
    user_info = user_info_response.json()
    oauth_id = str(user_info.get('id'))
    picture = user_info.get('avatar_url')
    username = user_info.get('login').lower()
    if username is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: username"})
    username = username.lower()
    email = user_info.get('email')
    if email is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: email"})
    email = email.lower()
    name = user_info.get('name')
    if name is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: name"})
    parts = name.split(' ')
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else parts[0]
    try:
        user = await register_user(oauth_id, email, first_name, last_name, username, picture)
    except Exception as e:
        print('[GH_OAUTH]', e)
        return HTTPException(status_code=400, detail={"error": f"Failed to register user: {e}"})
    if user is None:
        return HTTPException(status_code=400, detail={"error": "Failed to register user"})
    access_token, refresh_token = sign_tokens(user)
    
    response = RedirectResponse(url=os.getenv("CLIENT_HOST"))
    response.set_cookie(key='access_token', value=access_token, httponly=True, domain=localhost)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, domain=localhost)
    
    return response
