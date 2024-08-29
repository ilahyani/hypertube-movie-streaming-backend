from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .api import api as auth_api

app = FastAPI()

app.include_router(auth_api.router, prefix='/api/auth')

@app.get("/")
async def root():
    return { "message": "Auth Service IS UP!" }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    err_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}"
    return JSONResponse(
        status_code = 400,
        content = { "error":  err_msg }
    )
