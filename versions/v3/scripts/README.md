# scripts — Utility Scripts (v3)

Scripts for data generation, testing, deployment, and system verification for the openEMIS v3 Odoo system.

## Scripts

### Data Generation
| Script | Purpose |
|--------|---------|
| `generate_demo_data.py` | Generates bulk demo data — 100 classrooms, 100 staff, 100 parents, 100 students per class. Outputs XML files into each module's `demo/` directory. |
| `seed_kenya.py` | Kenya-specific seed data (counties, sub-counties, schools) |
| `seed_phase1.py` – `seed_phase6.py` | Phased data seeding scripts |
| `seed_postgres.sql` | Raw SQL seed for PostgreSQL |
| `query_database.sql` | Diagnostic SQL queries |

### Testing
| Script | Purpose |
|--------|---------|
| `run_module_tests.sh` | Run Odoo unit tests for a single module or all modules |
| `api_test.sh` | End-to-end API tests against a running Odoo instance |
| `snapshot_test.sh` | Captures JSON snapshots from all module endpoints for regression testing |
| `k8s_test.sh` | Kubernetes smoke tests |
| `test_phase1.py` | Validates phase 1 seed data |
| `verify_phase4.py` | Validates phase 4 data |
| `verify_phase6.py` | Validates phase 6 data |
| `verify_system.sh` | Full system verification |
| `diagnose.py` | Diagnostic checks |

### Setup & Deployment
| Script | Purpose |
|--------|---------|
| `setup.sh` | Linux/macOS setup script |
| `install_windows.ps1` | Windows PowerShell setup |
| `migrate_userrole_enum.py` | DB migration helper |

## Usage

```bash
# Generate demo data
python scripts/generate_demo_data.py

# Test all modules
bash scripts/run_module_tests.sh ALL

# API tests against running Odoo
bash scripts/api_test.sh localhost 8069 odoo admin admin

# Snapshot tests
bash scripts/snapshot_test.sh localhost 8069 odoo admin admin
```
