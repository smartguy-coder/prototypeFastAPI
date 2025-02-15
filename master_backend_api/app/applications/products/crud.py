from applications.products.models import Category
from applications.base_crud import BaseCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from sqlalchemy.exc import IntegrityError


class CategoryDBManager(BaseCRUD):

    def __init__(self):
        self.model = Category

    async def create_category(self, name: str, session: AsyncSession) -> Category:

        category = self.model(name=name)
        session.add(category)
        try:
            await session.commit()
            await session.refresh(category)
            return category
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                detail=f"Error has occurred while creating Category with name {name}, probably already exists",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


category_manager = CategoryDBManager()
