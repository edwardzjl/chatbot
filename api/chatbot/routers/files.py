from fastapi import APIRouter

from chatbot.dependencies import S3ClientDep, UserIdHeaderDep
from chatbot.dependencies.commons import SettingsDep


router = APIRouter(prefix="/files")


@router.get("/upload-url")
def get_presigned_url(
    filename: str,
    s3_client: S3ClientDep,
    settings: SettingsDep,
    userid: UserIdHeaderDep,
) -> str:
    url = s3_client.presigned_put_object(settings.s3.bucket, f"{userid}/{filename}")
    return url
