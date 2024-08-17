# main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from auth_google import router as google_auth
from auth_42 import router as ft_auth
from auth_register import router as register_auth
from login import router as login

app = FastAPI()

app.include_router(google_auth)
app.include_router(ft_auth)
app.include_router(register_auth)
app.include_router(login)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    err_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}"
    return JSONResponse(
        status_code = 400,
        content = { "error":  err_msg }
    )
