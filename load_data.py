"""
Simple script to load sample data into database
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Database file
DB_FILE = "intellilearn.db"
DATA_DIR = Path("data/sample")

def create_tables():
    """Create database tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        role TEXT,
        job_level TEXT,
        years_of_experience REAL,
        hire_date TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Create skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        description TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Create employee_skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        proficiency_level INTEGER,
        years_of_experience REAL,
        last_assessed TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (skill_id) REFERENCES skills(id),
        UNIQUE(employee_id, skill_id)
    )
    """)
    
    # Create courses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        provider TEXT,
        duration_hours INTEGER,
        difficulty_level TEXT,
        url TEXT,
        category TEXT,
        description TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Create trainings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trainings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrollment_date TEXT,
        completion_date TEXT,
        status TEXT,
        score REAL,
        feedback TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Tables created")

def load_data():
    """Load sample data from CSV files"""
    conn = sqlite3.connect(DB_FILE)
    
    # Check if data already exists
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"\n[SKIP] Database already has {count} employees")
        print("To reload, delete database.db first")
        conn.close()
        return
    
    print("\n[LOADING] Importing sample data...")
    
    # Load employees
    employees_df = pd.read_csv(DATA_DIR / "employees.csv")
    for idx, row in employees_df.iterrows():
        cursor.execute("""
            INSERT INTO employees (employee_id, name, email, department, role, years_of_experience, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            f"EMP{str(idx+1).zfill(4)}",
            row['name'],
            row['email'],
            row['department'],
            row['role'],
            float(row['years_of_experience'])
        ))
    conn.commit()
    print(f"[OK] Loaded {len(employees_df)} employees")
    
    # Load skills
    skills_df = pd.read_csv(DATA_DIR / "skills.csv")
    for _, row in skills_df.iterrows():
        cursor.execute("""
            INSERT INTO skills (name, category, description, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (
            row['name'],
            row['category'],
            row.get('description', '')
        ))
    conn.commit()
    print(f"[OK] Loaded {len(skills_df)} skills")
    
    # Load employee_skills
    emp_skills_df = pd.read_csv(DATA_DIR / "employee_skills.csv")
    loaded_emp_skills = 0
    for _, row in emp_skills_df.iterrows():
        try:
            emp_id = int(row['employee_id'])
            skill_id = int(row['skill_id'])
            
            # Check if this relationship already exists or if IDs are valid
            cursor.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (emp_id,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("SELECT COUNT(*) FROM skills WHERE id = ?", (skill_id,))
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        INSERT OR IGNORE INTO employee_skills (employee_id, skill_id, proficiency_level, years_of_experience, created_at, updated_at)
                        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (
                        emp_id,
                        skill_id,
                        int(row['proficiency_level']),
                        float(row.get('years_of_experience', 0))
                    ))
                    loaded_emp_skills += 1
        except (ValueError, KeyError) as e:
            # Skip invalid rows
            continue
    conn.commit()
    print(f"[OK] Loaded {loaded_emp_skills} employee-skill relationships")
    
    # Load courses
    courses_df = pd.read_csv(DATA_DIR / "courses.csv")
    for _, row in courses_df.iterrows():
        cursor.execute("""
            INSERT INTO courses (title, provider, duration_hours, difficulty_level, url, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            row['title'],
            row['provider'],
            int(row['duration_hours']),
            row['difficulty_level'],
            row.get('url', ''),
            row['category']
        ))
    conn.commit()
    print(f"[OK] Loaded {len(courses_df)} courses")
    
    # Load trainings
    trainings_df = pd.read_csv(DATA_DIR / "training_history.csv")
    loaded_trainings = 0
    for _, row in trainings_df.iterrows():
        try:
            emp_id = int(row['employee_id'])
            course_id = int(row['course_id'])
            
            # Validate IDs exist
            cursor.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (emp_id,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("SELECT COUNT(*) FROM courses WHERE id = ?", (course_id,))
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        INSERT INTO trainings (employee_id, course_id, completion_date, status, score, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (
                        emp_id,
                        course_id,
                        row['completion_date'],
                        row['status'],
                        float(row['score']) if pd.notna(row.get('score')) else None
                    ))
                    loaded_trainings += 1
        except (ValueError, KeyError) as e:
            continue
    conn.commit()
    print(f"[OK] Loaded {loaded_trainings} training records")
    
    conn.close()
    
    print("\n" + "="*60)
    print("DATABASE LOADED SUCCESSFULLY!")
    print("="*60)
    print(f"\nTotal records:")
    print(f"  - {len(employees_df)} Employees")
    print(f"  - {len(skills_df)} Skills")
    print(f"  - {loaded_emp_skills} Employee-Skill relationships")
    print(f"  - {len(courses_df)} Courses")
    print(f"  - {loaded_trainings} Training records")
    print("\nNow start the backend server:")
    print("  python app.py")
    print("\nThen refresh the Analytics page in your browser!")
    print()

if __name__ == "__main__":
    try:
        print("="*60)
        print("LOADING SAMPLE DATA INTO DATABASE")
        print("="*60)
        create_tables()
        load_data()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
