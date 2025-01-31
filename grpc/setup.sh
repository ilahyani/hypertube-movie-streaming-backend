#!/bin/bash

apt-get update
pip install --upgrade pip
pip install "protobuf==5.27.2" "grpcio==1.66.2" "grpcio-tools<=1.66.2"
python3 -m grpc_tools.protoc -I=. --python_out=../data-service/src/grpc_files --grpc_python_out=../data-service/src/grpc_files hyper.proto
python3 -m grpc_tools.protoc -I=. --python_out=../auth-service/src/grpc --grpc_python_out=../auth-service/src/grpc hyper.proto
python3 -m grpc_tools.protoc -I=. --python_out=../user-service/src/grpc --grpc_python_out=../user-service/src/grpc hyper.proto