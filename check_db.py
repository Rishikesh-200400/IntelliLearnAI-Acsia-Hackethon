import sqlite3
import os

def check_database():
    db_path = "database.db"
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' does not exist.")
        return
    
    print(f"Database file found at: {os.path.abspath(db_path)}")
    print(f"File size: {os.path.getsize(db_path) / 1024:.2f} KB")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("\nNo tables found in the database!")
        else:
            print("\nTables in the database:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                print("-" * 50)
                
                # Get column info
                try:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    print("Columns:")
                    for col in columns:
                        print(f"  {col[1]} ({col[2]})")
                    
                    # Count rows
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"\nNumber of rows: {count}")
                    
                    # Show first few rows
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                        rows = cursor.fetchall()
                        print("\nSample data:")
                        for row in rows:
                            print(f"  {row}")
                    
                except sqlite3.Error as e:
                    print(f"  Error reading table: {e}")
                
                print("\n" + "="*50)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("="*60)
    print("DATABASE INSPECTION TOOL")
    print("="*60)
    check_database()
