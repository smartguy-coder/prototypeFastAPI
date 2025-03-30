from urllib.parse import urlparse

from settings import settings


def ensure_full_url(image: str) -> str:
    """Перевіряє, чи містить URL домен, і додає його за потреби."""
    parsed = urlparse(image)
    if not parsed.netloc:  # Якщо домен відсутній
        return f"{settings.WORK_URL}/{image.lstrip('/')}"
    return image
