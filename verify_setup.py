"""
Verification script to check if IntelliLearn AI setup is correct
"""
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    required = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'sqlalchemy': 'sqlalchemy',
        'langchain': 'langchain',
        'sentence-transformers': 'sentence_transformers',
        'plotly': 'plotly',
        'xgboost': 'xgboost'
    }
    
    all_installed = True
    for package, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            all_installed = False
    
    return all_installed

def check_directory_structure():
    """Check if required directories exist"""
    print("\nChecking directory structure...")
    required_dirs = [
        "app",
        "app/models",
        "app/modules",
        "data",
        "models"
    ]
    
    all_exist = True
    for directory in required_dirs:
        path = Path(directory)
        if path.exists():
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ (missing)")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if required files exist"""
    print("\nChecking critical files...")
    required_files = [
        "app.py",
        "requirements.txt",
        ".env.example",
        "generate_sample_data.py",
        "app/config.py",
        "app/database.py",
        "app/models/base.py",
        "app/modules/skill_gap_predictor.py",
        "app/modules/llm_assistant.py",
        "app/modules/recommender.py"
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            all_exist = False
    
    return all_exist

def check_sample_data():
    """Check if sample data exists"""
    print("\nChecking sample data...")
    sample_files = [
        "data/sample/employees.csv",
        "data/sample/skills.csv",
        "data/sample/employee_skills.csv",
        "data/sample/courses.csv",
        "data/sample/training_history.csv"
    ]
    
    all_exist = True
    for file in sample_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ⚠ {file} (run generate_sample_data.py)")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print(f"  ✓ .env file exists")
        return True
    elif env_example_path.exists():
        print(f"  ⚠ .env file not found (copy from .env.example)")
        return False
    else:
        print(f"  ✗ No environment files found")
        return False

def main():
    """Run all checks"""
    print("="*60)
    print("IntelliLearn AI - Setup Verification")
    print("="*60)
    print()
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Directory Structure": check_directory_structure(),
        "Critical Files": check_files(),
        "Sample Data": check_sample_data(),
        "Environment Config": check_env_file()
    }
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {check}")
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ Setup verification successful!")
        print("\nYou can now run: streamlit run app.py")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Generate sample data: python generate_sample_data.py")
        print("  - Create .env file: copy .env.example .env")
    
    print()
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
