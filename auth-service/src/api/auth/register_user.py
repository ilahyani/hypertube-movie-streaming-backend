import httpx
import boto3
import os
import datetime
from dotenv import load_dotenv
from src.database.db import add_user_to_db, fetch_db

load_dotenv()

async def upload_avatar_to_s3(username, url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content
    try:
        s3 = boto3.client(
            's3', aws_access_key_id = os.getenv('AWS_KEY'),
            aws_secret_access_key = os.getenv('AWS_SECRET'))
        s3_key = f'avatars/{datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")}_{username}_avatar.jpg'
        s3.put_object(Bucket='hyper-hyper-bucket', Key=s3_key, Body=content)
        return s3_key
    except Exception as e:
        print(e)
    avatar_url = ''
    return avatar_url

async def register_user(email: str, first_name: str, last_name: str, username: str, picture: str):
    query = "SELECT * FROM users WHERE username = %s AND email = %s ;"
    params = (username.replace(" ", "_"), email)
    user_data = await fetch_db(query, params)
    user = None
    if user_data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, user_data))
    if user is None:
        picture_s3_path = await upload_avatar_to_s3(username, picture)
        user = await add_user_to_db({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'picture': picture_s3_path
        }, True)
    return user