"""
Script to create user accounts for all employees
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database import SessionLocal, init_db
from app.models.base import Employee, UserAccount
from app.auth import hash_password

def create_user_accounts():
    """Create user accounts for all employees"""
    db = SessionLocal()
    try:
        # Get all employees
        employees = db.query(Employee).all()
        print(f"Found {len(employees)} employees")
        
        # Create user account for each employee
        for emp in employees:
            # Check if user account already exists
            existing = db.query(UserAccount).filter(UserAccount.employee_id == emp.id).first()
            if not existing:
                # Create new user account
                user = UserAccount(
                    email=emp.email,
                    employee_id=emp.id,
                    role='employee',
                    password_hash=hash_password('password123'),  # Default password
                    is_active=True
                )
                db.add(user)
                print(f"Created user account for {emp.email}")
        
        # Commit all changes
        db.commit()
        print("Successfully created user accounts for all employees")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating user accounts for employees...")
    create_user_accounts()
    print("Done!")
