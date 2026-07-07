"""
Database Setup Script
Run this once to create all tables in your Neon database.
"""
import os
from database import get_connection, close_connection


def setup_database():
    """Read schema.sql and execute it on the database."""
    conn = None
    cur = None
    
    try:
        # Get connection
        conn = get_connection()
        cur = conn.cursor()
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
        
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # Execute schema
        print("📦 Running schema.sql...")
        cur.execute(schema_sql)
        
        # Commit the transaction
        conn.commit()
        
        print("✅ Database schema created successfully!")
        print("✅ Sample data inserted!")
        print("✅ You're ready to build the backend APIs!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        if conn:
            conn.rollback()
    
    finally:
        close_connection(conn, cur)


if __name__ == "__main__":
    setup_database()
