from typing import List

from fastapi import File, HTTPException, UploadFile, status

ALLOWED_IMAGE_FILE_TYPES = ["image/jpeg", "image/png", "image/gif"]


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def validate_image(mainImage: UploadFile = File(...)) -> File:

    if mainImage.content_type not in ALLOWED_IMAGE_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {mainImage.content_type}. "
            f"Allowed types: {', '.join(ALLOWED_IMAGE_FILE_TYPES)}.",
        )

    file_size = len(await mainImage.read())
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File is too large. Maximum allowed size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    return mainImage


async def validate_images(
    images: List[UploadFile] = File(default=[], max_length=10),
) -> List[UploadFile]:
    if len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can upload a maximum of 10 images.",
        )
    for image in images:
        await validate_image(image)
    return images
