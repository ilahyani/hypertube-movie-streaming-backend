from fastapi import FastAPI, Request, Response, HTTPException
import datetime, jwt, os
from src.grpc.grpc_client import getUserById

app = FastAPI()

@app.get("/")
def authorize(req: Request, res: Response):
    jwt_token = req.headers.get("Authorization")

    if not jwt_token:
        print('ACCESS TOKEN IS MISSING')
        raise HTTPException(status_code=401)
    jwt_token = jwt_token.split(" ")[1]
    if not os.getenv('JWT_SECRET') or not os.getenv('JWT_ALGORITHM'):
        raise HTTPException(status_code=500)
    try:
        payload = jwt.decode(
            jwt_token,
            os.getenv('JWT_SECRET'),
            algorithms=os.getenv('JWT_ALGORITHM')
        )
    
    except jwt.ExpiredSignatureError:
        print('ACCESS TOKEN IS EXPIRED')
        raise HTTPException(status_code=401)
    
    except jwt.InvalidTokenError:
        print('ACCESS TOKEN IS INVALID')
        raise HTTPException(status_code=401)
    
    except Exception as e:
        print(f'FAILED TO DECODE ACCESS TOKEN: {e}')
        raise HTTPException(status_code=500)

    user, error = getUserById(payload['sub'])
    if error:
        print(f'RPC CLIENT FAILED: {error}')
        raise HTTPException(status_code=403)
    if user is None:
        print(f'USER NOT FOUND: {payload['sub']}')
        raise HTTPException(status_code=403)
    res.headers["X-User-ID"] = payload['sub']
    res.headers["Authorization"] = req.headers.get("Authorization")
    return {}