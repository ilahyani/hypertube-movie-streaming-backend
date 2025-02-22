#!/bin/bash

python3 -m grpc_tools.protoc -I=/grpc --python_out=./src/grpc --grpc_python_out=./src/grpc hyper.proto

sed -i 's/import hyper_pb2 as hyper__pb2/from src.grpc import hyper_pb2 as hyper__pb2/g' /app/src/grpc/hyper_pb2_grpc.py

fastapi run src/main.py --host 0.0.0.0