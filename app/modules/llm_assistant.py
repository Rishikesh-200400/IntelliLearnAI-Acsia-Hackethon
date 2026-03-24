"""
LLM Conversational Assistant with RAG
Built using LangChain + Mistral/GPT for interactive learning guidance
"""
from typing import List, Dict, Optional, Any
import re
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain.embeddings import HuggingFaceEmbeddings

try:
    from langchain_community.vectorstores import Chroma, FAISS
except ImportError:
    from langchain.vectorstores import Chroma, FAISS

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

# Optional imports - not critical for basic functionality
ConversationalRetrievalChain = None
ConversationBufferMemory = None
PromptTemplate = None

try:
    from langchain.chains import ConversationalRetrievalChain
except ImportError:
    pass

try:
    from langchain.memory import ConversationBufferMemory
except ImportError:
    pass

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    try:
        from langchain_core.prompts import PromptTemplate
    except ImportError:
        pass

try:
    from langchain.llms.base import LLM
except ImportError:
    try:
        from langchain_core.language_models.llms import LLM
    except ImportError:
        from langchain_core.language_models import BaseLLM as LLM
from sqlalchemy.orm import Session
from app.models.base import Employee, Course, EmployeeSkill, SkillGapPrediction
from app.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalLLMWrapper:
    """Wrapper for local LLM or API-based LLMs"""
    
    def __init__(self, provider: str = "local"):
        self.provider = provider
        self.logger = logger
        
    @property
    def _llm_type(self) -> str:
        return self.provider
    
    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Make the class callable"""
        return self._call(prompt, stop)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Call the LLM - This is a placeholder for actual LLM integration
        In production, integrate with OpenAI, Mistral, or local models
        """
        # Placeholder response - integrate with actual LLM API
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "mistral":
            return self._call_mistral(prompt)
        else:
            return self._generate_rule_based_response(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model=config.LLM_MODEL or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_rule_based_response(prompt)
    
    def _call_mistral(self, prompt: str) -> str:
        """Call Mistral API"""
        try:
            from mistralai import Mistral
            
            client = Mistral(api_key=config.MISTRAL_API_KEY)
            response = client.chat.complete(
                model=config.LLM_MODEL or "mistral-medium",
                messages=[{"role": "user", "content": prompt}],
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Mistral API error: {e}")
            return self._generate_rule_based_response(prompt)
    
    def _generate_rule_based_response(self, prompt: str) -> str:
        """Generate a rule-based response when LLM is not available"""
        prompt_lower = prompt.lower()
        
        if "skill gap" in prompt_lower or "missing skill" in prompt_lower:
            return "Based on your profile, I've identified several skill gaps. Let me recommend some personalized courses to help you bridge these gaps and advance your career."
        elif "recommend" in prompt_lower or "course" in prompt_lower:
            return "I can recommend personalized courses based on your current skills, career goals, and identified skill gaps. What specific area would you like to focus on?"
        elif "career" in prompt_lower or "growth" in prompt_lower:
            return "To support your career growth, I'll analyze your skill profile and recommend learning paths aligned with your goals. What's your target role or area of expertise?"
        else:
            return "I'm here to help you with personalized learning recommendations, skill gap analysis, and career development guidance. How can I assist you today?"


class LLMAssistant:
    """LLM-powered conversational assistant for personalized learning"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
        
        # Initialize embedding model (optional, disable if causing issues)
        self.embeddings = None
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu', 'trust_remote_code': False}
            )
            self.logger.info("Embeddings model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load embeddings model: {e}. RAG features will be limited.")
        
        # Initialize LLM
        self.llm = LocalLLMWrapper(provider=config.LLM_PROVIDER)
        
        # Initialize vector store for RAG
        self.vector_store = None
        self.retrieval_chain = None
        
        # Conversation memory (optional)
        if ConversationBufferMemory:
            try:
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="answer"
                )
            except:
                self.memory = {}  # Simple dict fallback
        else:
            self.memory = {}  # Simple dict fallback
        
        # Initialize RAG system (optional)
        try:
            self._initialize_rag_system()
        except Exception as e:
            self.logger.warning(f"RAG system initialization failed: {e}. Using basic mode.")
    
    def _initialize_rag_system(self):
        """Initialize Retrieval-Augmented Generation system"""
        try:
            # Skip if embeddings not available
            if not self.embeddings:
                self.logger.info("Skipping RAG initialization - embeddings not available")
                return
            
            # Get all courses from database
            courses = self.db.query(Course).all()
            
            if not courses:
                self.logger.warning("No courses found in database for RAG initialization")
                return
            
            # Create documents from courses
            documents = []
            for course in courses:
                doc_text = f"""
                Course: {course.title}
                Provider: {course.provider}
                Category: {course.category}
                Level: {course.difficulty_level}
                Duration: {course.duration_hours} hours
                Description: {course.description}
                Rating: {course.rating}/5
                """
                documents.append(doc_text)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            splits = text_splitter.create_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                splits,
                self.embeddings
            )
            
            # Create retrieval chain
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            
            # Create retrieval chain if components available
            if ConversationalRetrievalChain and PromptTemplate:
                try:
                    # Custom prompt template
                    prompt_template = """You are IntelliLearn AI, a personalized learning mentor. 
                    Use the following course information to answer the user's question about learning and skill development.
                    
                    Context: {context}
                    
                    Question: {question}
                    
                    Provide a helpful, encouraging response that guides the user towards relevant learning opportunities.
                    If recommending courses, explain why they're suitable based on the user's needs.
                    
                    Answer:"""
                    
                    PROMPT = PromptTemplate(
                        template=prompt_template,
                        input_variables=["context", "question"]
                    )
                    
                    self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                        llm=self.llm,
                        retriever=retriever,
                        memory=self.memory,
                        return_source_documents=True,
                        combine_docs_chain_kwargs={"prompt": PROMPT}
                    )
                    
                    self.logger.info("RAG system with chains initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Could not create retrieval chain: {e}. Using simple retrieval.")
            else:
                self.logger.info("RAG system initialized with basic retrieval (chains not available)")
            
        except Exception as e:
            self.logger.error(f"Error initializing RAG system: {e}")
    
    def chat(self, employee_id: int, message: str) -> Dict[str, Any]:
        """
        Interactive chat with the LLM assistant
        
        Args:
            employee_id: Employee ID for personalized context
            message: User's message
        
        Returns:
            Response with answer and relevant context
        """
        # Get employee context
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"error": "Employee not found"}
        
        # Get employee's skill gaps
        skill_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).order_by(SkillGapPrediction.gap_score.desc()).limit(5).all()
        
        # Add context to the message
        context = f"""
        Employee: {employee.name}
        Role: {employee.role}
        Department: {employee.department}
        Experience: {employee.years_of_experience} years
        
        Top Skill Gaps:
        {chr(10).join([f"- {gap.skill_name} (Gap: {gap.gap_score:.1f}, Priority: {gap.priority})" for gap in skill_gaps])}
        
        User Query: {message}
        """
        
        try:
            # If user asks about weakness in a specific skill, recommend courses directly
            mentioned_skills = self._extract_target_skills(message)
            if mentioned_skills:
                recs = self._recommend_courses_for_skills(employee, mentioned_skills, top_n=5)
                if recs:
                    lines = [
                        f"I found these courses to help improve {', '.join(mentioned_skills)}:",
                        ""
                    ]
                    for i, c in enumerate(recs, 1):
                        line = f"{i}. {c['course_title']} — {c.get('provider') or 'Provider'}\n   Link: {c.get('url') or 'N/A'}"
                        lines.append(line)
                    answer_text = "\n".join(lines)
                    return {
                        "answer": answer_text,
                        "recommended_courses": recs,
                        "timestamp": datetime.utcnow().isoformat()
                    }

            if self.retrieval_chain:
                # Use RAG for response
                result = self.retrieval_chain({"question": context})
                
                return {
                    "answer": result["answer"],
                    "source_documents": [
                        doc.page_content for doc in result.get("source_documents", [])
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Fallback to direct LLM call
                response = self.llm._call(context)
                return {
                    "answer": response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return {
                "error": str(e),
                "fallback_answer": "I'm here to help with your learning journey. Could you please rephrase your question?"
            }

    def _extract_target_skills(self, message: str) -> List[str]:
        """Extract skills the user says they are weak in or want to improve."""
        import re
        text = (message or '').lower()
        # Common patterns: "weak in X", "improve X", "learn X", "struggle with X"
        patterns = [
            r"weak in ([a-z0-9+\-_/.,\s]+)",
            r"improve ([a-z0-9+\-_/.,\s]+)",
            r"learn ([a-z0-9+\-_/.,\s]+)",
            r"struggle with ([a-z0-9+\-_/.,\s]+)",
            r"lack (?:knowledge in|skills in|of)?\s*([a-z0-9+\-_/.,\s]+)",
        ]
        found: List[str] = []
        for pat in patterns:
            for m in re.findall(pat, text):
                found.append(m.strip())
        # Split by commas/and if present
        skills: List[str] = []
        for chunk in found:
            for part in re.split(r"[,/]| and ", chunk):
                token = part.strip()
                if token and 1 <= len(token) <= 64:
                    skills.append(token)
        # Deduplicate
        uniq: List[str] = []
        for s in skills:
            if s not in uniq:
                uniq.append(s)
        return uniq[:5]

    def _recommend_courses_for_skills(self, employee: Employee, skills: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """Find courses matching the requested skills, prioritized by role alignment and keyword hits."""
        role_text = (employee.role or '').lower()
        # Build keyword set: user-mentioned skills + role keywords
        keywords: List[str] = []
        for s in skills:
            keywords += [w.strip().lower() for w in re.split(r"\s+", s) if w.strip()]
        # Role keywords similar to elsewhere
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

        # Score courses by keyword hits
        courses = self.db.query(Course).all()
        def score_course(c: Course) -> float:
            text = f"{c.title} {c.description or ''} {c.category or ''} {c.provider or ''}".lower()
            hits = sum(1 for kw in keywords if kw and kw in text)
            # Light boost for higher rating
            rating_boost = (c.rating or 0) / 10.0
            return hits + rating_boost

        ranked = sorted(courses, key=score_course, reverse=True)
        picked = [c for c in ranked if score_course(c) > 0][:top_n]
        if not picked:
            picked = ranked[:top_n]

        results: List[Dict[str, Any]] = []
        for c in picked:
            results.append({
                "course_id": c.id,
                "course_title": c.title,
                "provider": c.provider,
                "url": c.url,
                "difficulty_level": c.difficulty_level,
                "rating": c.rating,
            })
        return results
    
    def get_personalized_guidance(self, employee_id: int) -> Dict[str, Any]:
        """
        Generate personalized learning guidance for an employee
        """
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"error": "Employee not found"}
        
        # Get skill gaps
        skill_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).order_by(SkillGapPrediction.gap_score.desc()).all()
        
        # Get current skills
        current_skills = [es.skill.name for es in employee.skills]
        
        guidance = {
            "employee_name": employee.name,
            "role": employee.role,
            "current_skills": current_skills,
            "skill_gaps": [
                {
                    "skill": gap.skill_name,
                    "priority": gap.priority,
                    "gap_score": float(gap.gap_score)
                }
                for gap in skill_gaps[:5]
            ],
            "recommendations": self._generate_recommendations_text(employee, skill_gaps),
            "learning_path": self._generate_learning_path(skill_gaps)
        }
        
        return guidance
    
    def _generate_recommendations_text(self, employee: Employee, 
                                      skill_gaps: List[SkillGapPrediction]) -> str:
        """Generate personalized recommendation text"""
        if not skill_gaps:
            return f"Great job, {employee.name}! Your skill profile is strong. Consider exploring advanced topics in your field."
        
        high_priority = [gap for gap in skill_gaps if gap.priority == 'High']
        
        text = f"Hello {employee.name}! Based on your role as {employee.role}, "
        text += f"I've identified {len(high_priority)} high-priority skill gaps that could significantly impact your career growth.\n\n"
        
        for i, gap in enumerate(high_priority[:3], 1):
            text += f"{i}. **{gap.skill_name}**: This skill is crucial for your role. "
            text += f"Your current proficiency could be improved by {gap.gap_score:.1f} points.\n"
        
        text += "\nI recommend focusing on these areas through targeted learning programs. "
        text += "Would you like me to suggest specific courses?"
        
        return text
    
    def _generate_learning_path(self, skill_gaps: List[SkillGapPrediction]) -> List[Dict]:
        """Generate a structured learning path"""
        path = []
        
        # Group by priority
        high_priority = [gap for gap in skill_gaps if gap.priority == 'High']
        medium_priority = [gap for gap in skill_gaps if gap.priority == 'Medium']
        
        # Phase 1: High priority skills
        if high_priority:
            path.append({
                "phase": 1,
                "name": "Foundation Building",
                "duration_weeks": 4 * len(high_priority[:2]),
                "skills": [gap.skill_name for gap in high_priority[:2]],
                "focus": "Address critical skill gaps"
            })
        
        # Phase 2: More high priority or medium priority
        remaining_high = high_priority[2:]
        if remaining_high or medium_priority:
            skills = [gap.skill_name for gap in (remaining_high + medium_priority)[:2]]
            path.append({
                "phase": 2,
                "name": "Skill Enhancement",
                "duration_weeks": 4 * len(skills),
                "skills": skills,
                "focus": "Broaden your expertise"
            })
        
        # Phase 3: Advanced topics
        path.append({
            "phase": 3,
            "name": "Advanced Mastery",
            "duration_weeks": 8,
            "skills": ["Advanced topics", "Specialization"],
            "focus": "Achieve expert-level proficiency"
        })
        
        return path
    
    def explain_recommendation(self, employee_id: int, course_id: int) -> str:
        """Generate natural language explanation for why a course is recommended"""
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        course = self.db.query(Course).filter(Course.id == course_id).first()
        
        if not employee or not course:
            return "Unable to generate explanation."
        
        # Get relevant skill gaps
        skill_gaps = self.db.query(SkillGapPrediction).filter(
            SkillGapPrediction.employee_id == employee_id,
            SkillGapPrediction.is_active == True
        ).all()
        
        explanation = f"I recommend '{course.title}' for you because:\n\n"
        explanation += f"1. **Relevance**: This {course.difficulty_level} course aligns with your role as {employee.role}.\n"
        explanation += f"2. **Skill Development**: It addresses key areas where you can improve.\n"
        explanation += f"3. **Quality**: Rated {course.rating}/5 by learners, ensuring high-quality content.\n"
        explanation += f"4. **Time Investment**: {course.duration_hours} hours - manageable alongside your work.\n\n"
        explanation += "Completing this course will help bridge your skill gaps and accelerate your career growth."
        
        return explanation
