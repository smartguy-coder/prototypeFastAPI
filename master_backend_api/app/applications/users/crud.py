import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from applications.auth.password_handler import PasswordEncrypt
from applications.base_crud import BaseCRUD
from applications.users.models import User
from applications.users.schemas import UserHashedPassword
from settings import settings


class UserDBManager(BaseCRUD):

    def __init__(self):
        self.model = User

    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        session: AsyncSession,
        is_active: bool = True,
        is_verified: bool = False,
        is_admin: bool = False,
        notes: str = "",
    ) -> User:

        hashed_password = await PasswordEncrypt.get_password_hash(password)
        user = self.model(
            email=email,
            name=name,
            hashed_password=hashed_password,
            notes=notes,
            is_verified=is_verified,
            is_admin=is_admin,
            is_active=is_active,
        )
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

    async def create_admin(self, session: AsyncSession):
        admin = await self.get_item(
            field=User.email,
            field_value=settings.DEFAULT_ADMIN_USER_EMAIL,
            session=session,
        )
        if not admin:
            await self.create_user(
                name=settings.DEFAULT_ADMIN_USER_NAME,
                email=settings.DEFAULT_ADMIN_USER_EMAIL,
                password=settings.DEFAULT_ADMIN_USER_PASSWORD,
                is_verified=True,
                is_admin=True,
                notes="system created user",
                session=session,
            )

    async def activate_user_account(self, user_uuid: uuid.UUID, session: AsyncSession) -> User:
        user = await self.get_item(field=self.model.uuid_data, field_value=user_uuid, session=session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data for account activation is not correct",
            )
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link was used already")

        user.is_verified = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def change_user_password(self, user_id: int, new_password: str, session: AsyncSession):
        hashed_password = await PasswordEncrypt.get_password_hash(new_password)
        schema = UserHashedPassword(hashed_password=hashed_password)
        await self.patch_item(instance_id=user_id, data_to_patch=schema, session=session)


user_manager = UserDBManager()
