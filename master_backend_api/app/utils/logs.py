import logging
import json
from elasticsearch import Elasticsearch
from datetime import datetime


# Підключення до Elasticsearch
es = Elasticsearch("http://elasticsearch:9200", basic_auth=("elastic", "changeme"))


class ElasticsearchHandler(logging.Handler):
    def __init__(self, es_host="http://elasticsearch:9200"):
        super().__init__()
        self.es = Elasticsearch(es_host)  # Ініціалізуємо підключення

    def emit(self, record):
        try:
            log_entry_str = self.format(record)  # Отримуємо рядок
            print(f"{log_entry_str=}")  # Дебаг

            # ✅ Перетворюємо рядок у JSON
            log_entry = json.loads(log_entry_str)
            print(f"{log_entry=}")
            self.es.index(index=f"fastapi-logs-{datetime.now().strftime('%Y-%m-%d')}", document=log_entry)

        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")  # Відловлюємо помилки


logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.INFO)
es_handler = ElasticsearchHandler()
formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
es_handler.setFormatter(formatter)
logger.addHandler(es_handler)
# curl -X GET "127.0.0.1:9200/fastapi-logs-*/_search?pretty"
# curl -XGET http://localhost:9200/
