from fastapi import APIRouter

from chatbot.config import settings
from chatbot.dependencies import S3ClientDep, UserIdHeaderDep


router = APIRouter(
    prefix="/api/files",
    tags=["files"],
)


@router.get("/upload-url")
def get_presigned_url(
    filename: str, s3_client: S3ClientDep, userid: UserIdHeaderDep
) -> str:
    url = s3_client.presigned_put_object(settings.s3.bucket, f"{userid}/{filename}")
    return url
