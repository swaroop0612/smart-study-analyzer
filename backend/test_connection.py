from database import get_connection, close_connection


def test_db_connection():
    """Quick test to verify Neon database connection works."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Run a simple test query
        cur.execute("SELECT version();")
        version = cur.fetchone()

        print("✅ Database connected successfully!")
        print(f"📊 PostgreSQL version: {version['version']}")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    finally:
        close_connection(conn, cur)


if __name__ == "__main__":
    test_db_connection()
