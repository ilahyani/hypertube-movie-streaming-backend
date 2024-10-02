from fastapi import APIRouter
from .auth import auth_google
from .auth import auth_42
from .auth import auth_discord
from .auth import auth_register
from .auth import login
# from .auth import auth_facebook
# from .auth import reset_passwd
# from .auth import logout

router = APIRouter()

router.include_router(auth_google.router, prefix='/google')
router.include_router(auth_42.router, prefix='/42')
router.include_router(auth_discord.router, prefix='/discord')
router.include_router(auth_register.router, prefix='/register')
router.include_router(login.router, prefix='/login')
# router.include_router(auth_facebook.router, prefix='/facebook') # CANCELLED
# router.include_router(logout.router, prefix='/logout') # moved to user-service
# router.include_router(reset_passwd.router, prefix='/reset-passwd') # moved to user-service