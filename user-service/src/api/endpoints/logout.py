from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/')
async def logout(request: Request, response: Response):
    response.set_cookie(key='access_token', value="", httponly=True, max_age=0)
    response.set_cookie(key='refresh_token', value="", httponly=True, max_age=0)
    return JSONResponse(status_code=200, content={'success': True})