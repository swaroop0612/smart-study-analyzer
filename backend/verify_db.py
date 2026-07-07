"""
Verify Database Setup
Confirms that tables and data exist in the database.
"""
from database import get_connection, close_connection


def verify_database():
    """Check if tables exist and data is loaded."""
    conn = None
    cur = None
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print("\n📋 Tables in database:")
        for table in tables:
            print(f"   ✓ {table['table_name']}")
        
        # Check sample data
        cur.execute("SELECT COUNT(*) AS count FROM study_sessions;")
        count = cur.fetchone()['count']
        
        print(f"\n📊 Total study sessions in database: {count}")
        
        # Show sample data
        cur.execute("""
            SELECT student_name, study_date, subject, study_hours, focus_rating 
            FROM study_sessions 
            ORDER BY study_date 
            LIMIT 5;
        """)
        rows = cur.fetchall()
        
        print("\n📝 Sample data:")
        print("-" * 80)
        print(f"{'Name':<15} {'Date':<12} {'Subject':<15} {'Hours':<8} {'Focus':<6}")
        print("-" * 80)
        for row in rows:
            print(f"{row['student_name']:<15} {str(row['study_date']):<12} "
                  f"{row['subject']:<15} {row['study_hours']:<8} {row['focus_rating']:<6}")
        print("-" * 80)
        
        print("\n✅ Database is ready!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    finally:
        close_connection(conn, cur)


if __name__ == "__main__":
    verify_database()
