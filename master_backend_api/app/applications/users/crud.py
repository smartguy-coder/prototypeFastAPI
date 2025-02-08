from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_crud import BaseCRUD
from applications.users.models import User


class UserDBManager(BaseCRUD):

    def __init__(self):
        self.model = User

    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
        session: AsyncSession,
    ) -> User:
        user = self.model(email=email, name=name, hashed_password=hashed_password)
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                detail=f"Error has occurred while creating User with email {email}, probably already exists",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
