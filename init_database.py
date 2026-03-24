"""
Quick script to initialize database and load sample data
"""
import os
import sys
import hashlib
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database import get_db, init_db, SessionLocal
from app.models.base import Employee, Skill, EmployeeSkill, Course, Training
from sqlalchemy import inspect

def drop_all_tables():
    """Drop all database tables."""
    print("Dropping all tables...")
    from app.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    print("[OK] All tables dropped")

def load_sample_data():
    """Load sample data from CSV files into database"""
    print("Dropping existing tables...")
    drop_all_tables()
    
    print("\nInitializing database tables...")
    init_db()
    print("[OK] Tables created")
    
    data_dir = Path("data/sample")
    
    db = SessionLocal()
    try:
        # Load Employees
        print("\nLoading employees...")
        employees_df = pd.read_csv(data_dir / "employees.csv")
        
        # Ensure required columns exist
        required_columns = ['name', 'email', 'role', 'department', 'years_of_experience']
        if not all(col in employees_df.columns for col in required_columns):
            print("Error: Missing required columns in employees.csv")
            return
        
        # Check if employees already exist
        existing_count = db.query(Employee).count()
        if existing_count > 0:
            print(f"[SKIP] Database already has {existing_count} employees")
        else:
            for counter, (_idx, row) in enumerate(employees_df.iterrows(), start=1):
                try:
                    emp = Employee(
                        employee_id=f"EMP{str(counter).zfill(4)}",  # Generate EMP0001, EMP0002, etc.
                        name=row['name'],
                        email=row['email'],
                        role=row['role'],
                        department=row['department'],
                        years_of_experience=int(row['years_of_experience'])
                    )
                    db.add(emp)
                except Exception as e:
                    print(f"Error adding employee {row.get('name', 'Unknown')}: {e}")
                    db.rollback()
                    continue
            
            try:
                db.commit()
                print(f"[OK] Loaded {len(employees_df)} employees")
            except Exception as e:
                print(f"Error committing employees: {e}")
                db.rollback()
        
        # Load Skills
        print("\nLoading skills...")
        skills_df = pd.read_csv(data_dir / "skills.csv")
        for _, row in skills_df.iterrows():
            skill = Skill(
                name=row['name'],
                category=row['category'],
                description=row.get('description', '')
            )
            db.add(skill)
        db.commit()
        print(f"[OK] Loaded {len(skills_df)} skills")
        
        # Load Employee Skills
        print("\nLoading employee-skill relationships...")
        try:
            emp_skills_df = pd.read_csv(data_dir / "employee_skills.csv")
            print(f"Found {len(emp_skills_df)} employee-skill relationships in CSV")
            
            # Get all employees and skills to map names to IDs
            employees = {emp.employee_id: emp.id for emp in db.query(Employee).all()}
            skills = {skill.name.lower(): skill.id for skill in db.query(Skill).all()}  # Case-insensitive matching
            
            print(f"Found {len(employees)} employees and {len(skills)} skills in database")
            
            # Counters for stats
            success_count = 0
            missing_skill = 0
            missing_employee = 0
            
            for _, row in emp_skills_df.iterrows():
                try:
                    # Get employee ID
                    emp_id = str(row['employee_id']).strip()
                    if emp_id not in employees:
                        print(f"Warning: Employee {emp_id} not found in database")
                        missing_employee += 1
                        continue
                        
                    # Get skill ID by name (case-insensitive)
                    skill_name = str(row['skill_name']).strip().lower()
                    if skill_name not in skills:
                        print(f"Warning: Skill '{skill_name}' not found in database")
                        missing_skill += 1
                        continue
                        
                    # Create employee-skill relationship
                    emp_skill = EmployeeSkill(
                        employee_id=employees[emp_id],
                        skill_id=skills[skill_name],
                        proficiency_level=float(row['proficiency_level']),
                        last_assessed=pd.to_datetime(row['last_assessed']) if pd.notna(row.get('last_assessed')) else None,
                        assessment_method=row.get('assessment_method')
                    )
                    db.add(emp_skill)
                    success_count += 1
                    
                    # Commit in batches of 100
                    if success_count % 100 == 0:
                        db.commit()
                        print(f"Committed {success_count} employee-skill relationships...")
                        
                except Exception as e:
                    print(f"Error processing employee-skill relationship: {e}")
                    db.rollback()
                    continue
            
            # Final commit
            db.commit()
            print(f"[OK] Successfully loaded {success_count} employee-skill relationships")
            if missing_employee > 0:
                print(f"Warning: {missing_employee} relationships skipped due to missing employees")
            if missing_skill > 0:
                print(f"Warning: {missing_skill} relationships skipped due to missing skills")
                
        except FileNotFoundError:
            print("Error: employee_skills.csv not found in data/sample/ directory")
        except Exception as e:
            print(f"Error loading employee-skill relationships: {e}")
            db.rollback()
        
        # Load Courses
        print("\nLoading courses...")
        try:
            courses_df = pd.read_csv(data_dir / "courses.csv")
            print(f"Found {len(courses_df)} courses in CSV")
            
            # Ensure required columns exist
            required_columns = ['title', 'provider', 'duration_hours', 'difficulty_level', 'category']
            if not all(col in courses_df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in courses_df.columns]
                print(f"Error: Missing required columns in courses.csv: {', '.join(missing)}")
                return
            
            success_count = 0
            
            for _, row in courses_df.iterrows():
                try:
                    # Generate a unique course_id from the title
                    title_slug = str(row['title']).lower().replace(' ', '-').replace('/', '-')
                    course_hash = hashlib.md5(title_slug.encode()).hexdigest()[:8]
                    course_id = f"course-{course_hash}"
                    
                    # Create course with all required fields
                    course = Course(
                        course_id=course_id,
                        title=row['title'],
                        provider=row['provider'],
                        duration_hours=float(row['duration_hours']) if pd.notna(row['duration_hours']) else None,
                        difficulty_level=row['difficulty_level'],
                        category=row['category'],
                        url=row.get('url'),
                        description=row.get('description'),
                        cost=float(row['cost']) if 'cost' in row and pd.notna(row['cost']) else None,
                        rating=float(row['rating']) if 'rating' in row and pd.notna(row['rating']) else None
                    )
                    db.add(course)
                    success_count += 1
                    
                    # Commit in batches of 20
                    if success_count % 20 == 0:
                        db.commit()
                        print(f"Committed {success_count} courses...")
                        
                except Exception as e:
                    print(f"Error adding course '{row.get('title')}': {e}")
                    db.rollback()
                    continue
            
            # Final commit
            db.commit()
            print(f"[OK] Successfully loaded {success_count} courses")
            
        except FileNotFoundError:
            print("Error: courses.csv not found in data/sample/ directory")
        except Exception as e:
            print(f"Error loading courses: {e}")
            db.rollback()
        
        # Load Training History
        print("\nLoading training history...")
        try:
            trainings_df = pd.read_csv(data_dir / "training_history.csv")
            print(f"Found {len(trainings_df)} training records in CSV")
            
            # Get all employees and courses to map IDs
            employees = {emp.employee_id: emp.id for emp in db.query(Employee).all()}
            courses = {course.course_id: course.id for course in db.query(Course).all()}
            
            success_count = 0
            
            for _, row in trainings_df.iterrows():
                try:
                    # Handle employee_id (could be integer or EMP0001 format)
                    emp_id = str(row['employee_id']).strip()
                    if emp_id not in employees:
                        print(f"Warning: Employee {emp_id} not found in database")
                        continue
                        
                    # Handle course_id (could be integer or course ID string)
                    course_id = str(row['course_id']).strip()
                    if course_id not in courses:
                        print(f"Warning: Course ID {course_id} not found in database")
                        continue
                        
                    training = Training(
                        employee_id=employees[emp_id],
                        course_id=courses[course_id],
                        completion_date=pd.to_datetime(row['completion_date']) if pd.notna(row.get('completion_date')) else None,
                        status=row['status'],
                        progress_percentage=float(row.get('progress_percentage', 100)) if pd.notna(row.get('progress_percentage')) else 100,
                        assessment_score=float(row['assessment_score']) if 'assessment_score' in row and pd.notna(row['assessment_score']) else None,
                        feedback_rating=float(row['feedback_rating']) if 'feedback_rating' in row and pd.notna(row['feedback_rating']) else None,
                        enrollment_date=pd.to_datetime(row['enrollment_date']) if 'enrollment_date' in row and pd.notna(row.get('enrollment_date')) else None
                    )
                    db.add(training)
                    success_count += 1
                    
                    # Commit in batches of 50
                    if success_count % 50 == 0:
                        db.commit()
                        print(f"Committed {success_count} training records...")
                        
                except Exception as e:
                    print(f"Error adding training record: {e}")
                    db.rollback()
                    continue
            
            # Final commit
            db.commit()
            print(f"[OK] Successfully loaded {success_count} training records")
            
        except FileNotFoundError:
            print("Error: training_history.csv not found in data/sample/ directory")
        except Exception as e:
            print(f"Error loading training history: {e}")
            db.rollback()
    
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("="*60)
    print(f"\nDatabase location: database.db")
    print("\nSample data loaded successfully!")
    print("\nYou can now start the backend server:")
    print("  python app.py")
    print("\n")

if __name__ == "__main__":
    try:
        load_sample_data()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
