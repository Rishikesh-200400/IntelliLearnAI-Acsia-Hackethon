"""
Setup and initialization script for IntelliLearn AI
"""
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/sample",
        "data/raw",
        "data/processed",
        "data/vector_store",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Created directory structure")

def install_dependencies():
    """Install required packages"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def generate_sample_data():
    """Generate sample data"""
    print("\nGenerating sample data...")
    try:
        subprocess.check_call([sys.executable, "generate_sample_data.py"])
        print("✓ Sample data generated")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating sample data: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from template")
    else:
        print("✓ .env file already exists")

def main():
    """Main setup function"""
    print("="*60)
    print("IntelliLearn AI - Setup")
    print("="*60)
    print()
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Ask user if they want to install dependencies
    print("\n" + "="*60)
    response = input("Install dependencies? (y/n): ").lower()
    if response == 'y':
        install_dependencies()
    
    # Ask user if they want to generate sample data
    print("\n" + "="*60)
    response = input("Generate sample data? (y/n): ").lower()
    if response == 'y':
        generate_sample_data()
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file to add your API keys (optional)")
    print("2. Run: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print()

if __name__ == "__main__":
    main()
