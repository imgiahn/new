import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    """dict 형태로 결과를 돌려주는 새 DB 커넥션."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
