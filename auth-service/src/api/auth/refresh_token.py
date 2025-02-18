from fastapi import APIRouter, Request, Response, HTTPException
from dotenv import load_dotenv
import datetime, jwt, os

load_dotenv()
router = APIRouter()

@router.post('/')
async def refresh_token(request: Request):
    body = await request.json()
    refresh_token = body.get('refresh_token')
    if not refresh_token:
        return HTTPException(status_code=401, detail='REFRESH TOKEN NOT FOUND')
    try:
        payload = jwt.decode(refresh_token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
    except jwt.ExpiredSignatureError:
        return HTTPException(status_code=401, detail='TOKEN EXPIRED') # REDIRECT TO LOGIN
    except jwt.InvalidTokenError as e:
        return HTTPException(status_code=401, detail='Invalid Token') # REDIRECT TO LOGIN
    except Exception as e:
        print(f'[REFRESH_TOKEN] error: {e}')
        return HTTPException(status_code=500, detail='Internal Server Error')
    payload = {
        'sub': payload['sub'],
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }
    fresh_access_token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    return { 'access_token': fresh_access_token }
