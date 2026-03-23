# openEMIS — Open Source Educational Management Information System

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-eodenyire%2Fopenemis-blue)](https://github.com/eodenyire/openemis)

## Overview

openEMIS is an open-source Educational Management Information System designed to streamline academic and administrative processes in educational institutions. This repository contains the full evolution of the system across four major versions — from a lightweight REST API to a full Odoo ERP implementation.

---

## Versions

| Version | Stack | Description |
|---------|-------|-------------|
| [v1](versions/v1/README.md) | FastAPI + PostgreSQL | Standalone Python REST API — lightweight, no Odoo dependency |
| [v2](versions/v2/README.md) | FastAPI + Next.js 14 | Full-stack — FastAPI backend + modern React/TypeScript frontend |
| [v3](versions/v3/README.md) | Odoo 18.0 | Enterprise modular ERP — 35+ Odoo addon modules |
| [v4](versions/v4/README.md) | Django 4.2 | Traditional Django web app — multi-role school management system |

---

## Version Summaries

### v1 — Standalone FastAPI Backend
The first Python implementation. A clean, fast REST API with 25+ endpoints covering students, teachers, courses, admissions, exams, fees, library, HR, and analytics. Includes JWT auth, Alembic migrations, Docker, Kubernetes, and a Flutter mobile companion app.

→ [Read more](versions/v1/README.md)

### v2 — FastAPI + Next.js Frontend
Builds on v1 with a decoupled Next.js 14 frontend. The backend models were re-engineered from the openeducat Odoo modules. The frontend uses TypeScript, Tailwind CSS, Radix UI, Zustand, and React Query for a modern, production-ready interface.

→ [Read more](versions/v2/README.md)

### v3 — Odoo 18.0 Modular ERP
The enterprise implementation. A full suite of Odoo 18.0 addon modules providing comprehensive educational management. Includes CBC (Competency-Based Curriculum) support, DigiGuide career guidance with KUCCPS integration, a mentorship platform, educational blog, and 35+ independently installable modules.

→ [Read more](versions/v3/README.md)

### v4 — Django School Management System
A Django 4.2 web application converted from the original PHP CodeIgniter codebase. Multi-role system (Admin, Teacher, Student, Parent, Librarian, Accountant) with traditional Django architecture, DRF API layer, Celery task queue, and Bootstrap 5 frontend.

→ [Read more](versions/v4/README.md)

---

## Repository Structure

```
openEMIS/
├── versions/
│   ├── v1/         # FastAPI standalone backend
│   ├── v2/         # FastAPI + Next.js full-stack
│   ├── v3/         # Odoo 18.0 modular ERP
│   └── v4/         # Django school management system
└── README.md
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System-wide architecture — all 4 versions, data flow, design decisions |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide — native, Docker, Kubernetes, Heroku |
| [API_REFERENCE.md](API_REFERENCE.md) | Full REST API reference for v1 and v2 |
| [SECURITY.md](SECURITY.md) | Security practices, JWT config, secrets management |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute — branching, code standards, PR process |
| [CHANGELOG.md](CHANGELOG.md) | Version history — what changed between v1 → v2 → v3 → v4 |

### Per-Version Documentation

| Version | Architecture | Developer Guide | Extra |
|---------|-------------|-----------------|-------|
| v1 | [ARCHITECTURE.md](versions/v1/ARCHITECTURE.md) | [DEVELOPER_GUIDE.md](versions/v1/DEVELOPER_GUIDE.md) | — |
| v2 | [ARCHITECTURE.md](versions/v2/ARCHITECTURE.md) | [DEVELOPER_GUIDE.md](versions/v2/DEVELOPER_GUIDE.md) | — |
| v3 | [ARCHITECTURE.md](versions/v3/ARCHITECTURE.md) | [DEVELOPER_GUIDE.md](versions/v3/DEVELOPER_GUIDE.md) | [MODULE_DEPENDENCY_MAP.md](versions/v3/MODULE_DEPENDENCY_MAP.md) |
| v4 | [ARCHITECTURE.md](versions/v4/ARCHITECTURE.md) | [DEVELOPER_GUIDE.md](versions/v4/DEVELOPER_GUIDE.md) | — |

---

## License

LGPL-3.0 — see [LICENSE](LICENSE).

## Contact

- Website: https://www.openemis.org
- Email: support@openemis.org
- GitHub: https://github.com/eodenyire/openemis
