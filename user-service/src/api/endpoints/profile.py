from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/public')
async def get_public_profile(id: str, request: Request, response: Response):
    return

@router.get('/private')
async def get_private_profile(id: str, request: Request, response: Response):
    return