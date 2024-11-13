FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt .

COPY ./entrypoint.sh .

# COPY ../grpc/user.proto ./user.proto

RUN pip install --no-cache-dir -r ./requirements.txt

# RUN python3 -m grpc_tools.protoc -I=. --python_out=./src/grpc --grpc_python_out=./src/grpc user.proto

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

# CMD ["python3", "dev", "src/main.py"]