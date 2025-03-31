import re
from transliterate import translit
from urllib.parse import urlparse
from fastapi import HTTPException

import unicodedata

from settings import settings


def ensure_full_url(image: str) -> str:
    """Перевіряє, чи містить URL домен, і додає його за потреби."""
    parsed = urlparse(image)
    if not parsed.netloc:  # Якщо домен відсутній
        return f"{settings.WORK_URL}/{image.lstrip('/')}"
    return image


async def sanitize_filename(filename: str) -> str:
    """
    Перетворює кирилицю в латиницю та прибирає всі небезпечні символи.
    """
    # Перевіряємо, чи є кирилиця
    if re.search(r"[а-яА-ЯёЁіІїЇєЄґҐ]", filename):
        filename = translit(filename, reversed=True)  # Транслітерація кирилиці → латиниця

    # Нормалізуємо текст (видаляємо діакритичні знаки)
    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")

    # Видаляємо всі символи, крім [a-zA-Z0-9._-]
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    if not filename:
        raise HTTPException(status_code=400, detail="Invalid filename after sanitization.")
    return filename
