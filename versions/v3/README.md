# openEMIS v3 — Odoo 18.0 Modular ERP

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](LICENSE)

## Overview

v3 is the enterprise-grade implementation of openEMIS, built as a full suite of **Odoo 18.0 addon modules**. It provides a comprehensive, modular Educational Management Information System that leverages the Odoo ERP platform — giving institutions access to a battle-tested framework with built-in accounting, HR, CRM, and a rich web interface out of the box.

Each module is independently installable. Start with `openemis_core` and add what you need.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Platform | Odoo 18.0 |
| Language | Python 3.11 |
| Database | PostgreSQL 15 |
| Templates | QWeb (XML) |
| Frontend | Odoo Web Client (OWL framework) |
| Styling | SCSS |
| Deployment | Docker, Kubernetes, Heroku |

## Module Overview

| Module | Description |
|--------|-------------|
| `openemis_core` | Foundation — students, courses, subjects, faculties, academic years & terms |
| `openemis_admission` | Admissions & enrolment workflow |
| `openemis_activity` | Extra-curricular activities |
| `openemis_alumni` | Alumni management |
| `openemis_assignment` | Assignment creation, submission & grading |
| `openemis_attendance` | Student & faculty attendance tracking |
| `openemis_blog` | Educational blog for mentors, teachers & professionals |
| `openemis_cafeteria` | Cafeteria management |
| `openemis_cbc` | Competency-Based Curriculum (CBC) support |
| `openemis_classroom` | Classroom management |
| `openemis_digiguide` | Digital Career Guidance — CBC performance tracking, national exam prediction & KUCCPS integration |
| `openemis_discipline` | Student discipline management |
| `openemis_erp` | Meta-module bundling all core modules |
| `openemis_event` | Events management |
| `openemis_exam` | Examination scheduling, mark sheets & grade configuration |
| `openemis_facility` | School facilities management |
| `openemis_fees` | Fee structure, invoicing and payment tracking |
| `openemis_grading` | Grading system configuration |
| `openemis_health` | Student health records |
| `openemis_hostel` | Hostel accommodation management |
| `openemis_inventory` | Inventory management |
| `openemis_lesson` | Lesson planning |
| `openemis_library` | Library management with CBC grade-level, subject, topic & format categorisation |
| `openemis_lms` | Learning Management System |
| `openemis_mentorship` | Mentorship platform — mentor registration, DMs, group forums |
| `openemis_notice_board` | Notice board & announcements |
| `openemis_parent` | Parent portal and parent–student linking |
| `openemis_scholarship` | Scholarship management |
| `openemis_timetable` | Class timetable generation and management |
| `openemis_transportation` | Transport logistics management |
| `theme_web_openemis` | Custom UI theme |

## Quick Start (Native — no Docker)

### Prerequisites
- Python 3.11
- PostgreSQL 15
- Odoo 18.0 source (cloned to `C:\odoo18` or `/opt/odoo18`)

### 1. Clone Odoo source

```bash
git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git /opt/odoo18
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv /opt/odoo18/venv
source /opt/odoo18/venv/bin/activate   # Linux/macOS
# /opt/odoo18/venv/Scripts/activate    # Windows

pip install setuptools wheel
pip install -r /opt/odoo18/requirements.txt
```

### 3. Set up PostgreSQL

```sql
CREATE USER odoo WITH SUPERUSER PASSWORD 'odoo';
CREATE DATABASE odoo OWNER odoo;
```

### 4. Create Odoo config

```ini
[options]
addons_path = /opt/odoo18/addons,/path/to/versions/v3
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo
http_port = 8069
log_level = info
```

### 5. Initialize database and install modules

```bash
# Initialize base
python /opt/odoo18/odoo-bin -c odoo.conf -i base --stop-after-init

# Install all openEMIS modules
python /opt/odoo18/odoo-bin -c odoo.conf -i openemis_core --stop-after-init

# Start Odoo
python /opt/odoo18/odoo-bin -c odoo.conf
```

Open http://localhost:8069 — login with `admin` / `admin`.

## Docker Quick Start

```bash
docker compose up -d
```

Starts PostgreSQL + Odoo 18.0 together. Open http://localhost:8069.

## Kubernetes

```bash
docker build -t openemis:latest .
kind load docker-image openemis:latest --name openemis-local
kubectl apply -k kubernetes/
kubectl -n openemis rollout status deployment/openemis --timeout=300s
```

## Demo Data

Generate realistic test data (100 classrooms, 100 staff, 100 parents, 100 students per class):

```bash
python scripts/generate_demo_data.py
```

## Testing

```bash
# Test a single module
bash scripts/run_module_tests.sh openemis_core

# Test all modules
bash scripts/run_module_tests.sh ALL

# API end-to-end tests (requires running Odoo)
bash scripts/api_test.sh localhost 8069 odoo admin admin

# Snapshot/regression tests
bash scripts/snapshot_test.sh localhost 8069 odoo admin admin
```

## CI/CD

GitHub Actions workflows included:

| Workflow | Trigger |
|----------|---------|
| CI — Lint & Unit Tests | Every push / PR |
| Module Tests (parallel matrix) | Every push / PR |
| Docker Build & Integration | Push to main/develop |
| Kubernetes Smoke Tests | Push to main (k8s changes) |
| Deploy — Heroku | Version tags `v*.*.*` |

## License

LGPL-3.0 — see [LICENSE](LICENSE).

## Contact

- Website: https://www.openemis.org
- Email: support@openemis.org
- GitHub: https://github.com/eodenyire/openEMIS
