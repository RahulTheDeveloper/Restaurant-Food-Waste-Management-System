from storages.backends.s3boto3 import S3Boto3Storage
import uuid
from django.conf import settings


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    custom_domain = None
    region_name = settings.AWS_S3_REGION_NAME
    default_acl = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StaticStorage(S3Boto3Storage):
    
    location = 'static'
    file_overwrite = True
    default_acl = None
    region_name = settings.AWS_S3_REGION_NAME

