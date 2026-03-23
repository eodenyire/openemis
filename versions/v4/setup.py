#!/usr/bin/env python3
"""
School Management System Setup Script
This script helps set up the Django application
"""

import os
import sys
import subprocess
import secrets

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}: {e.stderr}")
        return None

def create_env_file():
    """Create .env file from .env.example"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as example_file:
                content = example_file.read()
            
            # Generate a random secret key
            secret_key = secrets.token_urlsafe(50)
            content = content.replace('your-secret-key-here', secret_key)
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✓ Created .env file with generated secret key")
        else:
            print("✗ .env.example file not found")
    else:
        print("✓ .env file already exists")

def main():
    print("🎓 School Management System Setup")
    print("=" * 40)
    
    # Check if Python is available
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        run_command('python -m venv venv', 'Creating virtual environment')
    else:
        print("✓ Virtual environment already exists")
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate && '
    else:  # Unix/Linux/Mac
        activate_cmd = 'source venv/bin/activate && '
    
    run_command(f'{activate_cmd}pip install --upgrade pip', 'Upgrading pip')
    run_command(f'{activate_cmd}pip install -r requirements.txt', 'Installing Python packages')
    
    # Create .env file
    create_env_file()
    
    # Run Django migrations
    run_command(f'{activate_cmd}python manage.py makemigrations', 'Creating database migrations')
    run_command(f'{activate_cmd}python manage.py migrate', 'Applying database migrations')
    
    # Create superuser prompt
    print("\n" + "=" * 40)
    print("Setup completed successfully! 🎉")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Create a superuser account:")
    print("   python manage.py createsuperuser")
    
    print("3. Start the development server:")
    print("   python manage.py runserver")
    
    print("\n4. Open your browser and go to:")
    print("   http://127.0.0.1:8000")
    
    print("\n5. Admin panel is available at:")
    print("   http://127.0.0.1:8000/admin")

if __name__ == '__main__':
    main()