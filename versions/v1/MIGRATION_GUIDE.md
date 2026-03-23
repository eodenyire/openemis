# Migration Guide

## v1 → v2

v2 will introduce the openeducat Odoo modules alongside the existing FastAPI backend.

### What changes in v2
- Odoo 18.0 + openeducat modules added as an optional layer
- Existing FastAPI API remains fully functional
- New Odoo-based workflows for institutions that prefer the ERP approach
- Shared PostgreSQL database (separate schemas)

### Preparing for v2
- Ensure your v1 data is backed up: `pg_dump openemis_db > openemis_v1_backup.sql`
- Document any custom models or endpoints you've added
- Review the v2 release notes when available

---

## Odoo → openEMIS v1 (legacy migration)

If you were previously running the Odoo-based version of openEMIS and want to migrate data to the standalone FastAPI v1:

### Export from Odoo

```python
# In an Odoo shell
students = env['op.student'].search([])
data = [{
    'admission_number': s.gr_no,
    'first_name': s.first_name,
    'last_name': s.last_name,
    'email': s.email,
} for s in students]

import json
with open('/tmp/students.json', 'w') as f:
    json.dump(data, f)
```

### Import to openEMIS v1

```python
import json
from app.db.session import SessionLocal
from app.models.student import Student

db = SessionLocal()
with open('students.json') as f:
    for item in json.load(f):
        db.add(Student(**item))
db.commit()
```

Repeat for other entities (teachers, courses, etc.) following the same pattern.
