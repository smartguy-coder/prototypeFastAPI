from services.api import login_and_get_user_with_tokens


class SecurityHandler:
    @classmethod
    async def authenticate_user_web(cls, email, password):
        try:
            user = await login_and_get_user_with_tokens(email, password)
        except Exception:
            return None
        return user

    @classmethod
    async def set_cookies(cls, user, response):
        if not user:
            # maybe there is an outdated refresh token
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        response.set_cookie(
            key="access_token",
            value=user["access_token"],
            httponly=True,
            max_age=60 * 4,
        )
        response.set_cookie(
            key="refresh_token",
            value=user["refresh_token"],
            httponly=True,
            max_age=60 * 60 * 24,  # day
        )

        return response
