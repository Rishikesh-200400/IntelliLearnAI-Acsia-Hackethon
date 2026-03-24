"""
IntelliLearn AI - Flask REST API Backend
AI-Driven Employee Skill Development Platform
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import sys
from datetime import datetime, timedelta
import zipfile
import tempfile
import os

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db_context
from app.modules.data_collection import DataCollector
from app.modules.skill_gap_predictor import SkillGapPredictor
from app.modules.llm_assistant import LLMAssistant
from app.modules.recommender import HybridRecommender
from app.modules.analytics import AnalyticsEngine
from app.models.base import Employee, Course, EmployeeSkill, SkillGapPrediction, Training, AdminUser, UserAccount, TokenTransaction
from sqlalchemy import func
from app.config import config
from app.auth import create_token, verify_token, extract_bearer_token, hash_password, verify_password

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize database
init_db()

# Create default admin if none exists
def _ensure_default_admin():
    try:
        with get_db_context() as db:
            exists = db.query(AdminUser).first()
            if not exists:
                admin = AdminUser(
                    email='admin@example.com',
                    password_hash=hash_password('admin123'),
                    full_name='Administrator',
                    is_active=True,
                )
                db.add(admin)
                db.commit()
    except Exception:
        pass

_ensure_default_admin()

# ============================================
# Auth Endpoints
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        if not email or not password:
            return jsonify({'error': 'email and password are required'}), 400
        with get_db_context() as db:
            # Try admin
            admin = db.query(AdminUser).filter(AdminUser.email == email, AdminUser.is_active == True).first()
            if admin and verify_password(admin.password_hash, password):
                token = create_token(admin.id, admin.email, 'admin')
                return jsonify({'token': token, 'role': 'admin', 'user': {'id': admin.id, 'email': admin.email, 'full_name': admin.full_name}})

            # Try employee user account
            ua = db.query(UserAccount).filter(UserAccount.email == email, UserAccount.is_active == True).first()
            if ua and verify_password(ua.password_hash, password):
                token = create_token(ua.id, ua.email, ua.role or 'employee')
                return jsonify({'token': token, 'role': ua.role or 'employee', 'employee_id': ua.employee_id, 'user': {'id': ua.id, 'email': ua.email}})

            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    try:
        token = extract_bearer_token()
        payload = verify_token(token) if token else None
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        with get_db_context() as db:
            # Use role embedded in token to avoid id collisions across tables
            role = (payload.get('role') or '').lower()
            if role == 'admin':
                user = db.query(AdminUser).filter(AdminUser.id == payload['uid']).first()
                if user:
                    return jsonify({'id': user.id, 'email': user.email, 'full_name': user.full_name, 'role': 'admin'})
            else:
                ua = db.query(UserAccount).filter(UserAccount.id == payload['uid']).first()
                if ua:
                    return jsonify({'id': ua.id, 'email': ua.email, 'role': ua.role or 'employee', 'employee_id': ua.employee_id})
            return jsonify({'error': 'Unauthorized'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register-employee', methods=['POST'])
def register_employee():
    """Create or update a user account for an employee email with password"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        if not email or not password:
            return jsonify({'error': 'email and password are required'}), 400
        with get_db_context() as db:
            emp = db.query(Employee).filter(Employee.email == email).first()
            if not emp:
                return jsonify({'error': 'Employee not found for email'}), 404
            ua = db.query(UserAccount).filter(UserAccount.email == email).first()
            if not ua:
                ua = UserAccount(email=email, employee_id=emp.id, role='employee', password_hash=hash_password(password))
                db.add(ua)
            else:
                ua.password_hash = hash_password(password)
                ua.employee_id = emp.id
                ua.role = 'employee'
            db.commit()
            return jsonify({'status': 'success', 'employee_id': emp.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Employee Endpoints
# ============================================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        with get_db_context() as db:
            employees = db.query(Employee).all()
            return jsonify([{
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': emp.name,
                'email': emp.email,
                'role': emp.role,
                'department': emp.department,
                'years_of_experience': emp.years_of_experience,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None
            } for emp in employees])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get employee by ID"""
    try:
        with get_db_context() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return jsonify({'error': 'Employee not found'}), 404
            
            return jsonify({
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.name,
                'email': employee.email,
                'role': employee.role,
                'department': employee.department,
                'years_of_experience': employee.years_of_experience,
                'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/skills', methods=['GET'])
def get_employee_skills(employee_id):
    """Get employee skills"""
    try:
        with get_db_context() as db:
            skills = db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == employee_id
            ).all()
            
            return jsonify([{
                'skill_name': s.skill.name,
                'skill_category': s.skill.category,
                'proficiency_level': s.proficiency_level,
                'last_assessed': s.last_assessed.isoformat() if s.last_assessed else None
            } for s in skills])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/skill-gaps', methods=['GET'])
def get_employee_skill_gaps(employee_id):
    """Get employee skill gaps"""
    try:
        with get_db_context() as db:
            gaps = db.query(SkillGapPrediction).filter(
                SkillGapPrediction.employee_id == employee_id,
                SkillGapPrediction.is_active == True
            ).order_by(SkillGapPrediction.gap_score.desc()).all()
            
            return jsonify([{
                'skill_name': g.skill_name,
                'current_level': g.current_level,
                'required_level': g.required_level,
                'gap_score': g.gap_score,
                'priority': g.priority,
                'confidence_score': g.confidence_score,
                'predicted_at': g.predicted_at.isoformat() if g.predicted_at else None
            } for g in gaps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/skill-gaps/predict', methods=['POST'])
def predict_skill_gaps(employee_id):
    """Predict skill gaps for an employee"""
    try:
        with get_db_context() as db:
            predictor = SkillGapPredictor()
            predictor.load_models()
            predicted_gaps = predictor.predict_skill_gaps(db, employee_id)
            
            if predicted_gaps:
                predictor.save_predictions_to_db(db, employee_id, predicted_gaps)
                return jsonify({
                    'status': 'success',
                    'gaps_found': len(predicted_gaps),
                    'message': f'Identified {len(predicted_gaps)} skill gaps'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'gaps_found': 0,
                    'message': 'No significant skill gaps identified'
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/trainings', methods=['GET'])
def get_employee_trainings(employee_id):
    """Get employee training history"""
    try:
        with get_db_context() as db:
            trainings = db.query(Training).filter(
                Training.employee_id == employee_id
            ).order_by(Training.enrollment_date.desc()).all()
            
            return jsonify([{
                'id': t.id,
                'course_id': t.course_id,
                'course_title': t.course.title if t.course else 'N/A',
                'course_provider': t.course.provider if t.course else 'N/A',
                'course_url': t.course.url if t.course else None,
                'status': t.status,
                'enrollment_date': t.enrollment_date.isoformat() if t.enrollment_date else None,
                'completion_date': t.completion_date.isoformat() if t.completion_date else None,
                'progress_percentage': t.progress_percentage,
                'assessment_score': t.assessment_score
            } for t in trainings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/courses', methods=['GET'])
def get_employee_courses(employee_id):
    """Get employee's enrolled courses (alias for trainings)"""
    try:
        with get_db_context() as db:
            trainings = db.query(Training).filter(
                Training.employee_id == employee_id
            ).order_by(Training.enrollment_date.desc()).all()
            
            return jsonify([{
                'id': t.id,
                'training_id': t.id,
                'course_id': t.course_id,
                'title': t.course.title if t.course else 'N/A',
                'provider': t.course.provider if t.course else 'N/A',
                'category': t.course.category if t.course else 'N/A',
                'difficulty_level': t.course.difficulty_level if t.course else 'N/A',
                'duration': t.course.duration_hours if t.course else 0,
                'url': t.course.url if t.course else None,
                'status': t.status,
                'enrollment_date': t.enrollment_date.isoformat() if t.enrollment_date else None,
                'completion_date': t.completion_date.isoformat() if t.completion_date else None,
                'progress_percentage': t.progress_percentage,
                'assessment_score': t.assessment_score,
                'description': t.course.description if t.course else ''
            } for t in trainings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Course Endpoints
# ============================================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        with get_db_context() as db:
            courses = db.query(Course).all()
            return jsonify([{
                'id': c.id,
                'title': c.title,
                'provider': c.provider,
                'category': c.category,
                'difficulty_level': c.difficulty_level,
                'duration_hours': c.duration_hours,
                'rating': c.rating,
                'url': c.url
            } for c in courses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Recommendations Endpoints
# ============================================

@app.route('/api/recommendations/<int:employee_id>', methods=['GET'])
def get_recommendations(employee_id):
    """Get course recommendations for an employee"""
    try:
        # Return hardcoded test data
        recommendations = [
            {
                'id': 1,
                'course_id': 1,
                'title': 'Test Course',
                'course_title': 'Test Course',
                'provider': 'Test Provider',
                'category': 'Programming',
                'difficulty_level': 'Intermediate',
                'duration_hours': 10,
                'rating': 4.5,
                'match_score': 0.8,
                'recommendation_score': 0.8,
                'url': 'http://example.com',
                'description': 'Test description',
                'priority': 'High'
            }
        ]
        
        return jsonify({
            'employee_id': employee_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        # Simplified error handling to avoid Windows console issues
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/api/learning-path/<int:employee_id>', methods=['GET'])
def get_learning_path(employee_id):
    """Get structured learning path for an employee"""
    try:
        with get_db_context() as db:
            recommender = HybridRecommender(db)
            learning_path = recommender.get_learning_path(employee_id)
            
            return jsonify({
                'employee_id': employee_id,
                'learning_path': learning_path
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# AI Assistant Endpoints
# ============================================

@app.route('/api/ai-assistant/chat', methods=['POST'])
def ai_chat():
    """Chat with AI assistant"""
    try:
        data = request.json
        employee_id = data.get('employee_id')
        query = data.get('query')
        
        if not employee_id or not query:
            return jsonify({'error': 'employee_id and query are required'}), 400
        
        with get_db_context() as db:
            assistant = LLMAssistant(db)
            response = assistant.chat(employee_id, query)
            
            return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-assistant/guidance/<int:employee_id>', methods=['GET'])
def get_personalized_guidance(employee_id):
    """Get personalized learning guidance"""
    try:
        with get_db_context() as db:
            assistant = LLMAssistant(db)
            guidance = assistant.get_personalized_guidance(employee_id)
            
            return jsonify(guidance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Analytics Endpoints
# ============================================

@app.route('/api/analytics/workforce-readiness', methods=['GET'])
def get_workforce_readiness():
    """Get workforce readiness metrics"""
    try:
        with get_db_context() as db:
            analytics = AnalyticsEngine(db)
            readiness = analytics.calculate_workforce_readiness()
            return jsonify(readiness)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/training-roi', methods=['GET'])
def get_training_roi():
    """Get training ROI metrics"""
    try:
        time_period = request.args.get('time_period_days', 90, type=int)
        
        with get_db_context() as db:
            analytics = AnalyticsEngine(db)
            roi = analytics.calculate_training_roi(time_period_days=time_period)
            return jsonify(roi)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/department-comparison', methods=['GET'])
def get_department_comparison():
    """Get department comparison"""
    try:
        with get_db_context() as db:
            analytics = AnalyticsEngine(db)
            comparison = analytics.get_department_comparison()
            return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/skill-gap-trends', methods=['GET'])
def get_skill_gap_trends():
    """Get skill gap trends"""
    try:
        time_periods = request.args.get('time_periods', 6, type=int)
        
        with get_db_context() as db:
            analytics = AnalyticsEngine(db)
            trends = analytics.get_skill_gap_trends(time_periods=time_periods)
            return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Admin Endpoints
# ============================================

@app.route('/api/admin/data-summary', methods=['GET'])
def get_data_summary():
    """Get data summary"""
    try:
        with get_db_context() as db:
            collector = DataCollector()
            summary = collector.get_employee_data_summary(db)
            return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/import-sample-data', methods=['POST'])
def import_sample_data():
    """Import sample data"""
    try:
        collector = DataCollector()
        sample_dir = Path("data/sample")

        # Preferred legacy sample CSV set
        legacy_files = {
            'employees': sample_dir / "employees.csv",
            'skills': sample_dir / "skills.csv",
            'employee_skills': sample_dir / "employee_skills.csv",
            'courses': sample_dir / "courses.csv",
            'training_history': sample_dir / "training_history.csv",
        }

        def legacy_available() -> bool:
            return all(p.exists() for p in legacy_files.values())

        if legacy_available():
            results = {
                'employees': collector.import_employees_from_csv(str(legacy_files['employees'])),
                'skills': collector.import_skills_from_csv(str(legacy_files['skills'])),
                'employee_skills': collector.import_employee_skills_from_csv(str(legacy_files['employee_skills'])),
                'courses': collector.import_courses_from_csv(str(legacy_files['courses'])),
                'training_history': collector.import_training_history_from_csv(str(legacy_files['training_history'])),
            }
        else:
            # Fallback to updated dataset files with custom mappings
            emp_csv = sample_dir / "Employee_Profile_Data_Updated.csv"
            course_csv = sample_dir / "Course_Catalog_Updated.csv"
            learn_hist_csv = sample_dir / "Employee_Learning_History_Updated.csv"

            if not (emp_csv.exists() and course_csv.exists() and learn_hist_csv.exists()):
                return jsonify({'error': 'Sample files not found. Provide legacy CSVs or the updated dataset CSVs in data/sample.'}), 400

            import pandas as pd

            # Employees mapping
            emp_df = pd.read_csv(str(emp_csv))
            mapped_emp = pd.DataFrame({
                'employee_id': emp_df.get('employee_id', emp_df.get('Employee_ID')),
                'name': emp_df.get('name', emp_df.get('employee_name', emp_df.get('full_name'))),
                'email': emp_df.get('email', emp_df.get('Email')),
                'department': emp_df.get('department', emp_df.get('dept', emp_df.get('Department'))),
                'role': emp_df.get('role', emp_df.get('job_role', emp_df.get('Role'))),
                'job_level': emp_df.get('job_level', emp_df.get('level', emp_df.get('Job_Level'))),
                'years_of_experience': emp_df.get('years_of_experience', emp_df.get('experience_years', emp_df.get('Years_of_Experience'))),
                'hire_date': emp_df.get('hire_date', emp_df.get('Hire_Date'))
            })
            tmp_emp = sample_dir / "_mapped_employees.csv"
            mapped_emp.to_csv(tmp_emp, index=False)

            # Courses mapping
            course_df = pd.read_csv(str(course_csv))
            mapped_courses = pd.DataFrame({
                'course_id': course_df.get('course_id', course_df.get('Course_ID')),
                'title': course_df.get('title', course_df.get('Course_Title')),
                'description': course_df.get('description', course_df.get('Description')),
                'provider': course_df.get('provider', course_df.get('Provider')),
                'category': course_df.get('category', course_df.get('Category')),
                'difficulty_level': course_df.get('difficulty_level', course_df.get('Difficulty')),
                'duration_hours': course_df.get('duration_hours', course_df.get('Duration_Hours')),
                'cost': course_df.get('cost', course_df.get('Cost')),
                'rating': course_df.get('rating', course_df.get('Rating')),
                'url': course_df.get('url', course_df.get('URL')),
            })
            tmp_courses = sample_dir / "_mapped_courses.csv"
            mapped_courses.to_csv(tmp_courses, index=False)

            # Training history mapping (score_percent -> assessment_score)
            th_df = pd.read_csv(str(learn_hist_csv))
            mapped_th = pd.DataFrame({
                'employee_id': th_df.get('employee_id'),
                'course_id': th_df.get('course_id'),
                'enrollment_date': th_df.get('enrollment_date'),
                'completion_date': th_df.get('completion_date'),
                'status': th_df.get('status'),
                'progress_percentage': th_df.get('progress_percentage', 100.0),
                'assessment_score': th_df.get('score_percent'),
            })
            tmp_th = sample_dir / "_mapped_training_history.csv"
            mapped_th.to_csv(tmp_th, index=False)

            results = {
                'employees': collector.import_employees_from_csv(str(tmp_emp)),
                'skills': 0,
                'employee_skills': 0,
                'courses': collector.import_courses_from_csv(str(tmp_courses)),
                'training_history': collector.import_training_history_from_csv(str(tmp_th)),
            }
        # Normalize departments/roles to Computer Engineering themes
        try:
            engineering_roles = [
                'Software Engineer', 'Backend Engineer', 'Frontend Engineer', 'Full-Stack Engineer',
                'Data Engineer', 'Machine Learning Engineer', 'DevOps Engineer', 'Cloud Engineer',
                'Security Engineer', 'QA Engineer'
            ]
            with get_db_context() as db:
                emps = db.query(Employee).all()
                for idx, emp in enumerate(emps):
                    emp.department = 'Computer Engineering'
                    emp.role = engineering_roles[idx % len(engineering_roles)]
                db.commit()
        except Exception:
            # Do not fail the import if normalization fails
            pass

        total = sum(results.values())
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully imported {total} total records',
            'details': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/train-models', methods=['POST'])
def train_models():
    """Train ML models"""
    try:
        with get_db_context() as db:
            predictor = SkillGapPredictor()
            results = predictor.train_models(db)
            return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/tokens/summary', methods=['GET'])
def tokens_summary():
    """Get total tokens per employee"""
    try:
        with get_db_context() as db:
            # Sum tokens per employee
            rows = db.query(
                Employee.id.label('employee_id'),
                Employee.name.label('name'),
                Employee.email.label('email'),
                func.coalesce(func.sum(TokenTransaction.amount), 0).label('tokens')
            ).outerjoin(TokenTransaction, TokenTransaction.employee_id == Employee.id)
            rows = rows.group_by(Employee.id).all()
            return jsonify([
                {
                    'employee_id': r.employee_id,
                    'name': r.name,
                    'email': r.email,
                    'tokens': int(r.tokens or 0)
                } for r in rows
            ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/tokens/award-completions', methods=['POST'])
def award_tokens_for_completed_trainings():
    """Award tokens for completed trainings that haven't been rewarded yet.
    Default: 10 tokens per completed training record without a token transaction."""
    try:
        tokens_per_completion = request.json.get('tokens_per_completion', 10) if request.is_json else 10
        awarded = 0
        with get_db_context() as db:
            # Find completed trainings
            completed = db.query(Training).filter(Training.status == 'Completed').all()
            for tr in completed:
                # Skip if token already given for this training
                exists = db.query(TokenTransaction).filter(TokenTransaction.training_id == tr.id).first()
                if exists:
                    continue
                # Create token record
                tx = TokenTransaction(
                    employee_id=tr.employee_id,
                    training_id=tr.id,
                    amount=tokens_per_completion,
                    reason='Course completion reward'
                )
                db.add(tx)
                awarded += 1
            db.commit()
        return jsonify({'status': 'success', 'awarded_count': awarded, 'tokens_per_completion': tokens_per_completion})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/assign-role-courses', methods=['POST'])
def assign_role_matched_courses():
    """Assign courses to each employee that match their job role keywords.
    Creates Training rows with status 'Enrolled' if not already present.
    Query params/body: top_n per employee (default 3)."""
    try:
        top_n = 3
        if request.is_json:
            top_n = int(request.json.get('top_n', 3) or 3)
        assigned = 0
        with get_db_context() as db:
            employees = db.query(Employee).all()
            all_courses = db.query(Course).all()

            for emp in employees:
                role_text = (emp.role or '').lower()
                if not role_text:
                    continue
                # Simple keyword mapping based on role
                keywords = []
                if 'backend' in role_text:
                    keywords += ['backend', 'api', 'server', 'database', 'python', 'node']
                if 'frontend' in role_text:
                    keywords += ['frontend', 'react', 'typescript', 'css', 'ui']
                if 'full' in role_text:
                    keywords += ['full-stack', 'react', 'node', 'api']
                if 'devops' in role_text or 'cloud' in role_text:
                    keywords += ['devops', 'aws', 'azure', 'kubernetes', 'docker', 'terraform', 'cloud']
                if 'security' in role_text:
                    keywords += ['security', 'owasp', 'cyber', 'auth']
                if 'qa' in role_text or 'test' in role_text:
                    keywords += ['testing', 'qa', 'automation', 'selenium', 'cypress']
                if 'ml' in role_text or 'machine learning' in role_text or 'data' in role_text:
                    keywords += ['machine learning', 'ml', 'data', 'pandas', 'scikit', 'deep learning']
                if not keywords:
                    keywords = role_text.split()

                # Score courses by keyword occurrences in title/description/category
                def course_score(c: Course) -> int:
                    text = f"{c.title} {c.description or ''} {c.category or ''} {c.provider or ''}".lower()
                    return sum(1 for kw in keywords if kw in text)

                ranked = sorted(all_courses, key=course_score, reverse=True)
                picked = [c for c in ranked if course_score(c) > 0][:top_n]
                if not picked:
                    picked = ranked[:top_n]

                for c in picked:
                    # Skip if already has a training for this course
                    exists = db.query(Training).filter(Training.employee_id == emp.id, Training.course_id == c.id).first()
                    if exists:
                        continue
                    tr = Training(
                        employee_id=emp.id,
                        course_id=c.id,
                        status='Enrolled',
                        enrollment_date=datetime.utcnow(),
                        progress_percentage=0.0
                    )
                    db.add(tr)
                    assigned += 1
            db.commit()
        return jsonify({'status': 'success', 'assigned_count': assigned, 'per_employee': top_n})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Admin Maintenance Endpoints
# ============================================

@app.route('/api/admin/reset-training-tokens', methods=['POST'])
def reset_training_and_tokens():
    """Delete all training history and token transactions for all employees."""
    try:
        with get_db_context() as db:
            # Delete token transactions first (foreign keys may reference trainings)
            tokens_deleted = db.query(TokenTransaction).delete()
            trainings_deleted = db.query(Training).delete()
            db.commit()
        return jsonify({
            'status': 'success',
            'tokens_deleted': int(tokens_deleted or 0),
            'trainings_deleted': int(trainings_deleted or 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/courses/add-missing-urls', methods=['POST'])
def add_missing_course_urls():
    """Backfill Course.url for courses missing a URL by generating a search link.

    For each course where url is null/empty, set to a Google search URL using the
    course title and provider so users can click through from the UI.
    """
    try:
        from urllib.parse import quote
        updated = 0
        with get_db_context() as db:
            courses = db.query(Course).all()
            for c in courses:
                if not c.url or str(c.url).strip() == '':
                    query = f"{c.title} {c.provider or 'course'}"
                    c.url = f"https://www.google.com/search?q={quote(query)}"
                    updated += 1
            db.commit()
        return jsonify({'status': 'success', 'updated': int(updated)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Skill Gap Analysis & ROI Endpoints
# ============================================

@app.route('/api/analytics/skill-gap-overview', methods=['GET'])
def get_skill_gap_overview():
    """Get organization-wide skill gap overview for admin dashboard"""
    try:
        with get_db_context() as db:
            # Get all active skill gaps
            gaps = db.query(SkillGapPrediction).filter(
                SkillGapPrediction.is_active == True
            ).all()
            
            # Count by priority
            high_priority = len([g for g in gaps if g.priority == 'High'])
            medium_priority = len([g for g in gaps if g.priority == 'Medium'])
            low_priority = len([g for g in gaps if g.priority == 'Low'])
            
            # Top skill gaps across organization
            skill_gap_counts = {}
            for g in gaps:
                skill_gap_counts[g.skill_name] = skill_gap_counts.get(g.skill_name, 0) + 1
            
            top_gaps = sorted(skill_gap_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Employees with gaps
            employees_with_gaps = len(set(g.employee_id for g in gaps))
            total_employees = db.query(Employee).count()
            
            return jsonify({
                'total_gaps': len(gaps),
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'employees_with_gaps': employees_with_gaps,
                'total_employees': total_employees,
                'coverage_percentage': round((employees_with_gaps / max(total_employees, 1)) * 100, 1),
                'top_skill_gaps': [{'skill': name, 'count': count} for name, count in top_gaps],
                'priority_distribution': [
                    {'priority': 'High', 'count': high_priority},
                    {'priority': 'Medium', 'count': medium_priority},
                    {'priority': 'Low', 'count': low_priority}
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/roi-metrics', methods=['GET'])
def get_roi_metrics():
    """Calculate ROI metrics for training investments"""
    try:
        with get_db_context() as db:
            # Get all completed trainings
            completed = db.query(Training).filter(Training.status == 'Completed').all()
            
            # Calculate costs
            total_cost = sum(t.course.cost or 0 for t in completed if t.course)
            total_hours = sum(t.course.duration_hours or 0 for t in completed if t.course)
            
            # Calculate benefits (tokens as proxy for value)
            token_txns = db.query(TokenTransaction).all()
            total_tokens = sum(tx.amount for tx in token_txns)
            
            # Assuming $10 per token value and $50/hour average employee cost
            estimated_value = total_tokens * 10
            time_investment_cost = total_hours * 50
            total_investment = total_cost + time_investment_cost
            
            roi_percentage = ((estimated_value - total_investment) / max(total_investment, 1)) * 100 if total_investment > 0 else 0
            
            # Course completion rate
            total_trainings = db.query(Training).count()
            completion_rate = (len(completed) / max(total_trainings, 1)) * 100
            
            # Average assessment score
            scores = [t.assessment_score for t in completed if t.assessment_score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            return jsonify({
                'total_investment': round(total_investment, 2),
                'estimated_value': round(estimated_value, 2),
                'roi_percentage': round(roi_percentage, 1),
                'completed_trainings': len(completed),
                'total_trainings': total_trainings,
                'completion_rate': round(completion_rate, 1),
                'average_score': round(avg_score, 1),
                'total_tokens_awarded': total_tokens,
                'training_hours': round(total_hours, 1),
                'cost_breakdown': {
                    'direct_course_costs': round(total_cost, 2),
                    'time_investment': round(time_investment_cost, 2)
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/skill-gaps/auto-recommend', methods=['POST'])
def auto_recommend_for_gaps():
    """Automatically generate course recommendations for employees with skill gaps"""
    try:
        data = request.json or {}
        employee_id = data.get('employee_id')
        
        with get_db_context() as db:
            # If no employee specified, do it for all employees with gaps
            if employee_id:
                employees = [db.query(Employee).get(employee_id)]
            else:
                gap_employee_ids = set(
                    g.employee_id for g in db.query(SkillGapPrediction).filter(
                        SkillGapPrediction.is_active == True
                    ).all()
                )
                employees = [db.query(Employee).get(eid) for eid in gap_employee_ids]
            
            recommendations_created = 0
            recommender = HybridRecommender(db)
            
            for emp in employees:
                if not emp:
                    continue
                
                # Get skill gaps
                gaps = db.query(SkillGapPrediction).filter(
                    SkillGapPrediction.employee_id == emp.id,
                    SkillGapPrediction.is_active == True
                ).order_by(SkillGapPrediction.gap_score.desc()).limit(3).all()
                
                if not gaps:
                    continue
                
                # Get recommendations
                recs = recommender.get_recommendations(emp.id, top_n=5)
                
                # Save top 3 recommendations as Recommendation records
                for rec in recs[:3]:
                    existing = db.query(Recommendation).filter(
                        Recommendation.employee_id == emp.id,
                        Recommendation.course_id == rec['id']
                    ).first()
                    
                    if not existing:
                        new_rec = Recommendation(
                            employee_id=emp.id,
                            course_id=rec['id'],
                            recommendation_score=rec.get('match_score', 0),
                            reasoning=f"Recommended to address skill gaps: {', '.join(g.skill_name for g in gaps[:2])}",
                            recommendation_type='Skill Gap'
                        )
                        db.add(new_rec)
                        recommendations_created += 1
            
            db.commit()
            
            return jsonify({
                'status': 'success',
                'recommendations_created': recommendations_created,
                'employees_processed': len([e for e in employees if e])
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees/<int:employee_id>/learning-path', methods=['GET'])
def get_employee_learning_path(employee_id):
    """Get personalized learning path for employee based on skill gaps"""
    try:
        with get_db_context() as db:
            employee = db.query(Employee).get(employee_id)
            if not employee:
                return jsonify({'error': 'Employee not found'}), 404
            
            # Get skill gaps
            gaps = db.query(SkillGapPrediction).filter(
                SkillGapPrediction.employee_id == employee_id,
                SkillGapPrediction.is_active == True
            ).order_by(SkillGapPrediction.gap_score.desc()).all()
            
            # Get recommendations
            recommender = HybridRecommender(db)
            courses = recommender.get_recommendations(employee_id, top_n=10)
            
            # Current trainings
            current_trainings = db.query(Training).filter(
                Training.employee_id == employee_id,
                Training.status.in_(['Enrolled', 'In Progress'])
            ).all()
            
            return jsonify({
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'role': employee.role,
                    'department': employee.department
                },
                'skill_gaps': [{
                    'skill_name': g.skill_name,
                    'current_level': g.current_level,
                    'required_level': g.required_level,
                    'gap_score': g.gap_score,
                    'priority': g.priority
                } for g in gaps],
                'recommended_courses': courses,
                'current_trainings': [{
                    'course_title': t.course.title if t.course else 'N/A',
                    'status': t.status,
                    'progress': t.progress_percentage
                } for t in current_trainings]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/import-external-data', methods=['POST'])
def import_external_data():
    """Import data from an external directory or a .zip file containing CSVs.

    Expects JSON body: { "path": "C:/path/to/folder-or-zip" }
    The folder/zip should include: employees.csv, skills.csv, employee_skills.csv, courses.csv, training_history.csv
    """
    try:
        body = request.json or {}
        raw_path = (body.get('path') or '').strip()
        if not raw_path:
            return jsonify({'error': 'path is required'}), 400

        p = Path(raw_path)
        if not p.exists():
            return jsonify({'error': f'Path does not exist: {raw_path}'}), 400

        # Resolve to a directory with CSVs. If a zip file, extract to temp.
        cleanup_dir = None
        try:
            if p.is_file() and p.suffix.lower() == '.zip':
                tmpdir = Path(tempfile.mkdtemp(prefix='import_external_'))
                with zipfile.ZipFile(str(p), 'r') as zf:
                    zf.extractall(str(tmpdir))
                target_dir = tmpdir
                cleanup_dir = tmpdir
            else:
                target_dir = p if p.is_dir() else p.parent

            # Try to find CSVs (allow nested single-level dir from zip)
            def find_csv(name: str) -> Path:
                # Direct
                candidate = target_dir / name
                if candidate.exists():
                    return candidate
                # Search first-level subdirs
                for child in target_dir.iterdir():
                    if child.is_dir():
                        cand = child / name
                        if cand.exists():
                            return cand
                return Path('')

            required = ['employees.csv','skills.csv','employee_skills.csv','courses.csv','training_history.csv']
            found = {name: find_csv(name) for name in required}
            missing = [k for k,v in found.items() if not v or not v.exists()]
            if missing:
                return jsonify({'error': f'Missing required files: {", ".join(missing)}'}), 400

            collector = DataCollector()
            results = {
                'employees': collector.import_employees_from_csv(str(found['employees.csv'])),
                'skills': collector.import_skills_from_csv(str(found['skills.csv'])),
                'employee_skills': collector.import_employee_skills_from_csv(str(found['employee_skills.csv'])),
                'courses': collector.import_courses_from_csv(str(found['courses.csv'])),
                'training_history': collector.import_training_history_from_csv(str(found['training_history.csv']))
            }

            total = sum(results.values())
            return jsonify({'status': 'success', 'message': f'Imported {total} records', 'details': results})
        finally:
            try:
                if cleanup_dir and cleanup_dir.exists():
                    # Best-effort cleanup
                    for root, dirs, files in os.walk(cleanup_dir, topdown=False):
                        for f in files:
                            try:
                                os.remove(Path(root) / f)
                            except Exception:
                                pass
                        for d in dirs:
                            try:
                                os.rmdir(Path(root) / d)
                            except Exception:
                                pass
                    try:
                        os.rmdir(cleanup_dir)
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/reset-progress', methods=['POST'])
def reset_tokens_and_progress():
    """Set all employees' tokens to 0 and reset all training progress to 0%.
    This keeps the training records but marks them as Enrolled with 0 progress.
    """
    try:
        with get_db_context() as db:
            # Remove all token transactions so totals become 0
            tokens_deleted = db.query(TokenTransaction).delete()
            # Reset all training records to baseline state
            updated = db.query(Training).update({
                Training.status: 'Enrolled',
                Training.progress_percentage: 0.0,
                Training.assessment_score: None,
                Training.completion_date: None,
            }, synchronize_session=False)
            db.commit()
        return jsonify({
            'status': 'success',
            'tokens_deleted': int(tokens_deleted or 0),
            'trainings_reset': int(updated or 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/wipe-domain-data', methods=['POST'])
def wipe_domain_data():
    """Delete all business/domain data (employees, skills, courses, trainings, predictions, etc.)
    This keeps admin users intact. Useful to remove previously imported datasets.
    """
    try:
        from app.models.base import (
            Employee, Skill, EmployeeSkill, Course, Training, SkillGapPrediction,
            Recommendation, Feedback, PerformanceMetric, UserAccount, TokenTransaction
        )
        removed = {}
        with get_db_context() as db:
            # Delete in dependency-safe order
            removed['token_transactions'] = db.query(TokenTransaction).delete()
            removed['recommendations'] = db.query(Recommendation).delete()
            removed['feedbacks'] = db.query(Feedback).delete()
            removed['performance_metrics'] = db.query(PerformanceMetric).delete()
            removed['trainings'] = db.query(Training).delete()
            removed['employee_skills'] = db.query(EmployeeSkill).delete()
            removed['skill_gap_predictions'] = db.query(SkillGapPrediction).delete()
            removed['user_accounts'] = db.query(UserAccount).delete()
            removed['courses'] = db.query(Course).delete()
            removed['skills'] = db.query(Skill).delete()
            removed['employees'] = db.query(Employee).delete()

        # Best-effort clean vector store directory
        try:
            vs_path = Path(config.VECTOR_STORE_PATH)
            if vs_path.exists():
                for root, dirs, files in os.walk(vs_path, topdown=False):
                    for f in files:
                        try:
                            os.remove(Path(root) / f)
                        except Exception:
                            pass
                    for d in dirs:
                        try:
                            os.rmdir(Path(root) / d)
                        except Exception:
                            pass
        except Exception:
            # Ignore cleanup failures
            pass

        return jsonify({'status': 'success', 'removed': {k: int(v or 0) for k, v in removed.items()}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Training & Assessment Endpoints
# ============================================

@app.route('/api/trainings/<int:training_id>', methods=['GET'])
def get_training_details(training_id):
    """Get training details"""
    try:
        with get_db_context() as db:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return jsonify({'error': 'Training not found'}), 404
            
            return jsonify({
                'id': training.id,
                'employee_id': training.employee_id,
                'course_id': training.course_id,
                'status': training.status,
                'enrollment_date': training.enrollment_date.isoformat() if training.enrollment_date else None,
                'completion_date': training.completion_date.isoformat() if training.completion_date else None,
                'progress_percentage': training.progress_percentage,
                'assessment_score': training.assessment_score
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    """Get course details"""
    try:
        with get_db_context() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return jsonify({'error': 'Course not found'}), 404
            
            return jsonify({
                'id': course.id,
                'course_id': course.course_id,
                'title': course.title,
                'description': course.description,
                'provider': course.provider,
                'category': course.category,
                'difficulty_level': course.difficulty_level,
                'duration_hours': course.duration_hours,
                'rating': course.rating,
                'url': course.url
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trainings/<int:training_id>/complete', methods=['POST'])
def complete_training(training_id):
    """Mark training as completed"""
    try:
        with get_db_context() as db:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return jsonify({'error': 'Training not found'}), 404
            
            training.status = 'Completed'
            training.completion_date = datetime.utcnow()
            training.progress_percentage = 100.0
            db.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Training marked as completed',
                'training': {
                    'id': training.id,
                    'status': training.status,
                    'completion_date': training.completion_date.isoformat()
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trainings/<int:training_id>/generate-assessment', methods=['POST'])
def generate_assessment(training_id):
    """Generate assessment questions for a training"""
    try:
        with get_db_context() as db:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return jsonify({'error': 'Training not found'}), 404
            
            if training.status != 'Completed':
                return jsonify({'error': 'Course must be completed before taking assessment'}), 400
            
            course = db.query(Course).filter(Course.id == training.course_id).first()
            if not course:
                return jsonify({'error': 'Course not found'}), 404
            
            # Generate questions based on course (simple example - in production use AI/question bank)
            questions = generate_course_questions(course)
            
            return jsonify({
                'status': 'success',
                'training_id': training_id,
                'course_title': course.title,
                'questions': questions
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trainings/<int:training_id>/submit-assessment', methods=['POST'])
def submit_assessment(training_id):
    """Submit assessment answers and calculate score"""
    try:
        data = request.json or {}
        user_answers = data.get('answers', [])
        
        with get_db_context() as db:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return jsonify({'error': 'Training not found'}), 404
            
            course = db.query(Course).filter(Course.id == training.course_id).first()
            
            # Generate the same questions to check answers
            questions = generate_course_questions(course)
            
            # Calculate score
            correct_answers = 0
            for i, question in enumerate(questions):
                if i < len(user_answers) and user_answers[i] == question['correct_answer']:
                    correct_answers += 1
            
            score = (correct_answers / len(questions)) * 100 if questions else 0
            
            # Update training with assessment score
            training.assessment_score = round(score, 2)
            db.commit()
            
            return jsonify({
                'status': 'success',
                'score': round(score, 2),
                'correct_answers': correct_answers,
                'total_questions': len(questions),
                'message': f'Assessment completed! You scored {round(score, 2)}%'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_course_questions(course):
    """Generate assessment questions based on course content"""
    # This is a simple implementation - in production, use a proper question bank or AI
    
    # Course-specific questions based on common categories
    question_templates = {
        'Technical': [
            {
                'question': f'What is the primary focus of {course.title}?',
                'options': [
                    'Programming fundamentals',
                    'Advanced concepts and best practices',
                    'Tool configuration',
                    'Project management'
                ],
                'correct_answer': 1
            },
            {
                'question': f'Which skill level is {course.title} designed for?',
                'options': [
                    'Complete beginners',
                    f'{course.difficulty_level} level learners',
                    'Expert professionals',
                    'All levels'
                ],
                'correct_answer': 1
            },
            {
                'question': f'What is the recommended time to complete {course.title}?',
                'options': [
                    f'{course.duration_hours} hours',
                    f'{course.duration_hours * 2} hours',
                    f'{course.duration_hours // 2} hours',
                    'No time limit'
                ],
                'correct_answer': 0
            },
            {
                'question': f'Who is the provider of {course.title}?',
                'options': [
                    'Self-paced learning',
                    course.provider,
                    'Community contributed',
                    'Unknown provider'
                ],
                'correct_answer': 1
            },
            {
                'question': f'What category does {course.title} fall under?',
                'options': [
                    'Business',
                    course.category,
                    'General',
                    'Uncategorized'
                ],
                'correct_answer': 1
            }
        ],
        'Soft Skill': [
            {
                'question': f'What is the main objective of {course.title}?',
                'options': [
                    'Technical skills development',
                    'Improving interpersonal abilities',
                    'Software proficiency',
                    'Hardware knowledge'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of these is a key soft skill?',
                'options': [
                    'Programming',
                    'Communication',
                    'Database management',
                    'Server configuration'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How can you apply soft skills in the workplace?',
                'options': [
                    'Only in meetings',
                    'In all professional interactions',
                    'Only with managers',
                    'Never needed'
                ],
                'correct_answer': 1
            },
            {
                'question': f'What level is {course.title} targeted at?',
                'options': [
                    'Advanced',
                    f'{course.difficulty_level}',
                    'Expert',
                    'Master'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why are soft skills important?',
                'options': [
                    'They help write better code',
                    'They improve team collaboration and productivity',
                    'They are not important',
                    'Only for leadership roles'
                ],
                'correct_answer': 1
            }
        ],
        'Compliance': [
            {
                'question': f'What is the purpose of {course.title}?',
                'options': [
                    'Entertainment',
                    'Meeting legal and regulatory requirements',
                    'Optional learning',
                    'Technical advancement'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why is compliance training important?',
                'options': [
                    'It is not important',
                    'To protect the organization and employees',
                    'Only for legal team',
                    'Just a formality'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How often should compliance training be completed?',
                'options': [
                    'Never',
                    'As required by policy and regulations',
                    'Only once',
                    'Every 10 years'
                ],
                'correct_answer': 1
            },
            {
                'question': f'What category is {course.title}?',
                'options': [
                    'Technical',
                    course.category,
                    'Optional',
                    'Recreational'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Who should complete compliance training?',
                'options': [
                    'Only managers',
                    'All employees as applicable',
                    'Only new hires',
                    'No one'
                ],
                'correct_answer': 1
            }
        ]
    }
    
    # Select appropriate question template
    category = course.category if course.category in question_templates else 'Technical'
    questions = question_templates[category]
    
    # Add IDs to questions
    for i, q in enumerate(questions):
        q['id'] = i + 1
    
    return questions


# ============================================
# Health Check
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'app_name': config.APP_NAME,
        'version': config.APP_VERSION,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
