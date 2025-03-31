import io
from typing import AsyncGenerator

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from settings import settings


class S3Storage:
    def __init__(self):
        self.bucket_name = settings.S3_DEFAULT_BUCKET_NAME

    async def get_s3_session(self) -> AsyncGenerator[aioboto3.Session.client, None]:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION_NAME,
        ) as s3:
            yield s3

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        async for s3_client in self.get_s3_session():
            file.file.seek(0)  # because of validate_image - it has read file
            try:
                await s3_client.upload_fileobj(file, self.bucket_name, object_name)
                return f"{settings.S3_PUBLIC_BUCKET_URL}/{object_name}"
            except ClientError as e:
                print(f"An error occurred: {e}")
                raise Exception

    async def upload_image(self, file: UploadFile, uuid_id: str, root_dir: str = "productImages") -> str:
        file_name = f"{root_dir}/{uuid_id}/{file.filename}"
        url = await self.upload_file(file, file_name)
        return url


s3_storage = S3Storage()
