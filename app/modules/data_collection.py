"""
Data Collection Module
Aggregates HR data, completed trainings, and job skill matrices
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.base import Employee, Skill, EmployeeSkill, Course, Training
from app.database import get_db_context
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """Handles data collection from various HR sources"""
    
    def __init__(self):
        self.logger = logger
    
    def import_employees_from_csv(self, file_path: str) -> int:
        """
        Import employee data from CSV file
        Expected columns: employee_id, name, email, department, role, 
                         job_level, years_of_experience, hire_date
        """
        try:
            df = pd.read_csv(file_path)
            
            with get_db_context() as db:
                count = 0
                for _, row in df.iterrows():
                    # Check if employee already exists
                    existing = db.query(Employee).filter(
                        Employee.employee_id == row['employee_id']
                    ).first()
                    
                    if not existing:
                        employee = Employee(
                            employee_id=row['employee_id'],
                            name=row['name'],
                            email=row['email'],
                            department=row.get('department'),
                            role=row.get('role'),
                            job_level=row.get('job_level'),
                            years_of_experience=row.get('years_of_experience'),
                            hire_date=pd.to_datetime(row.get('hire_date')) if 'hire_date' in row else None
                        )
                        db.add(employee)
                        count += 1
                
            self.logger.info(f"Imported {count} new employees")
            return count
            
        except Exception as e:
            self.logger.error(f"Error importing employees: {e}")
            raise
    
    def import_skills_from_csv(self, file_path: str) -> int:
        """
        Import skills data from CSV
        Expected columns: name, category, description, importance_score
        """
        try:
            df = pd.read_csv(file_path)
            
            with get_db_context() as db:
                count = 0
                for _, row in df.iterrows():
                    existing = db.query(Skill).filter(
                        Skill.name == row['name']
                    ).first()
                    
                    if not existing:
                        skill = Skill(
                            name=row['name'],
                            category=row.get('category', 'General'),
                            description=row.get('description'),
                            importance_score=row.get('importance_score', 1.0)
                        )
                        db.add(skill)
                        count += 1
                
            self.logger.info(f"Imported {count} new skills")
            return count
            
        except Exception as e:
            self.logger.error(f"Error importing skills: {e}")
            raise
    
    def import_employee_skills_from_csv(self, file_path: str) -> int:
        """
        Import employee skills with proficiency
        Expected columns: employee_id, skill_name, proficiency_level, 
                         last_assessed, assessment_method
        """
        try:
            df = pd.read_csv(file_path)
            
            with get_db_context() as db:
                count = 0
                for _, row in df.iterrows():
                    # Get employee
                    employee = db.query(Employee).filter(
                        Employee.employee_id == row['employee_id']
                    ).first()
                    
                    # Get skill
                    skill = db.query(Skill).filter(
                        Skill.name == row['skill_name']
                    ).first()
                    
                    if employee and skill:
                        # Check if already exists
                        existing = db.query(EmployeeSkill).filter(
                            EmployeeSkill.employee_id == employee.id,
                            EmployeeSkill.skill_id == skill.id
                        ).first()
                        
                        if existing:
                            # Update existing
                            existing.proficiency_level = row['proficiency_level']
                            existing.last_assessed = pd.to_datetime(row.get('last_assessed')) if 'last_assessed' in row else datetime.utcnow()
                            existing.assessment_method = row.get('assessment_method', 'Self-assessment')
                        else:
                            # Create new
                            emp_skill = EmployeeSkill(
                                employee_id=employee.id,
                                skill_id=skill.id,
                                proficiency_level=row['proficiency_level'],
                                last_assessed=pd.to_datetime(row.get('last_assessed')) if 'last_assessed' in row else datetime.utcnow(),
                                assessment_method=row.get('assessment_method', 'Self-assessment')
                            )
                            db.add(emp_skill)
                        count += 1
                
            self.logger.info(f"Imported/Updated {count} employee skills")
            return count
            
        except Exception as e:
            self.logger.error(f"Error importing employee skills: {e}")
            raise
    
    def import_courses_from_csv(self, file_path: str) -> int:
        """
        Import course data from CSV
        Expected columns: course_id, title, description, provider, category,
                         difficulty_level, duration_hours, cost, rating, url
        """
        try:
            df = pd.read_csv(file_path)
            
            with get_db_context() as db:
                count = 0
                for _, row in df.iterrows():
                    existing = db.query(Course).filter(
                        Course.course_id == row['course_id']
                    ).first()
                    
                    if not existing:
                        course = Course(
                            course_id=row['course_id'],
                            title=row['title'],
                            description=row.get('description'),
                            provider=row.get('provider'),
                            category=row.get('category'),
                            difficulty_level=row.get('difficulty_level'),
                            duration_hours=row.get('duration_hours'),
                            cost=row.get('cost', 0),
                            rating=row.get('rating'),
                            url=row.get('url')
                        )
                        db.add(course)
                        count += 1
                
            self.logger.info(f"Imported {count} new courses")
            return count
            
        except Exception as e:
            self.logger.error(f"Error importing courses: {e}")
            raise
    
    def import_training_history_from_csv(self, file_path: str) -> int:
        """
        Import training history from CSV
        Expected columns: employee_id, course_id, enrollment_date, 
                         completion_date, status, progress_percentage, assessment_score
        """
        try:
            df = pd.read_csv(file_path)
            
            with get_db_context() as db:
                count = 0
                for _, row in df.iterrows():
                    # Get employee and course
                    employee = db.query(Employee).filter(
                        Employee.employee_id == row['employee_id']
                    ).first()
                    
                    course = db.query(Course).filter(
                        Course.course_id == row['course_id']
                    ).first()
                    
                    if employee and course:
                        training = Training(
                            employee_id=employee.id,
                            course_id=course.id,
                            enrollment_date=pd.to_datetime(row.get('enrollment_date')),
                            completion_date=pd.to_datetime(row.get('completion_date')) if pd.notna(row.get('completion_date')) else None,
                            status=row.get('status', 'Enrolled'),
                            progress_percentage=row.get('progress_percentage', 0),
                            assessment_score=row.get('assessment_score')
                        )
                        db.add(training)
                        count += 1
                
            self.logger.info(f"Imported {count} training records")
            return count
            
        except Exception as e:
            self.logger.error(f"Error importing training history: {e}")
            raise
    
    def get_employee_data_summary(self, db: Session) -> Dict:
        """Get summary statistics of collected data"""
        return {
            'total_employees': db.query(Employee).count(),
            'total_skills': db.query(Skill).count(),
            'total_courses': db.query(Course).count(),
            'total_trainings': db.query(Training).count(),
            'avg_skills_per_employee': db.query(EmployeeSkill).count() / max(db.query(Employee).count(), 1)
        }
