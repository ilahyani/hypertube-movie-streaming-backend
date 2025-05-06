from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/')
async def logout(request: Request):
    try:
        response = JSONResponse(content={"message": "Logged out successfully"}, status_code=200)
        response.delete_cookie(key='access_token', httponly=True)
        response.delete_cookie(key='refresh_token', httponly=True)
       
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
