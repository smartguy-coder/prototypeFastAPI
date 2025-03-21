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
