import subprocess
import sys
import os
subprocess.run([sys.executable, "-m", "venv", "./env"])

# python3 -m venv env
# source env/bin/activate
# pip install --upgrade pip
# pip install "protobuf==5.27.2" "grpcio==1.66.2" "grpcio-tools<=1.66.2"
# deactivate

commands = [
    [
        "python3", "-m", "grpc_tools.protoc",
        "-I=.",
        "--python_out=../data-service/src/grpc",
        "--grpc_python_out=../data-service/src/grpc",
        "hyper.proto"
    ],
    [
        "python3", "-m", "grpc_tools.protoc",
        "-I=.",
        "--python_out=../auth-service/src/grpc",
        "--grpc_python_out=../auth-service/src/grpc",
        "hyper.proto"
    ],
    [
        "python3", "-m", "grpc_tools.protoc",
        "-I=.",
        "--python_out=../user-service/src/grpc",
        "--grpc_python_out=../user-service/src/grpc",
        "hyper.proto"
    ],
    [
        "python3", "-m", "grpc_tools.protoc",
        "-I=.",
        "--python_out=../authorization-service/src/grpc",
        "--grpc_python_out=../authorization-service/src/grpc",
        "hyper.proto"
    ]
]

for command in commands:
    subprocess.run(command)