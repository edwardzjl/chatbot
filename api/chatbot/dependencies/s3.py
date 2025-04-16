from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from minio import Minio
from chatbot.config import settings


@lru_cache
def get_s3_client() -> Minio:
    client = Minio(
        endpoint=settings.s3.endpoint,
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secret_key,
        secure=settings.s3.secure,
    )
    return client


S3ClientDep = Annotated[Minio, Depends(get_s3_client)]
