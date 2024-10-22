FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt .

COPY ./entrypoint.sh .

# COPY ../grpc/user.proto ./user.proto

RUN pip install --no-cache-dir -r ./requirements.txt

# RUN python -m grpc_tools.protoc -I=. --python_out=./src/grpc --grpc_python_out=./src/grpc user.proto

# RUN pip install protobuf grpcio grpcio-tools<=1.66.2

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

# DEV
# CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]

# PROD
# CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0"]