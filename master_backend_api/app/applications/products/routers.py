import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_queries import SearchParams
from applications.base_schemas import StatusSuccess
from applications.products.crud import category_manager, product_manager, order_manager, order_product_manager
from applications.products.models import Category, Product, OrderProduct, Order
from applications.products.schemas import (
    NewCategory,
    PaginationSavedCategoriesResponse,
    SavedCategory,
    SavedProduct,
    PaginationSavedProductsResponse,
    OrderSchema,
    AddRemoveOrderProductBodySchema,
)
from applications.users.models import User
from constants.messages import HelpTexts
from constants.permissions import UserPermissionsEnum
from dependencies.database import get_async_session
from dependencies.file_storage import validate_image, validate_images
from dependencies.security import require_permissions, get_current_user
from storage.s3 import s3_storage
from prometheus_client import Counter

router_categories = APIRouter()
router_products = APIRouter()
router_order = APIRouter()

custom_requests_categories_total = Counter(
    "custom_requests_categories_total", "Total requests to /api/products/categories"
)


@router_order.get("/")
async def get_current_order(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
) -> OrderSchema:
    order = await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
    return order


@router_order.post("/addProduct")
async def add_product_to_order(
    product_data: AddRemoveOrderProductBodySchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> OrderSchema:
    """Add product to order. If product already in order - we will increase it quantity. Always applies current price"""
    product = await product_manager.get_item(field=Product.id, field_value=product_data.product_id, session=session)
    if not product:
        raise HTTPException(
            detail=f"Product with id {product_data.product_id} not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    order: Order = await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
    await order_product_manager.set_quantity_and_price(
        product=product, order_id=order.id, quantity=product_data.quantity, session=session
    )
    order: Order = await order_manager.get_order_with_product(order_id=order.id, session=session)

    return order


@router_order.post("/decreaseRemoveProduct")
async def decrease_remove_product_from_order(
    product_data: AddRemoveOrderProductBodySchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> OrderSchema:
    product = await product_manager.get_item(field=Product.id, field_value=product_data.product_id, session=session)
    if not product:
        raise HTTPException(
            detail=f"Product with id {product_data.product_id} not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    order: Order = await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
    decrease_quantity = product_data.quantity * -1
    await order_product_manager.set_quantity_and_price(
        product=product, order_id=order.id, quantity=decrease_quantity, session=session
    )
    order: Order = await order_manager.get_order_with_product(order_id=order.id, session=session)

    return order


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
    result = await category_manager.get_items_paginated(
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
    has_product = await product_manager.any_item_exists(
        field=Product.category_id, field_value=category_id, session=session
    )
    if has_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Products with category #{category_id} exists",
        )

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

    created_product = await product_manager.create_instance(
        title=title.strip(),
        price=price,
        images=images_urls,
        main_image=main_image_url,
        category_id=category.id,
        session=session,
    )
    return SavedProduct.from_orm(created_product)


@router_products.get("/")
async def get_products(
    params: Annotated[SearchParams, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginationSavedProductsResponse:

    result = await product_manager.get_items_paginated(
        params=params,
        search_fields=[Product.title],
        targeted_schema=SavedProduct,
        session=session,
    )
    return result


@router_products.get("/{id}")
async def get_product(
    product_id: int = Path(..., description=HelpTexts.ITEM_PATH_ID_PARAM, ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProduct:

    product = await product_manager.get_item(field=Product.id, field_value=product_id, session=session)
    if not product:
        raise HTTPException(
            detail=f"Product with id #{product_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SavedProduct.from_orm(product)
