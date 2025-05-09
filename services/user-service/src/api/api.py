from fastapi import APIRouter
from .endpoints import profile
from .endpoints import logout
from .endpoints import editUser
from .endpoints import search

router = APIRouter()

router.include_router(logout.router, prefix='/logout')
router.include_router(profile.router, prefix='/profile')
router.include_router(editUser.router, prefix='/update')
router.include_router(search.router, prefix='/search')