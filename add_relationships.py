import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Add employee-skill relationships
print("Adding employee-skill relationships...")
for emp_id in range(1, 51):  # 50 employees
    # Each employee has 3-8 skills
    num_skills = random.randint(3, 8)
    skills = random.sample(range(1, 21), num_skills)  # 20 skills total
    
    for skill_id in skills:
        proficiency = random.randint(1, 5)
        years_exp = round(random.uniform(0.5, 8.0), 1)
        c.execute('''
            INSERT OR IGNORE INTO employee_skills 
            (employee_id, skill_id, proficiency_level, years_of_experience, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (emp_id, skill_id, proficiency, years_exp))

conn.commit()
print(f"[OK] Added employee-skill relationships")

# Add training records
print("Adding training records...")
for i in range(150):  # 150 training records
    emp_id = random.randint(1, 50)
    course_id = random.randint(1, 20)
    days_ago = random.randint(1, 365)
    status = random.choice(['completed', 'in_progress', 'completed', 'completed'])  # More completed
    score = round(random.uniform(65, 98), 1) if status == 'completed' else None
    
    c.execute('''
        INSERT INTO trainings 
        (employee_id, course_id, completion_date, status, score, created_at, updated_at)
        VALUES (?, ?, date('now', '-' || ? || ' days'), ?, ?, datetime('now'), datetime('now'))
    ''', (emp_id, course_id, days_ago, status, score))

conn.commit()
print(f"[OK] Added training records")

# Verify counts
c.execute("SELECT COUNT(*) FROM employee_skills")
emp_skills_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trainings")
trainings_count = c.fetchone()[0]

conn.close()

print("\n" + "="*60)
print("DATA ADDED SUCCESSFULLY!")
print("="*60)
print(f"\nDatabase now has:")
print(f"  - Employee-Skill relationships: {emp_skills_count}")
print(f"  - Training records: {trainings_count}")
print("\nYou can now:")
print("  1. Start backend: python app.py")
print("  2. Refresh Analytics page")
print()
