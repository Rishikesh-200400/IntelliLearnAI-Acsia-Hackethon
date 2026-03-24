"""
Hybrid Recommendation Engine
Combines collaborative filtering and content-based filtering using keyword matching
Embeddings disabled due to Windows compatibility issues
"""
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.base import (
    Employee, Course, Training, EmployeeSkill, 
    SkillGapPrediction, Recommendation
)
import logging

# Disable logging to avoid Windows console errors
logging.basicConfig(level=logging.CRITICAL+1)  # Disable all logging
logger = logging.getLogger(__name__)
logger.disabled = True


class HybridRecommender:
    """
    Hybrid recommendation system using:
    1. Content-based filtering (keyword/skill matching)
    2. Collaborative filtering (user-user similarity)
    3. Skill gap prioritization
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
        # self.logger.info("Initialized HybridRecommender with keyword-based matching")
    
    def get_recommendations(self, employee_id: int, top_n: int = 10,
                           include_reasoning: bool = True) -> List[Dict]:
        """
        Generate hybrid recommendations for an employee
        
        Args:
            employee_id: Employee ID
            top_n: Number of recommendations to return
            include_reasoning: Include explanation for each recommendation
        
        Returns:
            List of recommended courses with scores
        """
        try:
            employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                # self.logger.error(f"Employee {employee_id} not found")
                return []
            
            # self.logger.info(f"Getting recommendations for employee {employee_id} ({employee.name})")
            
            # Get different recommendation sources
            try:
                content_recs = self._content_based_recommendations(employee_id)
                # self.logger.info(f"Content recommendations: {len(content_recs)} courses")
            except Exception as e:
                # self.logger.error(f"Error in content recommendations: {e}")
                content_recs = {}
            
            try:
                collab_recs = self._collaborative_filtering(employee_id)
                # self.logger.info(f"Collaborative recommendations: {len(collab_recs)} courses")
            except Exception as e:
                # self.logger.error(f"Error in collaborative filtering: {e}")
                collab_recs = {}
            
            try:
                skill_gap_recs = self._skill_gap_recommendations(employee_id)
                # self.logger.info(f"Skill gap recommendations: {len(skill_gap_recs)} courses")
            except Exception as e:
                # self.logger.error(f"Error in skill gap recommendations: {e}")
                skill_gap_recs = {}
            
            # PRIORITY: Recommend courses ONLY based on skill gaps
            # If employee has skill gaps, only recommend courses that address those gaps
            # Otherwise, fall back to hybrid approach
            
            combined_scores = {}
            
            if skill_gap_recs:
                # Employee has skill gaps - only recommend gap-addressing courses
                for course_id, gap_score in skill_gap_recs.items():
                    # Boost score with role alignment
                    role_score = self._role_match_score(employee, course_id)
                    # 80% skill gap, 20% role match
                    score = (0.8 * gap_score) + (0.2 * role_score)
                    combined_scores[course_id] = score
            
            # FALLBACK: If no skill gap recommendations, use hybrid approach
            if not combined_scores:
                weights = {
                    'content': 0.4,
                    'collaborative': 0.3,
                    'role_match': 0.3
                }
                
                all_course_ids = set(
                    list(content_recs.keys()) + 
                    list(collab_recs.keys())
                )
                
                for course_id in all_course_ids:
                    role_score = self._role_match_score(employee, course_id)
                    score = (
                        weights['content'] * content_recs.get(course_id, 0) +
                        weights['collaborative'] * collab_recs.get(course_id, 0) +
                        weights['role_match'] * role_score
                    )
                    combined_scores[course_id] = score
            
            # ULTIMATE FALLBACK: If still no recommendations, recommend ALL uncompleted courses
            if not combined_scores:
                # self.logger.warning(f"No recommendations found for employee {employee_id}, using all available courses")
                all_courses = self.db.query(Course).all()
                for course in all_courses:
                    # Check if already completed
                    completed = self.db.query(Training).filter(
                        Training.employee_id == employee_id,
                        Training.course_id == course.id,
                        Training.status == 'Completed'
                    ).first()
                    if not completed:
                        # Give each course a base score
                        role_score = self._role_match_score(employee, course.id)
                        combined_scores[course.id] = max(0.1, role_score)  # At least 0.1 score
            
            sorted_courses = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
            
            # Build recommendation list with priority sorting
            # Get skill gaps for priority determination
            skill_gaps = self.db.query(SkillGapPrediction).filter(
                SkillGapPrediction.employee_id == employee_id,
                SkillGapPrediction.is_active == True
            ).all()
            
            # First, categorize courses by which gap priority they address
            course_priority_map = {}
            for course_id, score in sorted_courses:
                course = self.db.query(Course).filter(Course.id == course_id).first()
                if not course:
                    continue
                
                # Determine the highest priority gap this course addresses
                course_text = f"{course.title} {course.description or ''} {course.category or ''}".lower()
                highest_priority = 'Low'  # Default
                
                skill_keywords = {
                    'machine learning': ['machine learning', 'ml', 'deep learning', 'neural', 'ai'],
                    'react': ['react', 'react.js', 'reactjs', 'frontend'],
                    'docker': ['docker', 'container'],
                    'kubernetes': ['kubernetes', 'k8s'],
                    'aws': ['aws', 'amazon web services', 'cloud'],
                    'typescript': ['typescript', 'ts'],
                    'node.js': ['node', 'node.js', 'nodejs', 'backend'],
                    'graphql': ['graphql', 'api'],
                    'ci/cd': ['ci/cd', 'continuous integration', 'devops'],
                    'security best practices': ['security', 'cybersecurity', 'secure']
                }
                
                for gap in skill_gaps:
                    skill_lower = gap.skill_name.lower()
                    keywords = skill_keywords.get(skill_lower, [skill_lower])
                    
                    if any(keyword in course_text for keyword in keywords):
                        if gap.priority == 'High':
                            highest_priority = 'High'
                            break
                        elif gap.priority == 'Medium' and highest_priority != 'High':
                            highest_priority = 'Medium'
                
                course_priority_map[course_id] = (highest_priority, score, course)
            
            # Sort by priority first (High > Medium > Low), then by score
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            sorted_by_priority = sorted(
                course_priority_map.values(),
                key=lambda x: (priority_order.get(x[0], 3), -x[1])
            )
            
            # Build final recommendation list
            recommendations = []
            for priority, score, course in sorted_by_priority:
                rec = {
                    'id': course.id,
                    'course_id': course.id,
                    'title': course.title,
                    'course_title': course.title,  # Also include for compatibility
                    'provider': course.provider,
                    'category': course.category,
                    'difficulty_level': course.difficulty_level,
                    'duration_hours': course.duration_hours,
                    'rating': course.rating,
                    'match_score': float(score),
                    'recommendation_score': float(score),  # Also include for frontend compatibility
                    'url': course.url,
                    'description': course.description,
                    'priority': priority  # Include priority for frontend display
                }
                
                if include_reasoning:
                    rec['reasoning'] = self._generate_reasoning(
                        employee, course, 
                        content_recs.get(course.id, 0),
                        collab_recs.get(course.id, 0),
                        skill_gap_recs.get(course.id, 0)
                    )
                
                recommendations.append(rec)
            
            # self.logger.info(f"Generated {len(recommendations)} recommendations for employee {employee_id}")
            return recommendations
            
        except Exception as e:
            # self.logger.error(f"Error generating recommendations: {e}", exc_info=True)
            # Return empty list on error
            return []

    def _role_match_score(self, employee: Employee, course_id: int) -> float:
        """Score how well a course matches the employee's job role using simple keyword mapping."""
        role_text = (employee.role or '').lower()
        if not role_text:
            return 0.0
        # Map role keywords similar to admin role-course assignment
        keywords: List[str] = []
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

        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return 0.0
        text = f"{course.title} {course.description or ''} {course.category or ''} {course.provider or ''}".lower()
        hits = sum(1 for kw in keywords if kw in text)
        # Normalize: 0 if no hit, then scale with diminishing returns
        if hits == 0:
            return 0.0
        return min(1.0, 0.2 * hits)
    
    def _content_based_recommendations(self, employee_id: int) -> Dict[int, float]:
        """
        Content-based filtering using skill matching (embeddings disabled on Windows)
        """
        scores = {}
        
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return scores
        
        # Get employee skills
        employee_skills = [es.skill.name for es in employee.skills if es.skill and es.skill.name]
        
        # ALWAYS use keyword matching (embeddings disabled on Windows)
        return self._simple_content_matching(employee, employee_skills)
    
    def _simple_content_matching(self, employee: Employee, employee_skills: List[str]) -> Dict[int, float]:
        """Simple keyword-based matching when embeddings are not available"""
        scores = {}
        skills_lower = [s.lower() for s in employee_skills] if employee_skills else []
        role_lower = (employee.role or "").lower()
        
        courses = self.db.query(Course).all()
        for course in courses:
            # Check if already completed
            completed = self.db.query(Training).filter(
                Training.employee_id == employee.id,
                Training.course_id == course.id,
                Training.status == 'Completed'
            ).first()
            if completed:
                continue
            
            course_text = f"{course.title or ''} {course.description or ''} {course.category or ''}".lower()
            
            # Calculate score based on keyword matches
            score = 0.1  # Base score so all courses get some recommendation value
            for skill in skills_lower:
                if skill in course_text:
                    score += 0.3
            
            if role_lower and any(word in course_text for word in role_lower.split() if word):
                score += 0.2
            
            # Always add the course with at least the base score
            scores[course.id] = min(1.0, score)
        
        # Normalize scores
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _collaborative_filtering(self, employee_id: int) -> Dict[int, float]:
        """
        Collaborative filtering based on similar users' training history
        """
        scores = {}
        
        # Get similar employees (same role, similar skills)
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return scores
        
        similar_employees = self.db.query(Employee).filter(
            Employee.role == employee.role,
            Employee.id != employee_id
        ).limit(20).all()
        
        if not similar_employees:
            return scores
        
        # Get courses completed by similar employees
        course_counts = {}
        for similar_emp in similar_employees:
            completed_trainings = self.db.query(Training).filter(
                Training.employee_id == similar_emp.id,
                Training.status == 'Completed',
                Training.assessment_score != None
            ).all()
            
            for training in completed_trainings:
                if training.course_id not in course_counts:
                    course_counts[training.course_id] = {
                        'count': 0,
                        'avg_score': 0,
                        'scores': []
                    }
                course_counts[training.course_id]['count'] += 1
                course_counts[training.course_id]['scores'].append(training.assessment_score)
        
        # Calculate scores based on popularity and quality
        for course_id, data in course_counts.items():
            # Check if current employee already completed
            completed = self.db.query(Training).filter(
                Training.employee_id == employee_id,
                Training.course_id == course_id,
                Training.status == 'Completed'
            ).first()
            
            if not completed:
                # Score = popularity * quality
                popularity = data['count'] / len(similar_employees)
                # Use Python's built-in mean instead of numpy (Windows compatibility)
                avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                quality = avg_score / 100.0  # Normalize to 0-1
                scores[course_id] = popularity * quality
        
        # Normalize scores
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _skill_gap_recommendations(self, employee_id: int) -> Dict[int, float]:
        """
        Recommend courses ONLY if they address identified skill gaps
        Returns empty dict if no gaps or no matching courses
        """
        scores = {}
        
        # Get skill gaps
        skill_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).all()
        
        if not skill_gaps:
            return scores
        
        # Create skill gap profile
        gap_skills = [gap.skill_name for gap in skill_gaps if gap.skill_name]
        
        if not gap_skills:
            return scores
        
        # ALWAYS use keyword matching (embeddings disabled on Windows)
        return self._simple_skill_gap_matching(employee_id, gap_skills)
    
    def _simple_skill_gap_matching(self, employee_id: int, gap_skills: List[str]) -> Dict[int, float]:
        """Simple keyword-based matching for skill gaps when embeddings not available"""
        scores = {}
        gap_skills_lower = [s.lower() for s in gap_skills]
        
        courses = self.db.query(Course).all()
        for course in courses:
            # Check if already completed
            completed = self.db.query(Training).filter(
                Training.employee_id == employee_id,
                Training.course_id == course.id,
                Training.status == 'Completed'
            ).first()
            if completed:
                continue
            
            course_text = f"{course.title} {course.description or ''} {course.category or ''}".lower()
            
            # Check if course addresses any skill gap
            for skill in gap_skills_lower:
                # Flexible keyword matching
                skill_keywords = {
                    'machine learning': ['machine learning', 'ml', 'deep learning', 'neural', 'ai'],
                    'react': ['react', 'react.js', 'reactjs', 'frontend', 'javascript'],
                    'docker': ['docker', 'container'],
                    'kubernetes': ['kubernetes', 'k8s'],
                    'aws': ['aws', 'amazon web services', 'cloud'],
                    'typescript': ['typescript', 'ts'],
                    'node.js': ['node', 'node.js', 'nodejs', 'backend', 'javascript'],
                    'graphql': ['graphql', 'api'],
                    'ci/cd': ['ci/cd', 'continuous integration', 'devops', 'pipeline'],
                    'security best practices': ['security', 'cybersecurity', 'secure']
                }
                
                keywords = skill_keywords.get(skill, [skill])
                matched = any(kw in course_text for kw in keywords)
                
                if matched:
                    if course.id not in scores:
                        scores[course.id] = 0.0
                    scores[course.id] += 0.5
        
        # Normalize scores
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _generate_reasoning(self, employee: Employee, course: Course,
                          content_score: float, collab_score: float, 
                          skill_gap_score: float) -> str:
        """Generate natural language reasoning for recommendation"""
        reasons = []
        
        # Skill gap relevance
        if skill_gap_score > 0.5:
            reasons.append(
                f"Addresses critical skill gaps identified in your profile"
            )
        
        # Content match
        if content_score > 0.5:
            reasons.append(
                f"Aligns well with your role as {employee.role} and current skill set"
            )
        
        # Collaborative signal
        if collab_score > 0.5:
            reasons.append(
                f"Highly rated by professionals in similar roles"
            )
        
        # Course quality
        if course.rating and course.rating >= 4.0:
            reasons.append(
                f"Excellent course rating ({course.rating}/5)"
            )
        
        # Appropriate level
        reasons.append(
            f"{course.difficulty_level} level suits your experience"
        )
        
        return "; ".join(reasons)
    
    def save_recommendations_to_db(self, employee_id: int, 
                                  recommendations: List[Dict]) -> int:
        """Save recommendations to database"""
        count = 0
        
        for rec in recommendations:
            recommendation = Recommendation(
                employee_id=employee_id,
                course_id=rec['course_id'],
                recommendation_score=rec['recommendation_score'],
                reasoning=rec.get('reasoning', ''),
                recommendation_type='Hybrid',
                recommended_at=datetime.utcnow()
            )
            self.db.add(recommendation)
            count += 1
        
        self.db.commit()
        return count
    
    def get_learning_path(self, employee_id: int) -> List[Dict]:
        """
        Generate a structured learning path based on recommendations
        """
        recommendations = self.get_recommendations(employee_id, top_n=15)
        
        # Group by difficulty level
        beginner = [r for r in recommendations if r['difficulty_level'] == 'Beginner']
        intermediate = [r for r in recommendations if r['difficulty_level'] == 'Intermediate']
        advanced = [r for r in recommendations if r['difficulty_level'] == 'Advanced']
        
        learning_path = []
        
        if beginner:
            learning_path.append({
                'stage': 'Foundation',
                'level': 'Beginner',
                'courses': beginner[:3],
                'estimated_duration_weeks': sum(c['duration_hours'] for c in beginner[:3]) / 10
            })
        
        if intermediate:
            learning_path.append({
                'stage': 'Development',
                'level': 'Intermediate',
                'courses': intermediate[:4],
                'estimated_duration_weeks': sum(c['duration_hours'] for c in intermediate[:4]) / 10
            })
        
        if advanced:
            learning_path.append({
                'stage': 'Mastery',
                'level': 'Advanced',
                'courses': advanced[:3],
                'estimated_duration_weeks': sum(c['duration_hours'] for c in advanced[:3]) / 10
            })
        
        return learning_path
