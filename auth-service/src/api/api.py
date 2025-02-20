from fastapi import APIRouter
from .auth import auth_google
from .auth import auth_github
from .auth import auth_gitlab
from .auth import auth_42
from .auth import auth_discord
from .auth import auth_register
from .auth import login
from .auth import refresh_token
# from .auth import auth_facebook

router = APIRouter()

router.include_router(refresh_token.router, prefix='/refresh')
router.include_router(auth_google.router, prefix='/google')
router.include_router(auth_42.router, prefix='/42')
router.include_router(auth_discord.router, prefix='/discord')
router.include_router(auth_github.router, prefix='/github')
router.include_router(auth_gitlab.router, prefix='/gitlab')
router.include_router(auth_register.router, prefix='/register')
router.include_router(login.router, prefix='/login')
# router.include_router(auth_facebook.router, prefix='/facebook') # CANCELLED
