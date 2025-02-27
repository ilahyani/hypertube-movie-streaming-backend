import httpx
import boto3
import os
import datetime
from dotenv import load_dotenv
from src.grpc.grpc_client import addUser
from google.protobuf.json_format import MessageToDict
from .upload_to_s3 import upload_avatar_to_s3

async def register_user(oauth_id: str, email: str, first_name: str, last_name: str, username: str, picture: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(picture)
        response.raise_for_status()
        content = response.content
    picture_link = await upload_avatar_to_s3(username, content)
    user_msg, error = addUser({
        'id': '0',
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'picture': picture_link
    }, oauth_id)
    if user_msg is None:
        print(f'[register_user failed]: {error}')
        return None
    user_msg = MessageToDict(user_msg, preserving_proto_field_name=True)
    return user_msg['user']
