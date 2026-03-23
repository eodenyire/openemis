from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).order_by(User.id).all()
print(f"Total users: {len(users)}\n")
for u in users[:20]:
    print(f"  id={u.id} username={u.username} email={u.email} role={u.role} active={u.is_active} superuser={u.is_superuser}")
db.close()
