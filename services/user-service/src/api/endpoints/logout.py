from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/')
async def logout(request: Request, response: Response):
    try:
        response.delete_cookie(key='access_token', httponly=True)
        response.delete_cookie(key='refresh_token', httponly=True)
        return JSONResponse(status_code=200, content={'success': True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))