# utils/aws.py
import boto3
from django.conf import settings
from botocore.config import Config

def generate_presigned_media_url(key: str, expires_in=3600) -> str:
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(region_name=settings.AWS_S3_REGION_NAME) 
    )
    
    if not isinstance(settings.AWS_STORAGE_BUCKET_NAME, str):
        raise ValueError(f"Invalid bucket name: {settings.AWS_STORAGE_BUCKET_NAME!r}")

    media_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': f'media/{key}'
        },
        ExpiresIn=expires_in
    )

    return media_url

    