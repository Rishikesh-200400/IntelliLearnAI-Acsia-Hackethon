"""
Configuration module for IntelliLearn AI platform
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "IntelliLearn AI")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./database.db"  # Default to SQLite for easy setup
    )
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    
    # Vector Store
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Model Paths
    MODELS_DIR = Path("./models")
    SKILL_GAP_MODEL_PATH = Path(os.getenv(
        "SKILL_GAP_MODEL_PATH",
        "./models/skill_gap_model.pkl"
    ))
    RECOMMENDER_MODEL_PATH = Path(os.getenv(
        "RECOMMENDER_MODEL_PATH",
        "./models/recommender_model.pkl"
    ))
    
    # Data Paths
    DATA_DIR = Path("./data")
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    
    # Analytics
    ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "365"))
    ROI_CALCULATION_INTERVAL = int(os.getenv("ROI_CALCULATION_INTERVAL", "30"))
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.MODELS_DIR,
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            Path(cls.VECTOR_STORE_PATH)
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Initialize configuration
config = Config()
config.ensure_directories()
