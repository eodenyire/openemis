#!/usr/bin/env python3
"""
Quick start script for School Management System
"""

import os
import sys
import subprocess

def check_python():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_venv():
    """Check if virtual environment exists"""
    return os.path.exists('venv')

def run_command(command, description="Running command"):
    """Execute a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False, e.stderr

def main():
    print("🎓 School Management System - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    # Check if setup is needed
    if not check_venv():
        print("\n📦 Virtual environment not found. Running setup...")
        success, output = run_command("python setup.py", "Setting up the project")
        if not success:
            print("❌ Setup failed. Please run 'python setup.py' manually.")
            sys.exit(1)
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate && '
        python_cmd = 'python'
    else:  # Unix/Linux/Mac
        activate_cmd = 'source venv/bin/activate && '
        python_cmd = 'python'
    
    # Check if migrations are needed
    print("\n🔄 Checking database status...")
    success, output = run_command(f'{activate_cmd}{python_cmd} manage.py showmigrations --plan', 
                                 "Checking migrations")
    
    if success and '[ ]' in output:
        print("📊 Applying database migrations...")
        run_command(f'{activate_cmd}{python_cmd} manage.py migrate', "Applying migrations")
    
    # Check if superuser exists
    print("\n👤 Checking for superuser...")
    success, output = run_command(f'{activate_cmd}{python_cmd} manage.py shell -c "from accounts.models import User; print(User.objects.filter(is_superuser=True).exists())"', 
                                 "Checking superuser")
    
    if success and 'False' in output:
        print("\n🔐 No superuser found. You'll need to create one.")
        print("After the server starts, press Ctrl+C and run:")
        print(f"   {activate_cmd}{python_cmd} manage.py createsuperuser")
    
    # Start the development server
    print("\n🚀 Starting development server...")
    print("=" * 50)
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🔧 Admin panel available at: http://127.0.0.1:8000/admin")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run(f'{activate_cmd}{python_cmd} manage.py runserver', shell=True, check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using School Management System!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if migrations are applied: python manage.py migrate")
        print("3. Verify your .env file configuration")

if __name__ == '__main__':
    main()