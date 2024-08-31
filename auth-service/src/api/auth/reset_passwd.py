import bcrypt, datetime, jwt, os
from fastapi import Request, APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse
from src.database.db import fetch_db
from .jw_tokens import verify_token
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

@router.post('/')
async def send_passwdReset_email(request: Request, response: Response):
    email = None
    try:
        body = await request.json()
    except Exception as e:
        print(f'Failed to parse body: {e}')
        return JSONResponse(status_code=400, content={'error': 'Bad Request'})
    email = body.get('email')
    if email is None:
        return HTTPException(status_code=400, content={'error': 'Email is required to perform this action'})
    
    query = "SELECT * FROM users WHERE email = %s ;"
    params = (email, )
    user_data = await fetch_db(query, params)
    user = None
    if user_data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, user_data))
    if user is None:
        return HTTPException(status_code=400, content={'error': 'No account is associated with this email'})

    payload = {
        'user_id': user.get('id'),
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5)
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGORITHM'))
    reset_link = f'{os.getenv('APP_HOST')}/api/auth/reset-passwd/reset?token={token}'

    message = MIMEMultipart("alternative")
    message["From"] = os.getenv('SMTP_USER')
    message["To"] = email
    message["Subject"] = 'PASSWORD RESET REQUEST'
    body = f"""
        <html>
        <body>
            <h1>PASSWORD RESET REQUEST</h1>
            <p>To reset your 🌽 CornHub Password click this link {reset_link} </p>
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

    return JSONResponse(status_code=200, content={'success': True})

@router.post('/reset')
async def verify_email(request: Request, response: Response):
    token = request.query_params.get('token')
    if token is None:
        return HTTPException(status_code=400, content={'error': 'Token required'})
    isValid, payload = verify_token(token)
    if payload.user_id is None:
        return HTTPException(status_code=400, content={'error': 'Invalid Token'})
    query = "SELECT * FROM users WHERE id = %s ;"
    params = (payload.user_id, )
    user_data = await fetch_db(query, params)
    if user_data is None:
        return HTTPException(status_code=400, content={'error': 'Invalid Token'})
    return JSONResponse(status_code=200, content={'success': True})
