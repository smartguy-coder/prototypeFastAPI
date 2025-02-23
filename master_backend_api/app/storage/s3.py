import boto3
from fastapi import UploadFile

from settings import settings


class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            # region_name="us-east-1",  # nor required yet for local dev
        )

    async def upload_file(
        self,
        file: UploadFile,
        object_name: str,
        bucket_name: str = settings.S3_DEFAULT_BUCKET_NAME,
    ) -> str:
        file.file.seek(0)
        file_content = file.file.read()
        self.s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=file_content)
        return f"{bucket_name}/{object_name}"

    async def upload_image(self, file: UploadFile, uuid_id: str, root_dir: str = "productImages") -> str:
        file_name = f"{root_dir}/{uuid_id}/{file.filename}"
        url = await self.upload_file(file, file_name)
        return url


s3_storage = S3Storage()
