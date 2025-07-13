#!/usr/bin/env python3
"""
Startup script for Multi-Agentic Conversational AI
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'openai',
        'python-dotenv',
        'PyPDF2',
        'pymongo',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating .env file template...")
        
        env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=conversational_ai

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file template")
        print("⚠️  Please update OPENAI_API_KEY in .env file")
        return False
    
    print("✅ .env file found")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Multi-Agentic Conversational AI...")
    
    # Check if we're in the right directory
    if not Path('app').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🤖 Multi-Agentic Conversational AI Startup")
    print("=" * 50)
    
    # Run checks
    check_python_version()
    
    if not check_dependencies():
        print("\n📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        if not check_dependencies():
            sys.exit(1)
    
    check_env_file()
    
    print("\n" + "=" * 50)
    print("🎯 Ready to start!")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    print("=" * 50)
    
    start_server()

if __name__ == "__main__":
    main() 