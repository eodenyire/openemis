#!/usr/bin/env python
"""
Create default admin user for School Management System
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from accounts.models import User, AdminProfile

def create_admin():
    """Create default admin user"""
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            print("✅ Admin user already exists")
            admin_user = User.objects.get(username='admin')
        else:
            # Create admin user
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@school.com',
                first_name='System',
                last_name='Administrator',
                user_type='admin',
                is_staff=True,
                is_superuser=True
            )
            print("✅ Admin user created successfully")
        
        # Create or get admin profile
        admin_profile, created = AdminProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'employee_id': 'EMP001',
                'department': 'Administration'
            }
        )
        
        if created:
            print("✅ Admin profile created successfully")
        else:
            print("✅ Admin profile already exists")
        
        print("\n" + "="*50)
        print("🎉 Admin user setup completed!")
        print("="*50)
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@school.com")
        print("="*50)
        print("\nYou can now login to:")
        print("• Main site: http://127.0.0.1:8000")
        print("• Admin panel: http://127.0.0.1:8000/admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

if __name__ == '__main__':
    create_admin()