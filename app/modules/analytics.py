"""
Analytics and ROI Module
Measures learning effectiveness and readiness improvement
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.base import (
    Employee, Training, EmployeeSkill, SkillGapPrediction,
    PerformanceMetric, Feedback
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Analytics and ROI calculation engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def calculate_workforce_readiness(self, department: Optional[str] = None) -> Dict:
        """
        Calculate overall workforce readiness score
        
        Args:
            department: Optional department filter
        
        Returns:
            Readiness metrics and breakdown
        """
        query = self.db.query(Employee)
        if department:
            query = query.filter(Employee.department == department)
        
        employees = query.all()
        
        if not employees:
            return {
                'readiness_score': 0,
                'total_employees': 0,
                'avg_skill_coverage': 0,
                'distribution': {
                    'high_readiness': 0,
                    'medium_readiness': 0,
                    'low_readiness': 0
                },
                'department': department or 'All'
            }
        
        readiness_scores = []
        skill_coverage = []
        
        for emp in employees:
            # Calculate individual readiness
            emp_skills = self.db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == emp.id
            ).all()
            
            if emp_skills:
                # Average skill proficiency
                avg_proficiency = np.mean([es.proficiency_level for es in emp_skills])
                
                # Skill gap impact
                active_gaps = self.db.query(SkillGapPrediction).filter(
                    SkillGapPrediction.employee_id == emp.id,
                    SkillGapPrediction.is_active == True
                ).all()
                
                gap_penalty = sum(gap.gap_score for gap in active_gaps) / 10.0
                
                # Readiness = proficiency - gap_penalty
                readiness = max(0, avg_proficiency - gap_penalty)
                readiness_scores.append(readiness)
                
                # Skill coverage
                total_skills = self.db.query(func.count(func.distinct(EmployeeSkill.skill_id))).scalar()
                emp_skill_count = len(emp_skills)
                coverage = (emp_skill_count / max(total_skills, 1)) * 100
                skill_coverage.append(coverage)
        
        overall_readiness = np.mean(readiness_scores) if readiness_scores else 0
        avg_coverage = np.mean(skill_coverage) if skill_coverage else 0
        
        # Calculate distribution
        distribution = {
            'high_readiness': sum(1 for s in readiness_scores if s >= 7),
            'medium_readiness': sum(1 for s in readiness_scores if 4 <= s < 7),
            'low_readiness': sum(1 for s in readiness_scores if s < 4)
        }
        
        return {
            'readiness_score': float(overall_readiness),
            'total_employees': len(employees),
            'avg_skill_coverage': float(avg_coverage),
            'distribution': distribution,
            'department': department or 'All'
        }
    
    def calculate_training_roi(self, time_period_days: int = 90) -> Dict:
        """
        Calculate Return on Investment for training programs
        
        Args:
            time_period_days: Period to analyze
        
        Returns:
            ROI metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        # Get completed trainings in period
        completed_trainings = self.db.query(Training).filter(
            Training.status == 'Completed',
            Training.completion_date >= cutoff_date
        ).all()
        
        if not completed_trainings:
            return {'roi': 0, 'total_trainings': 0}
        
        # Calculate costs
        total_cost = 0
        total_hours = 0
        employees_trained = set()
        
        for training in completed_trainings:
            if training.course and training.course.cost:
                total_cost += training.course.cost
            if training.course and training.course.duration_hours:
                total_hours += training.course.duration_hours
            employees_trained.add(training.employee_id)
        
        # Calculate benefits
        # 1. Skill improvement
        skill_improvements = []
        for emp_id in employees_trained:
            before_skills = self.db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == emp_id,
                EmployeeSkill.last_assessed < cutoff_date
            ).all()
            
            after_skills = self.db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == emp_id,
                EmployeeSkill.last_assessed >= cutoff_date
            ).all()
            
            if before_skills and after_skills:
                before_avg = np.mean([s.proficiency_level for s in before_skills])
                after_avg = np.mean([s.proficiency_level for s in after_skills])
                improvement = after_avg - before_avg
                skill_improvements.append(improvement)
        
        avg_skill_improvement = np.mean(skill_improvements) if skill_improvements else 0
        
        # 2. Performance metrics improvement
        performance_improvements = []
        for emp_id in employees_trained:
            before_metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.employee_id == emp_id,
                PerformanceMetric.metric_date < cutoff_date
            ).all()
            
            after_metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.employee_id == emp_id,
                PerformanceMetric.metric_date >= cutoff_date
            ).all()
            
            if before_metrics and after_metrics:
                before_avg = np.mean([m.metric_value for m in before_metrics])
                after_avg = np.mean([m.metric_value for m in after_metrics])
                improvement = ((after_avg - before_avg) / before_avg) * 100 if before_avg > 0 else 0
                performance_improvements.append(improvement)
        
        avg_performance_improvement = np.mean(performance_improvements) if performance_improvements else 0
        
        # Estimate monetary benefit (simplified)
        # Assume 1 point skill improvement = $1000 value per employee
        # Assume 1% performance improvement = $500 value per employee
        estimated_benefit = (
            avg_skill_improvement * len(employees_trained) * 1000 +
            avg_performance_improvement * len(employees_trained) * 500
        )
        
        # Calculate ROI
        roi_percentage = ((estimated_benefit - total_cost) / max(total_cost, 1)) * 100
        
        return {
            'roi_percentage': float(roi_percentage),
            'total_cost': float(total_cost),
            'estimated_benefit': float(estimated_benefit),
            'total_trainings': len(completed_trainings),
            'employees_trained': len(employees_trained),
            'avg_skill_improvement': float(avg_skill_improvement),
            'avg_performance_improvement': float(avg_performance_improvement),
            'total_training_hours': float(total_hours),
            'period_days': time_period_days
        }
    
    def get_training_effectiveness(self, course_id: Optional[int] = None) -> Dict:
        """
        Analyze training effectiveness
        
        Args:
            course_id: Optional specific course to analyze
        
        Returns:
            Effectiveness metrics
        """
        query = self.db.query(Training).filter(Training.status == 'Completed')
        
        if course_id:
            query = query.filter(Training.course_id == course_id)
        
        trainings = query.all()
        
        if not trainings:
            return {'effectiveness_score': 0, 'total_trainings': 0}
        
        # Metrics
        completion_rate = len(trainings) / max(
            self.db.query(Training).filter(
                Training.course_id == course_id if course_id else True
            ).count(), 1
        ) * 100
        
        avg_assessment_score = np.mean([
            t.assessment_score for t in trainings if t.assessment_score
        ]) if any(t.assessment_score for t in trainings) else 0
        
        avg_feedback_rating = np.mean([
            t.feedback_rating for t in trainings if t.feedback_rating
        ]) if any(t.feedback_rating for t in trainings) else 0
        
        # Calculate skill improvement post-training
        skill_improvements = []
        for training in trainings[:50]:  # Sample for performance
            # Get skill assessments before and after training
            pre_skills = self.db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == training.employee_id,
                EmployeeSkill.last_assessed < training.enrollment_date
            ).all()
            
            post_skills = self.db.query(EmployeeSkill).filter(
                EmployeeSkill.employee_id == training.employee_id,
                EmployeeSkill.last_assessed > training.completion_date
            ).all()
            
            if pre_skills and post_skills:
                pre_avg = np.mean([s.proficiency_level for s in pre_skills])
                post_avg = np.mean([s.proficiency_level for s in post_skills])
                improvement = post_avg - pre_avg
                skill_improvements.append(improvement)
        
        avg_skill_improvement = np.mean(skill_improvements) if skill_improvements else 0
        
        # Overall effectiveness score (weighted average)
        effectiveness_score = (
            0.3 * (completion_rate / 100 * 10) +
            0.3 * (avg_assessment_score / 10) +
            0.2 * (avg_feedback_rating / 5 * 10) +
            0.2 * max(0, avg_skill_improvement)
        )
        
        return {
            'effectiveness_score': float(effectiveness_score),
            'completion_rate': float(completion_rate),
            'avg_assessment_score': float(avg_assessment_score),
            'avg_feedback_rating': float(avg_feedback_rating),
            'avg_skill_improvement': float(avg_skill_improvement),
            'total_trainings': len(trainings)
        }
    
    def get_skill_gap_trends(self, time_periods: int = 6) -> Dict:
        """
        Analyze skill gap trends over time
        
        Args:
            time_periods: Number of monthly periods to analyze
        
        Returns:
            Trend data
        """
        trends = []
        
        for i in range(time_periods):
            start_date = datetime.utcnow() - timedelta(days=30 * (i + 1))
            end_date = datetime.utcnow() - timedelta(days=30 * i)
            
            gaps = self.db.query(SkillGapPrediction).filter(
                SkillGapPrediction.predicted_at >= start_date,
                SkillGapPrediction.predicted_at < end_date
            ).all()
            
            if gaps:
                avg_gap_score = np.mean([g.gap_score for g in gaps])
                high_priority_count = sum(1 for g in gaps if g.priority == 'High')
                
                trends.append({
                    'period': start_date.strftime('%Y-%m'),
                    'avg_gap_score': float(avg_gap_score),
                    'high_priority_count': high_priority_count,
                    'total_gaps': len(gaps)
                })
        
        trends.reverse()  # Chronological order
        
        return {
            'trends': trends,
            'periods': time_periods
        }
    
    def get_department_comparison(self) -> List[Dict]:
        """Compare metrics across departments"""
        departments = self.db.query(
            func.distinct(Employee.department)
        ).filter(Employee.department != None).all()
        
        comparisons = []
        
        for (dept,) in departments:
            readiness = self.calculate_workforce_readiness(department=dept)
            
            # Get training participation
            emp_ids = [e.id for e in self.db.query(Employee).filter(
                Employee.department == dept
            ).all()]
            
            total_trainings = self.db.query(Training).filter(
                Training.employee_id.in_(emp_ids)
            ).count()
            
            completed_trainings = self.db.query(Training).filter(
                Training.employee_id.in_(emp_ids),
                Training.status == 'Completed'
            ).count()
            
            comparisons.append({
                'department': dept,
                'readiness_score': readiness['readiness_score'],
                'total_employees': readiness['total_employees'],
                'total_trainings': total_trainings,
                'completed_trainings': completed_trainings,
                'completion_rate': (completed_trainings / max(total_trainings, 1)) * 100
            })
        
        # Sort by readiness score
        comparisons.sort(key=lambda x: x['readiness_score'], reverse=True)
        
        return comparisons
    
    def get_individual_progress(self, employee_id: int, 
                               time_period_days: int = 180) -> Dict:
        """
        Track individual employee progress
        
        Args:
            employee_id: Employee ID
            time_period_days: Period to analyze
        
        Returns:
            Progress metrics
        """
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {'error': 'Employee not found'}
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        # Skill progression
        skill_history = self.db.query(EmployeeSkill).filter(
            EmployeeSkill.employee_id == employee_id
        ).all()
        
        current_avg_skill = np.mean([s.proficiency_level for s in skill_history]) if skill_history else 0
        
        # Training history
        trainings = self.db.query(Training).filter(
            Training.employee_id == employee_id,
            Training.enrollment_date >= cutoff_date
        ).all()
        
        completed = sum(1 for t in trainings if t.status == 'Completed')
        in_progress = sum(1 for t in trainings if t.status == 'In Progress')
        
        # Skill gap reduction
        old_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.predicted_at < cutoff_date
        ).all()
        
        current_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).all()
        
        old_avg_gap = np.mean([g.gap_score for g in old_gaps]) if old_gaps else 0
        current_avg_gap = np.mean([g.gap_score for g in current_gaps]) if current_gaps else 0
        gap_reduction = old_avg_gap - current_avg_gap
        
        return {
            'employee_name': employee.name,
            'current_skill_level': float(current_avg_skill),
            'trainings_completed': completed,
            'trainings_in_progress': in_progress,
            'skill_gap_reduction': float(gap_reduction),
            'current_skill_gaps': len(current_gaps),
            'readiness_improvement': float(gap_reduction / max(old_avg_gap, 1) * 100) if old_avg_gap > 0 else 0,
            'period_days': time_period_days
        }
