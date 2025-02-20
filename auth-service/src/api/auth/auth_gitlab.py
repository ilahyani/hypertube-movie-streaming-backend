import os
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from .jw_tokens import sign_tokens
from .register_user import register_user
from .. import redis
import secrets
import hashlib
import base64
import json
import asyncio

load_dotenv()
router = APIRouter()

@router.get('/')
async def gt_auth():
    if not os.getenv("gt_client_id") or not os.getenv("gt_client_secret") or not os.getenv('gt_redirect_uri'):
        return HTTPException(status_code=500, detail={"error": "Missing OAuth environment variables!"})
    client_id = f'client_id={os.getenv("gt_client_id")}'
    redirect_uri = f'redirect_uri={os.getenv('gt_redirect_uri')}'
    response_type = 'response_type=code'
    scope = 'scope=read_user'
    user_key = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(32)
    code_verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_verifier_hash).decode().rstrip("=")
    state_data = {
        'state': secrets.token_urlsafe(32),
        'key': f"state:{user_key}"
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    await asyncio.gather(
        redis.add_key_value_redis(state_data.get("key"), state_data.get("state"), 600),
        redis.add_key_value_redis(state_data.get("state"), code_verifier, 600)
    )
    state = f'state={encoded_state}'
    code_challenge_query = f'code_challenge={code_challenge}&code_challenge_method=S256'
    gt_auth_url = f"https://gitlab.com/oauth/authorize?response_type=code&{client_id}&{redirect_uri}&{response_type}&{scope}&{state}&{code_challenge_query}"
    return RedirectResponse(url=gt_auth_url)

@router.get('/redirect')
async def gt_auth_callback(request: Request, response: Response):
    encoded_state = request.query_params.get('state')
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
    state_record, code_verifier = await asyncio.gather(
        redis.get_value_redis(state_data.get("key")),
        redis.get_value_redis(state_data.get("state"))
    )
    if (state_record != state_data.get("state")):
        return HTTPException(status_code=400, detail='State does not match.')
    await redis.delete_key_redis(state_data.get("key"))
    code = f'code={request.query_params.get("code")}'
    client_id = f'client_id={os.getenv("gt_client_id")}'
    client_secret = f'client_secret={os.getenv("gt_client_secret")}'
    grant_type = f'grant_type=authorization_code'
    redirect_uri = f'redirect_uri={os.getenv('gt_redirect_uri')}'
    code_verifier = f'code_verifier={code_verifier}'
    gt_token_url = f'https://gitlab.com/oauth/token?{client_id}&{client_secret}&{code}&{grant_type}&{redirect_uri}&{code_verifier}'

    async with httpx.AsyncClient() as client:
        token_response = await client.post(gt_token_url)
        if token_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve access token"})
        token_data = token_response.json()
        user_info_response = await client.get(
            f"https://gitlab.com/api/v4/user?access_token={token_data.get('access_token')}"
        )
        if user_info_response.status_code != 200:
            return HTTPException(status_code=400, detail={"error": "Failed to retrieve user info"})
    user_info = user_info_response.json()
    oauth_id = str(user_info.get('id'))
    picture = user_info.get('avatar_url')
    email = user_info.get('email')
    if email is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: email"})
    email = email.lower()
    username = user_info.get('username')
    if username is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: username"})
    username = username.lower()
    name = user_info.get('name')
    if name is None:
        return HTTPException(status_code=400, detail={"error": "Required data missing: name"})
    parts = name.split(' ')
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else parts[0]
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