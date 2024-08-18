from fastapi import APIRouter
from .auth import auth_google
from .auth import auth_42
from .auth import auth_register
from .auth import login

router = APIRouter()

router.include_router(auth_google.router, prefix='/google')
router.include_router(auth_42.router, prefix='/42')
router.include_router(auth_register.router, prefix='/register')
router.include_router(login.router, prefix='/login')