import httpx

from services.api_constants import URLS
from settings import settings


async def call_main_api(endpoint: URLS, params: dict, path_id=""):

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.UDS_BASE_URL}/api/{endpoint}/{path_id}", params=params
            )
            print(response.status_code)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
        return None


async def get_user_by_access_token(access_token):
    async with httpx.AsyncClient() as client:
        try:
            response_user = await client.get(
                f"{settings.UDS_BASE_URL}/api/users/me",
                params={},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response_user.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return None

    user = response_user.json()
    return user


async def get_new_token_pair(refresh_token):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.UDS_BASE_URL}/api/auth/refresh",
                headers={"X-Refresh-Token": refresh_token},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {}
    return response.json()


async def login_user(email, password):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.UDS_BASE_URL}/api/auth/login",
                data={"username": email, "password": password},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {}
    return response.json()


async def login_and_get_user_with_tokens(email, password) -> dict:
    tokens_response_json = await login_user(email, password)
    if not tokens_response_json:
        return {}
    user = await get_user_by_access_token(tokens_response_json["access_token"])
    user |= tokens_response_json

    return user
