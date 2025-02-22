import datetime, os
import jwt
from dotenv import load_dotenv

load_dotenv()

def sign_tokens(user):
    access_payload = {
        'sub': user.get('id'),
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }
    refresh_payload = {
        'sub': user.get('id'),
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    }
    access_token = jwt.encode(access_payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    refresh_token = jwt.encode(refresh_payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    return access_token, refresh_token

def verify_token(token):
    try:
        decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
        return True, decoded
    except jwt.InvalidTokenError:
        return False, None
    
def refresh_token(refresh_token):
    refresh_token_valid, refresh_token_decoded = verify_token(refresh_token)
    if not refresh_token_valid:
        return False, None
    payload = {
        'sub': refresh_token_decoded['sub'],
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }
    fresh_access_token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    return True, fresh_access_token
