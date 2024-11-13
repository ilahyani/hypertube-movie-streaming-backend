from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .api import api as auth_api
# from .grpc import grpc_server as grpc_server
# from src.database.db import search_users
# import threading
# import uvicorn
# import asyncio

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

##TODO: grpc stops after 4 to 5 exceptions

# async def start_grpc_server():
#     while True:
#         try:
#             grpc_thread = threading.Thread(target=grpc_server.serve, daemon=True)
#             grpc_thread.start()
#             while grpc_thread.is_alive():
#                 await asyncio.sleep(5)
#         except Exception as e:
#             print(f"gRPC server error: {e}")
#         print("gRPC server stopped. Restarting...")
#         time.sleep(1)

# loop = asyncio.get_event_loop()
# loop.create_task(start_grpc_server())