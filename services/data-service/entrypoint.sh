#!/bin/bash

# pip install protobuf grpcio "grpcio-tools<=1.66.2"

python3 -m grpc_tools.protoc -I=/grpc --python_out=./src/grpc_files --grpc_python_out=./src/grpc_files hyper.proto

export PYTHONPATH=$PYTHONPATH:/app/src

sed -i 's/import hyper_pb2 as hyper__pb2/from src.grpc_files import hyper_pb2 as hyper__pb2/g' /app/src/grpc_files/hyper_pb2_grpc.py

python3 src/main.py