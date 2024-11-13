#!/bin/bash

# pip install protobuf grpcio "grpcio-tools<=1.66.2"

python3 -m grpc_tools.protoc -I=/grpc --python_out=./src/grpc_files --grpc_python_out=./src/grpc_files user.proto

export PYTHONPATH=$PYTHONPATH:/app/src

sed -i 's/import user_pb2 as user__pb2/from src.grpc_files import user_pb2 as user__pb2/g' /app/src/grpc_files/user_pb2_grpc.py

python3 src/main.py