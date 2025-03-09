import logging
import json
from elasticsearch import Elasticsearch
from datetime import datetime


# Підключення до Elasticsearch
# es = Elasticsearch("http://elasticsearch:9200", basic_auth=("elastic", "changeme"))


class ElasticsearchHandler(logging.Handler, logging.Formatter):
    def __init__(self, es_host="http://elasticsearch:9200"):
        super().__init__()
        self.es = Elasticsearch(es_host)  # Ініціалізуємо підключення

    def format(self, record):
        """Форматуємо запис у формат JSON"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),  # Час запису у форматі ISO
            "level": record.levelname,  # Рівень логування (INFO, ERROR, і т.д.)
            "message": record.getMessage(),  # Повідомлення лога
            "logger": record.name,  # Назва логера
            "exception": None,  # Виключення, якщо є
            "extra": {
                k: str(v)
                for k, v in record.__dict__.items()
                # if k not in vars(logging.LogRecord("", "", "", "", "", "", "", "")).keys()
            },
        }

        # Якщо в записі є виключення, додаємо його
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)  # Перетворюємо словник у JSON рядок

    def emit(self, record):
        try:
            log_entry_str = self.format(record)  # Отримуємо рядок
            log_entry = json.loads(log_entry_str)
            self.es.index(index=f"fastapi-logs-{datetime.now().strftime('%Y-%m-%d')}", document=log_entry)

        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")  # Відловлюємо помилки


def get_logger(name="uvicorn.access", es_host="http://elasticsearch:9200"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Підключення ElasticsearchHandler
    es_handler = ElasticsearchHandler(es_host)
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
    es_handler.setFormatter(formatter)

    # Додаємо обробник до логера
    logger.addHandler(es_handler)

    return logger


# Використання функції для отримання логера
logger = get_logger()

# curl -X GET "127.0.0.1:9200/fastapi-logs-*/_search?pretty"
# http://127.0.0.1:9200/fastapi-*/_search?pretty&size=50&from=50
# curl -XGET http://localhost:9200/
