from fastapi import APIRouter
from .endpoints import reset_passwd
from .endpoints import profile
from .endpoints import logout

router = APIRouter()

router.include_router(logout.router, prefix='/logout')
router.include_router(reset_passwd.router, prefix='/reset-passwd')
router.include_router(profile.router, prefix='/profile')