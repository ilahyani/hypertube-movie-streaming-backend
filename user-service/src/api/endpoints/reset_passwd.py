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

@router.post('/')
async def send_passwdReset_email(request: Request, response: Response):
    email = None
    try:
        body = await request.json()
    except Exception as e:
        print(f'Failed to parse body: {e}')
        return HTTPException(status_code=400, detail={'error': 'Bad Request'})
    email = body.get('email')
    if email is None:
        return HTTPException(status_code=400, detail={'error': 'Email is required to perform this action'})

    user = getUserById(request.state.user_id)
    if user is None:
        print('user not found')
        return HTTPException(status_code=400, detail={'error': 'Bad Request'})
    print('protobuf', user)
    user = MessageToDict(user, preserving_proto_field_name=True)
    print('dict', user)
    if user['user']['email'] != email:
        raise HTTPException(status_code=400, detail={'error': 'Invalid Request'})

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
    # return response

@router.post('/reset')
async def verify_email(request: Request, response: Response):
    token = request.query_params.get('token')
    if token is None:
        return HTTPException(status_code=400, detail={'error': 'Token required'})
    # isValid, payload = True, jwt.decode()
    # if isValid is False or payload.user_id is None:
    #     return HTTPException(status_code=400, detail={'error': 'Invalid Token'})
    # query = "SELECT * FROM users WHERE id = %s ;"
    # params = (payload.user_id, )
    # user_data = await fetch_db(query, params)
    user = None
    if user is None:
        JSONResponse(status_code=200, content={'success': False})
    return JSONResponse(status_code=200, content={'success': True})
