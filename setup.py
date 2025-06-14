"""
Deployment and setup script for FlashForge AI
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def create_sample_env():
    """Create a sample .env file for environment variables"""
    env_content = """# FlashForge AI Environment Variables
# Copy this file to .env and add your actual API key

# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom model settings
# MODEL_NAME=gpt-3.5-turbo
# MAX_TOKENS=2000
# TEMPERATURE=0.3
"""
    
    env_file = Path(".env.example")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env.example file")
    else:
        print("✅ .env.example already exists")

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "test_flashforge.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 FlashForge AI Deployment Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create sample environment file
    create_sample_env()
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed but continuing with setup")
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your OpenAI API key to .env")
    print("3. Run: streamlit run app.py")
    print("4. Or run CLI version: python cli.py")
    print("\n📖 Documentation: See README.md for detailed instructions")

if __name__ == "__main__":
    main()
