"""
Database models for IntelliLearn AI Platform
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, JSON, Table
)
from sqlalchemy.orm import relationship
from app.database import Base


# Association table for many-to-many relationship between skills and courses
course_skills = Table(
    'course_skills',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)


class Employee(Base):
    """Employee model"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    department = Column(String(100))
    role = Column(String(100))
    job_level = Column(String(50))
    years_of_experience = Column(Float)
    hire_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    trainings = relationship("Training", back_populates="employee", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGapPrediction", back_populates="employee", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="employee", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="employee", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="employee", cascade="all, delete-orphan")


class Skill(Base):
    """Skills model"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    category = Column(String(100))  # e.g., Technical, Soft Skills, Leadership
    description = Column(Text)
    importance_score = Column(Float, default=1.0)  # Relative importance
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")
    courses = relationship("Course", secondary=course_skills, back_populates="skills")


class EmployeeSkill(Base):
    """Employee skills with proficiency levels"""
    __tablename__ = "employee_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(Float)  # 0-10 scale
    last_assessed = Column(DateTime)
    assessment_method = Column(String(100))  # Self-assessment, Manager, Test
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")


class Course(Base):
    """Training courses and learning materials"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    provider = Column(String(200))
    category = Column(String(100))
    difficulty_level = Column(String(50))  # Beginner, Intermediate, Advanced
    duration_hours = Column(Float)
    cost = Column(Float)
    rating = Column(Float)
    url = Column(String(500))
    content_embedding = Column(JSON)  # Store embeddings for similarity search
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("Skill", secondary=course_skills, back_populates="courses")
    trainings = relationship("Training", back_populates="course")


class Training(Base):
    """Employee training history"""
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrollment_date = Column(DateTime)
    completion_date = Column(DateTime)
    status = Column(String(50))  # Enrolled, In Progress, Completed, Dropped
    progress_percentage = Column(Float, default=0.0)
    assessment_score = Column(Float)
    feedback_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="trainings")
    course = relationship("Course", back_populates="trainings")


class SkillGapPrediction(Base):
    """Predicted skill gaps for employees"""
    __tablename__ = "skill_gap_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_name = Column(String(200), nullable=False)
    current_level = Column(Float)
    required_level = Column(Float)
    gap_score = Column(Float)  # Difference between required and current
    priority = Column(String(50))  # High, Medium, Low
    confidence_score = Column(Float)  # Model confidence
    predicted_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="skill_gaps")


class Recommendation(Base):
    """Course recommendations for employees"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    recommendation_score = Column(Float)
    reasoning = Column(Text)  # LLM-generated explanation
    recommendation_type = Column(String(50))  # Skill Gap, Career Growth, Interest-based
    is_accepted = Column(Boolean, default=False)
    recommended_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee", back_populates="recommendations")
    course = relationship("Course", foreign_keys=[course_id])


class Feedback(Base):
    """User feedback for adaptive learning"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    feedback_type = Column(String(50))  # Course, Recommendation, Chatbot
    rating = Column(Float)
    comment = Column(Text)
    context = Column(JSON)  # Additional context data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="feedbacks")


class PerformanceMetric(Base):
    """Performance metrics for ROI calculation"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    metric_name = Column(String(200), nullable=False)
    metric_value = Column(Float)
    metric_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="performance_metrics")


class AdminUser(Base):
    """Administrative user for dashboard access"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserAccount(Base):
    """End-user account mapped to an Employee, role = 'employee'"""
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='employee')
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TokenTransaction(Base):
    """Reward tokens granted to employees for achievements (e.g., course completion)"""
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=True)
    amount = Column(Integer, nullable=False, default=0)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
