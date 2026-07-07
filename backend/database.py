import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_connection():
    """
    Create and return a new database connection.
    Uses RealDictCursor so query results come back as dictionaries
    instead of tuples — easier to work with in Flask APIs.
    """
    try:
        connection = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )
        return connection
    except Exception as e:
        print(f"[DB ERROR] Could not connect to database: {e}")
        raise e


def close_connection(connection, cursor=None):
    """
    Safely close cursor and connection.
    Always call this after database operations to avoid memory leaks.
    """
    if cursor:
        cursor.close()
    if connection:
        connection.close()
