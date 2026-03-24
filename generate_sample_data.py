"""
Generate sample data for IntelliLearn AI platform
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Create data directory
data_dir = Path("data/sample")
data_dir.mkdir(parents=True, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# 1. Generate Employees
print("Generating employees...")

departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Operations', 'Finance']
roles = ['Software Engineer', 'Data Scientist', 'Product Manager', 'Sales Manager', 
         'Marketing Specialist', 'HR Manager', 'Operations Lead', 'Financial Analyst']
job_levels = ['Junior', 'Mid', 'Senior', 'Lead', 'Manager']

employees_data = []
for i in range(1, 51):  # 50 employees
    emp = {
        'employee_id': f'EMP{i:04d}',
        'name': f'Employee {i}',
        'email': f'employee{i}@company.com',
        'department': random.choice(departments),
        'role': random.choice(roles),
        'job_level': random.choice(job_levels),
        'years_of_experience': round(random.uniform(0.5, 15), 1),
        'hire_date': (datetime.now() - timedelta(days=random.randint(30, 1825))).strftime('%Y-%m-%d')
    }
    employees_data.append(emp)

employees_df = pd.DataFrame(employees_data)
employees_df.to_csv(data_dir / 'employees.csv', index=False)
print(f"[OK] Generated {len(employees_df)} employees")

# 2. Generate Skills
print("Generating skills...")

skills_data = [
    # Technical Skills
    {'name': 'Python Programming', 'category': 'Technical', 'description': 'Programming in Python', 'importance_score': 1.5},
    {'name': 'Machine Learning', 'category': 'Technical', 'description': 'ML algorithms and models', 'importance_score': 1.8},
    {'name': 'Data Analysis', 'category': 'Technical', 'description': 'Data analysis and visualization', 'importance_score': 1.6},
    {'name': 'SQL', 'category': 'Technical', 'description': 'Database querying', 'importance_score': 1.4},
    {'name': 'JavaScript', 'category': 'Technical', 'description': 'Web development', 'importance_score': 1.3},
    {'name': 'Cloud Computing', 'category': 'Technical', 'description': 'AWS, Azure, GCP', 'importance_score': 1.7},
    {'name': 'DevOps', 'category': 'Technical', 'description': 'CI/CD and deployment', 'importance_score': 1.5},
    {'name': 'Cybersecurity', 'category': 'Technical', 'description': 'Security best practices', 'importance_score': 1.6},
    {'name': 'Data Engineering', 'category': 'Technical', 'description': 'Data pipelines and ETL', 'importance_score': 1.7},
    {'name': 'AI and Deep Learning', 'category': 'Technical', 'description': 'Neural networks and AI', 'importance_score': 1.9},
    
    # Soft Skills
    {'name': 'Communication', 'category': 'Soft Skills', 'description': 'Effective communication', 'importance_score': 1.4},
    {'name': 'Leadership', 'category': 'Leadership', 'description': 'Team leadership', 'importance_score': 1.5},
    {'name': 'Project Management', 'category': 'Leadership', 'description': 'Managing projects', 'importance_score': 1.6},
    {'name': 'Critical Thinking', 'category': 'Soft Skills', 'description': 'Problem solving', 'importance_score': 1.3},
    {'name': 'Collaboration', 'category': 'Soft Skills', 'description': 'Teamwork', 'importance_score': 1.3},
    {'name': 'Time Management', 'category': 'Soft Skills', 'description': 'Managing time effectively', 'importance_score': 1.2},
    {'name': 'Adaptability', 'category': 'Soft Skills', 'description': 'Adapting to change', 'importance_score': 1.3},
    {'name': 'Negotiation', 'category': 'Soft Skills', 'description': 'Negotiation skills', 'importance_score': 1.4},
    {'name': 'Strategic Planning', 'category': 'Leadership', 'description': 'Strategic thinking', 'importance_score': 1.6},
    {'name': 'Agile Methodology', 'category': 'Technical', 'description': 'Agile practices', 'importance_score': 1.4},
]

skills_df = pd.DataFrame(skills_data)
skills_df.to_csv(data_dir / 'skills.csv', index=False)
print(f"[OK] Generated {len(skills_df)} skills")

# 3. Generate Employee Skills
print("Generating employee skills...")

employee_skills_data = []
for emp_id in employees_df['employee_id']:
    # Each employee has 5-12 skills
    num_skills = random.randint(5, 12)
    selected_skills = random.sample(skills_df['name'].tolist(), num_skills)
    
    for skill_name in selected_skills:
        emp_skill = {
            'employee_id': emp_id,
            'skill_name': skill_name,
            'proficiency_level': round(random.uniform(3, 9), 1),
            'last_assessed': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d'),
            'assessment_method': random.choice(['Self-assessment', 'Manager', 'Test', 'Peer Review'])
        }
        employee_skills_data.append(emp_skill)

employee_skills_df = pd.DataFrame(employee_skills_data)
employee_skills_df.to_csv(data_dir / 'employee_skills.csv', index=False)
print(f"[OK] Generated {len(employee_skills_df)} employee skill records")

# 4. Generate Courses
print("Generating courses...")

courses_data = [
    # Python & Data Science
    {'course_id': 'CS001', 'title': 'Python for Data Science', 'description': 'Learn Python programming for data analysis', 
     'provider': 'Coursera', 'category': 'Data Science', 'difficulty_level': 'Beginner', 'duration_hours': 40, 'cost': 49, 'rating': 4.7, 'url': 'https://coursera.org/python-ds'},
    {'course_id': 'CS002', 'title': 'Machine Learning Fundamentals', 'description': 'Introduction to ML algorithms', 
     'provider': 'Udacity', 'category': 'Machine Learning', 'difficulty_level': 'Intermediate', 'duration_hours': 60, 'cost': 199, 'rating': 4.8, 'url': 'https://udacity.com/ml-fundamentals'},
    {'course_id': 'CS003', 'title': 'Advanced Machine Learning', 'description': 'Deep dive into advanced ML techniques', 
     'provider': 'Coursera', 'category': 'Machine Learning', 'difficulty_level': 'Advanced', 'duration_hours': 80, 'cost': 299, 'rating': 4.9, 'url': 'https://coursera.org/advanced-ml'},
    {'course_id': 'CS004', 'title': 'Data Visualization with Python', 'description': 'Master data visualization techniques', 
     'provider': 'DataCamp', 'category': 'Data Science', 'difficulty_level': 'Intermediate', 'duration_hours': 30, 'cost': 79, 'rating': 4.6, 'url': 'https://datacamp.com/data-viz'},
    
    # Cloud & DevOps
    {'course_id': 'CS005', 'title': 'AWS Cloud Practitioner', 'description': 'AWS fundamentals and services', 
     'provider': 'AWS Training', 'category': 'Cloud Computing', 'difficulty_level': 'Beginner', 'duration_hours': 35, 'cost': 0, 'rating': 4.5, 'url': 'https://aws.amazon.com/training'},
    {'course_id': 'CS006', 'title': 'Docker and Kubernetes', 'description': 'Container orchestration', 
     'provider': 'Udemy', 'category': 'DevOps', 'difficulty_level': 'Intermediate', 'duration_hours': 45, 'cost': 89, 'rating': 4.7, 'url': 'https://udemy.com/docker-k8s'},
    {'course_id': 'CS007', 'title': 'CI/CD with Jenkins', 'description': 'Continuous integration and deployment', 
     'provider': 'LinkedIn Learning', 'category': 'DevOps', 'difficulty_level': 'Intermediate', 'duration_hours': 25, 'cost': 39, 'rating': 4.4, 'url': 'https://linkedin.com/jenkins'},
    
    # Web Development
    {'course_id': 'CS008', 'title': 'Full Stack Web Development', 'description': 'Complete web development course', 
     'provider': 'Udemy', 'category': 'Web Development', 'difficulty_level': 'Intermediate', 'duration_hours': 70, 'cost': 129, 'rating': 4.6, 'url': 'https://udemy.com/fullstack'},
    {'course_id': 'CS009', 'title': 'React and Redux', 'description': 'Modern frontend development', 
     'provider': 'Pluralsight', 'category': 'Web Development', 'difficulty_level': 'Intermediate', 'duration_hours': 40, 'cost': 99, 'rating': 4.5, 'url': 'https://pluralsight.com/react'},
    
    # Cybersecurity
    {'course_id': 'CS010', 'title': 'Cybersecurity Fundamentals', 'description': 'Introduction to cybersecurity', 
     'provider': 'Coursera', 'category': 'Security', 'difficulty_level': 'Beginner', 'duration_hours': 50, 'cost': 149, 'rating': 4.7, 'url': 'https://coursera.org/cybersecurity'},
    {'course_id': 'CS011', 'title': 'Ethical Hacking', 'description': 'Penetration testing and security', 
     'provider': 'Udemy', 'category': 'Security', 'difficulty_level': 'Advanced', 'duration_hours': 60, 'cost': 199, 'rating': 4.8, 'url': 'https://udemy.com/ethical-hacking'},
    
    # Leadership & Soft Skills
    {'course_id': 'CS012', 'title': 'Leadership Essentials', 'description': 'Develop leadership skills', 
     'provider': 'LinkedIn Learning', 'category': 'Leadership', 'difficulty_level': 'Beginner', 'duration_hours': 20, 'cost': 49, 'rating': 4.5, 'url': 'https://linkedin.com/leadership'},
    {'course_id': 'CS013', 'title': 'Project Management Professional', 'description': 'PMP certification prep', 
     'provider': 'PMI', 'category': 'Project Management', 'difficulty_level': 'Advanced', 'duration_hours': 100, 'cost': 399, 'rating': 4.8, 'url': 'https://pmi.org/pmp'},
    {'course_id': 'CS014', 'title': 'Effective Communication', 'description': 'Improve communication skills', 
     'provider': 'Coursera', 'category': 'Soft Skills', 'difficulty_level': 'Beginner', 'duration_hours': 15, 'cost': 29, 'rating': 4.4, 'url': 'https://coursera.org/communication'},
    {'course_id': 'CS015', 'title': 'Agile and Scrum Mastery', 'description': 'Master agile methodologies', 
     'provider': 'Scrum Alliance', 'category': 'Project Management', 'difficulty_level': 'Intermediate', 'duration_hours': 30, 'cost': 149, 'rating': 4.7, 'url': 'https://scrumalliance.org/agile'},
    
    # AI & Deep Learning
    {'course_id': 'CS016', 'title': 'Deep Learning Specialization', 'description': 'Neural networks and deep learning', 
     'provider': 'Coursera', 'category': 'AI', 'difficulty_level': 'Advanced', 'duration_hours': 120, 'cost': 399, 'rating': 4.9, 'url': 'https://coursera.org/deep-learning'},
    {'course_id': 'CS017', 'title': 'Natural Language Processing', 'description': 'NLP techniques and applications', 
     'provider': 'Udacity', 'category': 'AI', 'difficulty_level': 'Advanced', 'duration_hours': 90, 'cost': 299, 'rating': 4.8, 'url': 'https://udacity.com/nlp'},
    {'course_id': 'CS018', 'title': 'Computer Vision', 'description': 'Image processing and CV', 
     'provider': 'Coursera', 'category': 'AI', 'difficulty_level': 'Advanced', 'duration_hours': 85, 'cost': 279, 'rating': 4.7, 'url': 'https://coursera.org/computer-vision'},
    
    # Data Engineering
    {'course_id': 'CS019', 'title': 'Data Engineering Fundamentals', 'description': 'ETL and data pipelines', 
     'provider': 'DataCamp', 'category': 'Data Engineering', 'difficulty_level': 'Intermediate', 'duration_hours': 55, 'cost': 159, 'rating': 4.6, 'url': 'https://datacamp.com/data-eng'},
    {'course_id': 'CS020', 'title': 'Big Data with Spark', 'description': 'Apache Spark for big data', 
     'provider': 'Udemy', 'category': 'Data Engineering', 'difficulty_level': 'Advanced', 'duration_hours': 70, 'cost': 189, 'rating': 4.7, 'url': 'https://udemy.com/spark'},
]

courses_df = pd.DataFrame(courses_data)
courses_df.to_csv(data_dir / 'courses.csv', index=False)
print(f"[OK] Generated {len(courses_df)} courses")

# 5. Generate Training History
print("Generating training history...")

training_data = []
statuses = ['Completed', 'In Progress', 'Enrolled']

for _ in range(150):  # 150 training records
    emp_id = random.choice(employees_df['employee_id'].tolist())
    course_id = random.choice(courses_df['course_id'].tolist())
    status = random.choice(statuses)
    
    enrollment_date = datetime.now() - timedelta(days=random.randint(1, 365))
    
    if status == 'Completed':
        completion_date = enrollment_date + timedelta(days=random.randint(7, 90))
        progress = 100
        assessment_score = round(random.uniform(60, 98), 1)
    elif status == 'In Progress':
        completion_date = None
        progress = round(random.uniform(20, 80), 1)
        assessment_score = None
    else:  # Enrolled
        completion_date = None
        progress = round(random.uniform(0, 20), 1)
        assessment_score = None
    
    training = {
        'employee_id': emp_id,
        'course_id': course_id,
        'enrollment_date': enrollment_date.strftime('%Y-%m-%d'),
        'completion_date': completion_date.strftime('%Y-%m-%d') if completion_date else '',
        'status': status,
        'progress_percentage': progress,
        'assessment_score': assessment_score if assessment_score else ''
    }
    training_data.append(training)

training_df = pd.DataFrame(training_data)
training_df.to_csv(data_dir / 'training_history.csv', index=False)
print(f"[OK] Generated {len(training_df)} training records")

print("\n" + "="*60)
print("Sample data generation complete!")
print("="*60)
print(f"\nFiles created in {data_dir}:")
print(f"  - employees.csv ({len(employees_df)} records)")
print(f"  - skills.csv ({len(skills_df)} records)")
print(f"  - employee_skills.csv ({len(employee_skills_df)} records)")
print(f"  - courses.csv ({len(courses_df)} records)")
print(f"  - training_history.csv ({len(training_df)} records)")
print("\nYou can now import this data through the Admin Panel in the Streamlit app.")
