#!/bin/bash

pip install protobuf grpcio "grpcio-tools<=1.66.2"

python -m grpc_tools.protoc -I=/grpc --python_out=./src/grpc --grpc_python_out=./src/grpc user.proto

sed -i 's/import user_pb2 as user__pb2/from src.grpc import user_pb2 as user__pb2/g' /app/src/grpc/user_pb2_grpc.py

fastapi dev src/main.py --host 0.0.0.0