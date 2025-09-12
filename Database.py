import sqlite3
import os

def show_database_info():
    # Check if database exists in instance folder
    db_path = 'instance/vms.db'
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    try:
        # Connect to the database file
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Show all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("Database exists but has no tables.")
            return
            
        print("Database Tables:")
        for table in tables:
            table_name = table[0]
            print(f"\n=== {table_name} ===")
            
            # Show table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Show first 5 rows for each table
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                if rows:
                    print("Sample rows:")
                    for row in rows:
                        print(f"  {row}")
                else:
                    print("  No data in table")
            except sqlite3.OperationalError as e:
                print(f"  Unable to fetch rows: {e}")
            
            print()  # Empty line for readability

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        # Always close the connection
        if conn:
            conn.close()

# Run the database info function
if __name__ == "__main__":
    show_database_info()
