import datetime, jwt, os
from dotenv import load_dotenv
from fastapi import Request, APIRouter, Response, HTTPException, Query
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.grpc.grpc_client import *
from src.grpc import hyper_pb2 as hyper_pb2

router = APIRouter()
load_dotenv()

@router.post('/')
async def send_passwdReset_email(request: Request, email: str = Query(...)):
    if not email:
        raise HTTPException(status_code=404, detail={'error': 'email missing'})
    user, error = getUserByEmail(email)
    user = MessageToDict(user, preserving_proto_field_name=True)
    if not user:
        raise HTTPException(status_code=400, detail={'error': 'User Not Found'})
    email = user['user']['email']
    id = user['user']['id']
    payload = {
        'user_id': id,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=10)
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    reset_link = f"{os.getenv('CLIENT_HOST')}/resetpassword?token={token}"

    message = MIMEMultipart("alternative")
    message["From"] = os.getenv('SMTP_USER')
    message["To"] = email
    message["Subject"] = 'PASSWORD RESET REQUEST'
    body = f"""
        <html>
        <body>
            <h1>PASSWORD RESET REQUEST</h1>
            <p>To reset your Password click this link {reset_link} </p>
        </body>
        </html>
    """
    message.attach(MIMEText(body, "html"))
    try:
        with smtplib.SMTP_SSL(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT')) as server:
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
            server.sendmail(os.getenv('SMTP_USER'), email, message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return JSONResponse(status_code=200, content={'success': False})

    return JSONResponse(status_code=200, content={'success': True})

@router.post('/verify')
async def verify_email(request: Request, token: str = Query(...)):
    # user_id = request.headers.get("X-User-ID")

    try:
        decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
        user_id = decoded.get("user_id")
        if not user_id:
            return JSONResponse(status_code=200, content={"valid": False})
        user = getUserById(user_id)
        if user is None:
            return JSONResponse(status_code=200, content={"valid": False})
    
    except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
        return JSONResponse(status_code=200, content={"valid": False})
    
    except HTTPException:
        raise

    return JSONResponse(status_code=200, content={"valid": True}) 

@router.post('/reset')
async def reset_passwd(request: Request, token: str = Query(...)):
    try:
        decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=os.getenv('JWT_ALGORITHM'))
        user_id = decoded.get("user_id")
        if not user_id:
            raise HTTPException(status_code=403, detail=['Forbidden: Invalid Token'])
        
        try:
            body = await request.json()
    
        except Exception as e:
            print(f'[Profile Router] Failed to parse body: {e}')
            raise HTTPException(status_code=400, detail={'Failed to parse body'})
        
        new_password = str(body.get('new_password'))
        if not new_password:
            raise HTTPException(status_code=400, detail={'Bad Request'})
        update, error = updatePassword(user_id, None, new_password)
        
        if update is None:
            print('[reset-password Router] update failed')
            raise HTTPException(status_code=400, detail={ "error": error.details() })
        update = MessageToDict(update, preserving_proto_field_name=True)
        return update
    
    except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
        return JSONResponse(status_code=200, content={"message": "invalid_token"})
    
    except HTTPException:
        raise
