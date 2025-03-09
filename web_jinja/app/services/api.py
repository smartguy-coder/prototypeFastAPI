import httpx

from services.api_constants import URLS
from settings import settings


async def call_main_api(endpoint: URLS):
    """
    https://chatgpt.com/share/67cdf873-75d4-8004-9a24-b78b096e5be3

    Можна виконати запит через сокет з всередини контейнера master-backend-api  за допомогою curl:

        curl --unix-socket /app/tmp_uds/master-backend.sock http://localhost/api/categories/
        Якщо цей запит успішно повертає відповідь, це підтверджує, що сокет працює і використовується правильно.

    Якщо ви хочете перевірити, чи web-jinja контейнер правильно використовує UDS для комунікації з master-backend-api, переконайтеся, що вказаний шлях до сокета (/app/tmp_uds/master-backend.sock) доступний у відповідній мережі контейнерів. Ви можете зробити запит з іншого контейнера:

        curl --unix-socket /app/tmp_uds/master-backend.sock http://localhost/api/categories/

    """

    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(uds=settings.UDS_PATH),
        base_url=settings.UDS_BASE_URL,
    ) as client:
        try:
            response = await client.get(f"/api/{endpoint}/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
        return None
