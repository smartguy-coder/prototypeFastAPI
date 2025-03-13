from fastapi import Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from applications.products.crud import product_manager
from applications.products.models import Product

from dependencies.database import get_async_session


async def get_product(
    product_id: int = Body(ge=1, description="It is Product id, not OrderProduct id"),
    session: AsyncSession = Depends(get_async_session),
) -> Product:
    product = await product_manager.get_item(field=Product.id, field_value=product_id, session=session)
    if not product:
        raise HTTPException(
            detail=f"Product with id {product_id} not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return product
