#!/usr/bin/env python
"""
Quick Start Script for openEMIS
Creates initial database schema and admin user
"""
import sys
import app.db.registry  # noqa: F401 – registers all models
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            email="admin@openemis.org",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            first_name="System",
            last_name="Administrator",
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created")
        print("\n" + "="*50)
        print("Admin Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@openemis.org")
        print("="*50 + "\n")
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("\n" + "="*50)
    print("openEMIS Quick Start")
    print("="*50 + "\n")
    
    try:
        init_db()
        create_admin_user()
        
        print("\n✓ Setup complete!")
        print("\nNext steps:")
        print("  1. Run: python run.py")
        print("  2. Open: http://localhost:8000/api/docs")
        print("  3. Login with admin credentials above")
        print("\n")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nMake sure PostgreSQL is running and configured correctly.")
        print("Check your .env file for correct database credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()
