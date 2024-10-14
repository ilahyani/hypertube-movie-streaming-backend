FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# RUN python -m grpc_tools.protoc -I=./src/grpc --python_out=./src/grpc --grpc_python_out=./src/grpc ./src/grpc/user.proto

# DEV
CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]

# PROD
# CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0"]