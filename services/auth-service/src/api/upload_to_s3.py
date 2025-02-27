import httpx
import boto3
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

async def upload_avatar_to_s3(username, content):    
    try:
        s3 = boto3.client(
            's3', aws_access_key_id = os.getenv('AWS_KEY'),
            aws_secret_access_key = os.getenv('AWS_SECRET'))
        s3_key = f'avatars/{datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")}_{username}_avatar.jpg'
        s3.put_object(Bucket='hyperrrr-bucket', Key=s3_key, Body=content)
        return f"https://hyperrrr-bucket.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(e)
    return None
