"""Add new UserRole enum values to PostgreSQL without dropping the column."""
import sys
sys.path.insert(0, ".")

from app.db.session import engine
from sqlalchemy import text

NEW_ROLES = [
    "super_admin", "school_admin", "academic_director",
    "finance_officer", "registrar", "librarian",
    "transport_manager", "hr_manager", "nurse",
    "hostel_manager", "security_officer", "government",
]

with engine.connect() as conn:
    for role in NEW_ROLES:
        try:
            conn.execute(text(f"ALTER TYPE userrole ADD VALUE IF NOT EXISTS '{role}'"))
            conn.commit()
            print(f"  ✓ Added role: {role}")
        except Exception as e:
            print(f"  ⚠ {role}: {e}")
            conn.rollback()

print("\n✅ UserRole enum migration complete")
