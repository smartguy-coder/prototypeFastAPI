import httpx

from services.api_constants import URLS
from settings import settings


async def call_main_api(
    endpoint: URLS, params: dict, path_id="", access_token=""
) -> dict:

    async with httpx.AsyncClient() as client:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        try:
            response = await client.get(
                f"{settings.BASE_URL}/api/{endpoint}/{path_id}",
                params=params,
                headers=headers,
            )
            print(response.status_code)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
        return {}


async def call_main_api_create_user(form_obj) -> dict:

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.PUBLIC_URL}/api/{URLS.USERS}/create",
                json={
                    "name": form_obj.name,
                    "email": form_obj.email,
                    "password": form_obj.password,
                },
            )
            print(response.status_code)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
        return {}


async def get_user_by_access_token(access_token):
    async with httpx.AsyncClient() as client:
        try:
            response_user = await client.get(
                f"{settings.BASE_URL}/api/users/me",
                params={},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response_user.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {}

    user = response_user.json()
    return user


async def get_new_token_pair(refresh_token):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.BASE_URL}/api/auth/refresh",
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
                f"{settings.BASE_URL}/api/auth/login",
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


async def force_logout_user(access_token):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.BASE_URL}/api/auth/force-logout",
                headers={"Authorization": f"Bearer {access_token}"},
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


async def add_product_to_cart_request(quantity, product_id, access_token):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{settings.BASE_URL}/api/orders/addProduct",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"quantity": quantity, "product_id": product_id},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {}
    return response.json()


async def change_product_quantity_request(product_id, action, access_token):
    payload = {"quantity": 1, "product_id": product_id}

    if action == "increase":
        url = f"{settings.BASE_URL}/api/orders/addProduct"
    elif action == "decrease":
        url = f"{settings.BASE_URL}/api/orders/decreaseRemoveProduct"
    elif action == "delete":
        url = f"{settings.BASE_URL}/api/orders/decreaseRemoveProduct"
        payload |= {"is_set_quantity": True, "quantity": 0}
    else:
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                url=url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {}
    return response.json()
