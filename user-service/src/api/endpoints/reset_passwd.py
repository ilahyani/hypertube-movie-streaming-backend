import datetime, jwt, os
from dotenv import load_dotenv
from fastapi import Request, APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.grpc.grpc_client import getUserById
from src.grpc import user_pb2 as user_pb2

router = APIRouter()
load_dotenv()

@router.get('/')
async def send_passwdReset_email(request: Request, response: Response):
    user = getUserById(request.state.user_id)
    if user is None:
        print('user not found')
        return HTTPException(status_code=400, detail={'error': 'Bad Request'})
    user = MessageToDict(user[0], preserving_proto_field_name=True)
    email = user['user']['email']
    id = user['user']['id']
    payload = {
        'user_id': id,
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
        return JSONResponse(status_code=200, content={'success': False})

    return JSONResponse(status_code=200, content={'success': True})
    # return response

#TODO: FINISH THIS WHEN UI IS READY
@router.post('/reset')
async def verify_email(request: Request, response: Response):
    return True
