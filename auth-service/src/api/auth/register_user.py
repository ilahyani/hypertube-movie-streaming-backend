import httpx
import boto3
import os
import datetime
from dotenv import load_dotenv
from src.database.db import add_user_to_db, fetch_db, get_user_by_username, get_user_dict

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
        return f"https://hyper-hyper-bucket.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(e)
    avatar_url = ''
    return avatar_url

#TODO: CONFIRM EMAILS

async def register_user(oauth_id: str, email: str, first_name: str, last_name: str, username: str, picture: str):
    query = "SELECT * FROM users WHERE oauth_id = %s ;"
    user_data = await fetch_db(query, (oauth_id, ))
    if user_data is not None:
        user = get_user_dict(user_data)
        del user['passwd'], user['oauth_id']
        return user
    # picture_s3_path = await upload_avatar_to_s3(username, picture)
    user = await add_user_to_db({
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'picture': picture
    }, oauth_id)
    return user