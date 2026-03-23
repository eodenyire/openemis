# scripts — Utility Scripts (v1)

A collection of shell scripts, Python scripts, and SQL files for database seeding, testing, deployment, and system verification.

## Scripts

### Database Seeding

| Script | Purpose |
|--------|---------|
| `seed_phase1.py` | Phase 1 seed — users, roles, departments |
| `seed_phase2.py` | Phase 2 seed — students and faculty |
| `seed_phase3.py` | Phase 3 seed — courses, subjects, batches |
| `seed_phase4.py` | Phase 4 seed — admissions and enrollment |
| `seed_phase5.py` | Phase 5 seed — attendance and exams |
| `seed_phase6.py` | Phase 6 seed — fees, library, hostel |
| `seed_kenya.py` | Kenya-specific seed data (counties, schools) |
| `seed_postgres.sql` | Raw SQL seed for PostgreSQL |
| `generate_demo_data.py` | Generates bulk demo data (100 students, staff, parents) |
| `query_database.sql` | Useful diagnostic SQL queries |

### Testing & Verification

| Script | Purpose |
|--------|---------|
| `api_test.sh` | End-to-end API tests against a running instance |
| `snapshot_test.sh` | Captures JSON snapshots from all API endpoints for regression testing |
| `run_module_tests.sh` | Runs tests for a single module or all modules |
| `k8s_test.sh` | Kubernetes smoke tests |
| `test_phase1.py` | Validates phase 1 seed data |
| `verify_phase4.py` | Validates phase 4 seed data |
| `verify_phase6.py` | Validates phase 6 seed data |
| `verify_system.sh` | Full system verification (PostgreSQL + API health) |
| `diagnose.py` | Diagnostic checks for common setup issues |
| `check_passwords.py` | Verifies user password hashes |
| `check_users.py` | Lists and validates user accounts |

### Setup & Deployment

| Script | Purpose |
|--------|---------|
| `setup.sh` | Full Linux/macOS setup (venv, deps, DB, migrations) |
| `install_windows.ps1` | Windows PowerShell setup script |
| `migrate_userrole_enum.py` | Database migration for user role enum changes |

## Usage

```bash
# Seed the database in phases
python scripts/seed_phase1.py
python scripts/seed_phase2.py
# ... through phase 6

# Or generate bulk demo data
python scripts/generate_demo_data.py

# Run API tests against a live instance
bash scripts/api_test.sh localhost 8000

# Verify the system
bash scripts/verify_system.sh
```
