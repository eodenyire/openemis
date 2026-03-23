import requests

BASE = "http://localhost:8000/api/v1"

# Login
r = requests.post(f"{BASE}/auth/login", data={"username": "admin", "password": "admin123"})
data = r.json()
token = data["access_token"]
print(f"Login OK — role: {data.get('role')}, permissions: {len(data.get('permissions', []))}")

headers = {"Authorization": f"Bearer {token}"}

# /me
me = requests.get(f"{BASE}/auth/me", headers=headers).json()
print(f"/me: {me['username']} ({me['role']}) — {len(me['permissions'])} permissions")

# Dashboard summary
dash = requests.get(f"{BASE}/dashboard/summary", headers=headers).json()
print(f"Dashboard: {dash}")

# CBC grade levels
grades = requests.get(f"{BASE}/cbc/grade-levels", headers=headers).json()
print(f"CBC Grades: {len(grades)} — {[g['name'] for g in grades]}")

# Score conversion
score = requests.get(f"{BASE}/cbc/score-to-level?score=75", headers=headers).json()
print(f"Score 75 => {score}")
