from celery import Celery
from .config import Config, load_config

cfg: Config = load_config()

app = Celery(
    "gpn",
    broker=cfg.redis_url,  # адрес брокера сообщений
    result_backend=cfg.redis_url,
    include=["app.tasks"],  # путь к модулю с задачами Celery
)
