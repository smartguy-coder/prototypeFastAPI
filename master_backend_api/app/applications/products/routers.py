import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_queries import SearchParams
from applications.base_schemas import StatusSuccess
from applications.products.crud import category_manager, product_manager
from applications.products.models import Category, Product
from applications.products.schemas import NewCategory, PaginationSavedCategoriesResponse, SavedCategory, SavedProduct
from constants.messages import HelpTexts
from constants.permissions import UserPermissionsEnum
from dependencies.database import get_async_session
from dependencies.file_storage import validate_image, validate_images
from dependencies.security import require_permissions
from storage.s3 import s3_storage
from prometheus_client import Counter

router_categories = APIRouter()
router_products = APIRouter()

custom_requests_categories_total = Counter(
    "custom_requests_categories_total", "Total requests to /api/products/categories"
)


@router_categories.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))],
)
async def create_category(
    new_category: NewCategory,
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:
    maybe_category: Category | None = await category_manager.get_item(
        field=Category.name, field_value=new_category.name, session=session
    )
    if maybe_category:
        raise HTTPException(
            detail=f"Category {maybe_category.name} already exists",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    saved_category = await category_manager.create_instance(name=new_category.name, session=session)

    return SavedCategory.from_orm(saved_category)


@router_categories.get("/{id}")
async def get_category(
    category_id: int = Path(..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:

    category = await category_manager.get_item(field=Category.id, field_value=category_id, session=session)
    if not category:
        raise HTTPException(
            detail=f"Category with id #{category_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SavedCategory.from_orm(category)


@router_categories.get("/")
async def get_categories(
    params: Annotated[SearchParams, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginationSavedCategoriesResponse:
    custom_requests_categories_total.inc()
    result = await category_manager.get_items(
        params=params,
        search_fields=[Category.name],
        targeted_schema=SavedCategory,
        session=session,
    )
    return result


@router_categories.patch(
    "/{id}",
    dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))],
)
async def update_category(
    category_data: NewCategory,
    category_id: int = Path(..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategory:
    category_updated = await category_manager.patch_item(category_id, data_to_patch=category_data, session=session)
    return SavedCategory.from_orm(category_updated)


@router_categories.delete(
    "/{id}",
    dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT_CATEGORY]))],
)
async def delete_category(
    category_id: int = Path(..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> StatusSuccess:
    # todo check deleting with products in it
    await category_manager.delete_item(category_id, session=session)
    return StatusSuccess()


@router_products.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[
    #     Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT]))
    # ],
)
async def create_product(
    # cannot use pydantic model in multipart/form-data with UploadFile in body (just in query, but here - post request)
    title: str = Body(min_length=3, max_length=256),
    price: float = Body(ge=0.01),
    categoryId: int = Body(gt=0),
    main_image: UploadFile = Depends(validate_image),
    images: list[UploadFile] = Depends(validate_images),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProduct:
    # base validation part
    category = await category_manager.get_item(field=Category.id, field_value=categoryId, session=session)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category #{categoryId} does not exist",
        )

    product = await product_manager.get_item(field=Product.title, field_value=title.strip(), session=session)
    if product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with given title already created (#{product.id})",
        )
    # processing
    product_uuid = uuid.uuid4().hex
    try:
        main_image_url = await s3_storage.upload_image(file=main_image, uuid_id=product_uuid)
        images_urls = []
        for image in images:
            image_url = await s3_storage.upload_image(file=image, uuid_id=product_uuid)
            images_urls.append(image_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=f"Failed to upload image: {e}",
        )
    print(main_image_url)
    print(images_urls)

    created_product = await product_manager.create_instance(
        title=title.strip(),
        price=price,
        images=images_urls,
        main_image=main_image_url,
        category_id=category.id,
        session=session,
    )
    print(created_product)
    return SavedProduct.from_orm(created_product)
