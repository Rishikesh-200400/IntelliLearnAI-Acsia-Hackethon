"""
Direct data loading script for IntelliLearn AI
"""
import sqlite3
import pandas as pd
from pathlib import Path

def load_data():
    # Database file path
    db_path = "database.db"
    data_dir = Path("data/sample")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    try:
        # Load employees
        print("Loading employees...")
        employees_df = pd.read_csv(data_dir / "employees.csv")
        employees_df.to_sql('employees', conn, if_exists='replace', index=False)
        
        # Load skills
        print("Loading skills...")
        skills_df = pd.read_csv(data_dir / "skills.csv")
        skills_df.to_sql('skills', conn, if_exists='replace', index=False)
        
        # Load employee skills
        print("Loading employee skills...")
        emp_skills_df = pd.read_csv(data_dir / "employee_skills.csv")
        emp_skills_df.to_sql('employee_skills', conn, if_exists='replace', index=False)
        
        # Load courses
        print("Loading courses...")
        courses_df = pd.read_csv(data_dir / "courses.csv")
        courses_df.to_sql('courses', conn, if_exists='replace', index=False)
        
        # Load training history
        print("Loading training history...")
        training_df = pd.read_csv(data_dir / "training_history.csv")
        training_df.to_sql('trainings', conn, if_exists='replace', index=False)
        
        print("\nData loaded successfully!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("DIRECT DATA LOADING SCRIPT")
    print("="*60)
    load_data()
    print("\n" + "="*60)
    print("DATABASE POPULATION COMPLETE!")
    print("="*60)
