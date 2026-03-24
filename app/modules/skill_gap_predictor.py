"""
Skill Gap Prediction Module
Uses ML models (Random Forest, XGBoost) to forecast missing skills
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import xgboost as xgb
import joblib
from sqlalchemy.orm import Session
from app.models.base import Employee, EmployeeSkill, Skill, Training, SkillGapPrediction
from app.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillGapPredictor:
    """Predicts skill gaps using machine learning models"""
    
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.skill_encoder = LabelEncoder()
        self.logger = logger
        self.model_path = config.SKILL_GAP_MODEL_PATH
    
    def prepare_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare feature matrix and target variable from database
        Features include: employee attributes, current skill levels, training history
        Target: skill proficiency levels or gap indicators
        """
        # Get all employees with their skills
        employees = db.query(Employee).all()
        
        data = []
        for emp in employees:
            # Get employee skills
            emp_skills = {
                es.skill.name: es.proficiency_level 
                for es in emp.skills
            }
            
            # Get training statistics
            trainings = db.query(Training).filter(
                Training.employee_id == emp.id
            ).all()
            
            completed_trainings = sum(1 for t in trainings if t.status == 'Completed')
            avg_training_score = np.mean([t.assessment_score for t in trainings if t.assessment_score]) if trainings else 0
            
            # Create feature row for each skill
            all_skills = db.query(Skill).all()
            for skill in all_skills:
                row = {
                    'employee_id': emp.id,
                    'skill_name': skill.name,
                    'years_of_experience': emp.years_of_experience or 0,
                    'job_level': emp.job_level or 'Junior',
                    'department': emp.department or 'General',
                    'completed_trainings': completed_trainings,
                    'avg_training_score': avg_training_score,
                    'current_proficiency': emp_skills.get(skill.name, 0),
                    'skill_category': skill.category or 'General',
                    'skill_importance': skill.importance_score or 1.0
                }
                data.append(row)
        
        df = pd.DataFrame(data)
        
        # Fill any missing values
        df['job_level'] = df['job_level'].fillna('Junior')
        df['department'] = df['department'].fillna('General')
        df['skill_category'] = df['skill_category'].fillna('General')
        
        # Encode categorical variables using LabelEncoder for consistency
        from sklearn.preprocessing import LabelEncoder
        
        job_level_encoder = LabelEncoder()
        department_encoder = LabelEncoder()
        skill_category_encoder = LabelEncoder()
        
        df['job_level_encoded'] = job_level_encoder.fit_transform(df['job_level'])
        df['department_encoded'] = department_encoder.fit_transform(df['department'])
        df['skill_category_encoded'] = skill_category_encoder.fit_transform(df['skill_category'])
        
        # Select features
        feature_columns = [
            'years_of_experience', 'job_level_encoded', 'department_encoded',
            'completed_trainings', 'avg_training_score', 'skill_category_encoded',
            'skill_importance'
        ]
        
        X = df[feature_columns]
        y = df['current_proficiency']  # Target: predict proficiency level
        
        return X, y, df
    
    def train_models(self, db: Session) -> Dict:
        """Train both Random Forest and XGBoost models"""
        self.logger.info("Preparing training data...")
        X, y, full_df = self.prepare_training_data(db)
        
        if len(X) < 10:
            self.logger.warning("Insufficient data for training. Need at least 10 samples.")
            return {'status': 'insufficient_data'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.logger.info("Training Random Forest model...")
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train_scaled, y_train)
        rf_pred = self.rf_model.predict(X_test_scaled)
        rf_score = r2_score(y_test, rf_pred)
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
        
        # Train XGBoost
        self.logger.info("Training XGBoost model...")
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.xgb_model.fit(X_train_scaled, y_train)
        xgb_pred = self.xgb_model.predict(X_test_scaled)
        xgb_score = r2_score(y_test, xgb_pred)
        xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
        
        # Save models
        self.save_models()
        
        results = {
            'status': 'success',
            'random_forest': {
                'r2_score': float(rf_score),
                'rmse': float(rf_rmse)
            },
            'xgboost': {
                'r2_score': float(xgb_score),
                'rmse': float(xgb_rmse)
            },
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        self.logger.info(f"Model training complete: {results}")
        return results
    
    def predict_skill_gaps(self, db: Session, employee_id: int, 
                          required_level: float = 7.0) -> List[Dict]:
        """
        Predict skill gaps for a specific employee
        
        Args:
            db: Database session
            employee_id: Employee ID
            required_level: Minimum required proficiency level
        
        Returns:
            List of predicted skill gaps with priorities
        """
        if not self.rf_model or not self.xgb_model:
            self.load_models()
        
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return []
        
        # Get current skills
        current_skills = {
            es.skill.name: es.proficiency_level 
            for es in employee.skills
        }
        
        # Get training stats
        trainings = db.query(Training).filter(
            Training.employee_id == employee_id
        ).all()
        completed_trainings = sum(1 for t in trainings if t.status == 'Completed')
        avg_training_score = np.mean([t.assessment_score for t in trainings if t.assessment_score]) if trainings else 0
        
        # Predict for all skills
        all_skills = db.query(Skill).all()
        gaps = []
        
        for skill in all_skills:
            # Prepare feature vector with safe encoding
            job_level = employee.job_level or 'Junior'
            department = employee.department or 'General'
            skill_category = skill.category or 'General'
            
            # Simple numeric encoding (use hash mod for consistency)
            job_level_encoded = hash(job_level) % 10
            department_encoded = hash(department) % 10
            skill_category_encoded = hash(skill_category) % 10
            
            features = np.array([[
                employee.years_of_experience or 0,
                job_level_encoded,
                department_encoded,
                completed_trainings,
                avg_training_score,
                skill_category_encoded,
                skill.importance_score or 1.0
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict using both models and average
            rf_pred = self.rf_model.predict(features_scaled)[0]
            xgb_pred = self.xgb_model.predict(features_scaled)[0]
            predicted_level = (rf_pred + xgb_pred) / 2
            
            current_level = current_skills.get(skill.name, 0)
            gap_score = required_level - predicted_level
            
            # Only include if there's a significant gap
            if gap_score > 1.0:
                # Calculate priority based on gap size and skill importance
                priority_score = gap_score * (skill.importance_score or 1.0)
                
                if priority_score > 3.0:
                    priority = 'High'
                elif priority_score > 1.5:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                gaps.append({
                    'skill_name': skill.name,
                    'skill_category': skill.category,
                    'current_level': float(current_level),
                    'predicted_level': float(predicted_level),
                    'required_level': float(required_level),
                    'gap_score': float(gap_score),
                    'priority': priority,
                    'confidence_score': float(min(abs(rf_pred - xgb_pred), 1.0))  # Lower difference = higher confidence
                })
        
        # Sort by priority and gap score
        gaps.sort(key=lambda x: (-['High', 'Medium', 'Low'].index(x['priority']), -x['gap_score']))
        
        return gaps
    
    def save_predictions_to_db(self, db: Session, employee_id: int, gaps: List[Dict]):
        """Save skill gap predictions to database"""
        # Mark old predictions as inactive
        db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).update({'is_active': False})
        
        # Add new predictions
        for gap in gaps:
            prediction = SkillGapPrediction(
                employee_id=employee_id,
                skill_name=gap['skill_name'],
                current_level=gap['current_level'],
                required_level=gap['required_level'],
                gap_score=gap['gap_score'],
                priority=gap['priority'],
                confidence_score=gap['confidence_score'],
                predicted_at=datetime.utcnow(),
                is_active=True
            )
            db.add(prediction)
        
        db.commit()
    
    def save_models(self):
        """Save trained models to disk"""
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'rf_model': self.rf_model,
            'xgb_model': self.xgb_model,
            'scaler': self.scaler,
            'timestamp': datetime.utcnow()
        }
        
        joblib.dump(model_data, self.model_path)
        self.logger.info(f"Models saved to {self.model_path}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(self.model_path)
            self.rf_model = model_data['rf_model']
            self.xgb_model = model_data['xgb_model']
            self.scaler = model_data['scaler']
            self.logger.info(f"Models loaded from {self.model_path}")
        except FileNotFoundError:
            self.logger.warning("No saved models found. Please train models first.")
