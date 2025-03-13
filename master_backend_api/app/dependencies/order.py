from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from applications.products.crud import order_manager
from applications.products.models import Order
from applications.users.models import User
from dependencies.database import get_async_session
from dependencies.security import get_current_user


async def get_order(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
) -> Order:
    """Залежність для отримання відкритого замовлення"""
    return await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
