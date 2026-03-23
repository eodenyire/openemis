# v3 Architecture — Odoo 18.0 Modular ERP

## Overview

v3 is built entirely on the Odoo 18.0 platform. Rather than building a custom framework, v3 leverages Odoo's battle-tested ORM, view engine, security system, and web client. Each openEMIS feature is packaged as an independent Odoo addon module.

---

## Odoo Platform Architecture

```
Browser
    │
    ▼
Odoo Web Client (OWL — Odoo Web Library)
    │
    ├── Views: form, list, kanban, calendar, pivot, graph, activity
    ├── Actions (ir.actions.act_window, ir.actions.server)
    ├── Menus (ir.ui.menu)
    │
    ▼  (JSON-RPC over HTTP)
Odoo Server (Python)
    │
    ├── HTTP Controllers (controllers/*.py)
    │   └── Handles web routes, JSON-RPC, REST endpoints
    ├── ORM Layer
    │   └── models.Model — all business objects
    ├── Security Layer
    │   ├── ir.model.access.csv — CRUD permissions per group
    │   └── ir.rule — record-level row security
    ├── Workflow Engine
    │   └── State machines via selection fields + button actions
    ├── Report Engine
    │   └── QWeb PDF reports
    ├── Mail/Chatter
    │   └── Built-in messaging on every record
    │
    ▼
PostgreSQL (schema managed entirely by Odoo ORM)
```

---

## Module Structure

Every openEMIS module follows the standard Odoo addon layout:

```
openemis_<module>/
├── __manifest__.py          # Module metadata, dependencies, data files list
├── __init__.py              # Python package init
├── models/
│   ├── __init__.py
│   └── *.py                 # ORM model definitions
├── views/
│   └── *.xml                # Form, list, kanban, search views + menus + actions
├── security/
│   ├── ir.model.access.csv  # CRUD permissions per model per group
│   └── security.xml         # Group definitions, record rules
├── data/
│   └── *.xml                # Default/demo data
├── controllers/
│   └── *.py                 # HTTP controllers (REST endpoints, portal pages)
├── static/
│   ├── description/
│   │   └── icon.png         # Module icon (shown in Apps menu)
│   └── src/                 # JS/CSS assets
├── wizard/
│   └── *.py                 # Transient models (dialogs/wizards)
└── report/
    └── *.xml                # QWeb PDF report templates
```

---

## Module Dependency Graph

```
Odoo Base (built-in)
    │
    ▼
openemis_core  ◄── All other openEMIS modules depend on this
    │
    ├── openemis_admission
    ├── openemis_attendance
    ├── openemis_exam
    │       └── openemis_grading
    ├── openemis_fees
    ├── openemis_timetable
    ├── openemis_assignment
    ├── openemis_library
    ├── openemis_hostel
    ├── openemis_transportation
    ├── openemis_lms
    ├── openemis_lesson
    ├── openemis_cbc
    │       └── openemis_digiguide  (depends on cbc + exam)
    ├── openemis_mentorship
    ├── openemis_blog
    ├── openemis_parent
    ├── openemis_alumni
    ├── openemis_scholarship
    ├── openemis_health
    ├── openemis_discipline
    ├── openemis_notice_board
    ├── openemis_event
    ├── openemis_activity
    ├── openemis_cafeteria
    ├── openemis_facility
    ├── openemis_inventory
    ├── openemis_classroom
    └── openemis_achievement

openemis_erp  ← meta-module, depends on ALL above (one-click full install)

theme_web_openemis  ← depends on web (Odoo built-in)
```

---

## Core Data Model

### openemis_core

```
openemis.academic.year
    └── openemis.academic.term
         └── openemis.course
              ├── openemis.subject
              ├── openemis.enrollment (student ↔ course)
              └── openemis.faculty.assignment (faculty ↔ subject)

openemis.student
    ├── openemis.enrollment
    ├── openemis.attendance.record
    ├── openemis.exam.result
    ├── openemis.fee.record
    └── openemis.hostel.allocation

openemis.faculty
    ├── openemis.faculty.assignment
    └── openemis.attendance.record
```

---

## Security Model

### Groups (defined in `security/security.xml`)

```
openemis_core.group_student     → read-only on own records
openemis_core.group_teacher     → read/write on class records
openemis_core.group_admin       → full access
openemis_core.group_parent      → read-only on child's records
openemis_core.group_librarian   → full access to library models
openemis_core.group_accountant  → full access to fees/finance models
```

### Access Rules (`ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_student_admin,student.admin,model_openemis_student,group_admin,1,1,1,1
access_student_teacher,student.teacher,model_openemis_student,group_teacher,1,1,0,0
access_student_student,student.student,model_openemis_student,group_student,1,0,0,0
```

### Record Rules

Students can only see their own records:
```xml
<record model="ir.rule" id="rule_student_own_records">
    <field name="name">Students: own records only</field>
    <field name="model_id" ref="model_openemis_student"/>
    <field name="groups" eval="[(4, ref('group_student'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

---

## OWL Frontend

Odoo 18.0 uses OWL (Odoo Web Library) — a reactive component framework similar to Vue.js. Custom JavaScript components live in `static/src/`:

```javascript
// static/src/components/my_widget.js
import { Component, useState } from "@odoo/owl";

export class MyWidget extends Component {
    static template = "openemis_core.MyWidget";

    setup() {
        this.state = useState({ value: 0 });
    }
}
```

Template in XML:
```xml
<!-- static/src/components/my_widget.xml -->
<templates>
    <t t-name="openemis_core.MyWidget">
        <div class="my-widget">
            <span t-esc="state.value"/>
        </div>
    </t>
</templates>
```

---

## Odoo Configuration Reference

`odoo.conf` key settings:

| Setting | Description |
|---------|-------------|
| `addons_path` | Comma-separated paths to addon directories |
| `db_host/port/user/password/name` | PostgreSQL connection |
| `http_port` | Web server port (default 8069) |
| `workers` | Number of worker processes (0 = single-threaded) |
| `max_cron_threads` | Cron worker threads |
| `list_db` | Set `False` in production to hide DB manager |
| `admin_passwd` | Master password for DB management |
| `log_level` | `debug`, `info`, `warn`, `error` |
| `log_file` | Path to log file |

---

## Deployment Architecture

### Single Server (small institution)

```
Nginx (443) → Odoo (8069) → PostgreSQL (5432)
```

### Multi-Worker (medium institution)

```
Nginx (443)
    ├── /longpolling → Odoo longpolling worker (8072)
    └── /           → Odoo workers (8069) × 4
                          └── PostgreSQL (5432)
```

Workers = `(CPU cores × 2) + 1` is a common starting point.

### High Availability

```
Load Balancer
    ├── Odoo Node 1
    ├── Odoo Node 2
    └── Odoo Node 3
         └── PostgreSQL Primary
              └── PostgreSQL Replica (read-only)
```

Shared filestore must be on NFS or S3-compatible storage when running multiple nodes.
