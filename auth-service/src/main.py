from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .api import api as auth_api
from .grpc import grpc_server as grpc_server
import threading
import uvicorn
import asyncio

app = FastAPI()

app.include_router(auth_api.router, prefix='/api/auth')

@app.get("/")
def root():
    return { "message": "Auth Service IS UP!" }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    err_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}"
    return JSONResponse(
        status_code = 400,
        content = { "error":  err_msg }
    )

async def start_grpc_server():
    grpc_thread = threading.Thread(target=grpc_server.serve, daemon=True)
    grpc_thread.start()

# if __name__ == "__main__":
loop = asyncio.get_event_loop()
loop.run_until_complete(start_grpc_server())
uvicorn.run(app, host='0.0.0.0', port=8000)