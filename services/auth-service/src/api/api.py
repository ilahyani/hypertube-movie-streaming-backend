from fastapi import APIRouter
from .endpoints.strategies import google
from .endpoints.strategies import github
from .endpoints.strategies import gitlab
from .endpoints.strategies import _42
from .endpoints.strategies import discord
from .endpoints import register
from .endpoints import login
from .endpoints import token
from .endpoints import reset_passwd

router = APIRouter()

router.include_router(token.router, prefix='/refresh')
router.include_router(google.router, prefix='/google')
router.include_router(_42.router, prefix='/42')
router.include_router(discord.router, prefix='/discord')
router.include_router(github.router, prefix='/github')
router.include_router(gitlab.router, prefix='/gitlab')
router.include_router(register.router, prefix='/register')
router.include_router(login.router, prefix='/login')
router.include_router(reset_passwd.router, prefix='/reset-passwd')
