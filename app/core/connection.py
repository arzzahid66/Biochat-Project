import psycopg2
from dotenv import load_dotenv
from app.core.config import settings



def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=settings.PG_HOST,
        database=settings.PG_NAME,
        user=settings.PG_USER_NAME,
        password=settings.PG_PASSWORD,
        port=settings.PG_PORT

    )
    return conn