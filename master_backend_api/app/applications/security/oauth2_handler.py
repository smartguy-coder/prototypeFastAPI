# from settings import settings
#
#
# class SecurityHandler:
#     oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
#
#     @classmethod
#     async def get_current_user(
#         cls,
#         token: str = Depends(oauth2_scheme),
#         session: AsyncSession = Depends(get_async_session),
#     ):
#         payload = await AuthHandler.decode_token(token)
#         user = await dao.get_user_by_email(email=payload.get("email"), session=session)
#         if user:
#             return user
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User unknown"
#         )
