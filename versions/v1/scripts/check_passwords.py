from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import verify_password

db = SessionLocal()

test_cases = [
    ("admin", "admin123"),
    ("admin", "Admin@1234"),
    ("eodenyire", "eodenyire"),
    ("teacher001", "Teacher@1234"),
    ("student001", "Student@1234"),
    ("staff001", "Staff@1234"),
    ("parent001", "Parent@1234"),
]

for username, password in test_cases:
    u = db.query(User).filter(User.username == username).first()
    if u:
        ok = verify_password(password, u.hashed_password)
        print(f"  {username} / {password} => {'✓ WORKS' if ok else '✗ wrong password'}")
    else:
        print(f"  {username} => user not found")

db.close()
