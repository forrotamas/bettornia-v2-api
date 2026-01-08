from contextlib import contextmanager
import psycopg
from app.core.config import settings

@contextmanager
def get_conn():
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not set")
    with psycopg.connect(settings.database_url) as conn:
        yield conn
