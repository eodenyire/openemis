# v3 Developer Guide — Odoo 18.0

## Prerequisites

- Python 3.11
- PostgreSQL 15
- Odoo 18.0 source cloned to `C:\odoo18` (Windows) or `/opt/odoo18` (Linux/macOS)
- Virtual environment with Odoo dependencies installed

See [v3 README](README.md) for initial setup instructions.

---

## Development Server

```bash
# Activate Odoo venv
source /opt/odoo18/venv/bin/activate   # Linux/macOS
# C:\odoo18\venv\Scripts\activate      # Windows

# Start Odoo in dev mode (auto-reload assets)
python /opt/odoo18/odoo-bin \
  -c /path/to/odoo.conf \
  --dev=all

# Or with specific database
python /opt/odoo18/odoo-bin \
  -c /path/to/odoo.conf \
  --dev=all \
  --database openemis_odoo
```

Open http://localhost:8069 — login: `admin` / `admin`

`--dev=all` enables:
- Auto-reload Python files on change
- Asset recompilation without restart
- Detailed error pages

---

## Creating a New Module

### 1. Scaffold the module directory

```bash
cd versions/v3
mkdir openemis_mymodule
cd openemis_mymodule
```

### 2. Create `__manifest__.py`

```python
{
    'name': 'openEMIS My Module',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Short description of what this module does',
    'description': 'Longer description...',
    'author': 'openEMIS Team',
    'website': 'https://www.openemis.org',
    'license': 'LGPL-3',
    'depends': ['openemis_core'],   # always depend on core at minimum
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/my_model_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### 3. Create `__init__.py`

```python
from . import models
from . import controllers  # if you have controllers
```

### 4. Create the model

`models/__init__.py`:
```python
from . import my_model
```

`models/my_model.py`:
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'openemis.my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # adds chatter

    name = fields.Char(string='Name', required=True, tracking=True)
    student_id = fields.Many2one(
        'openemis.student',
        string='Student',
        required=True,
        ondelete='cascade'
    )
    date = fields.Date(string='Date', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('student_id')
    def _compute_something(self):
        for record in self:
            record.something = record.student_id.name if record.student_id else ''

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'
```

### 5. Create security files

`security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_admin,my.model.admin,model_openemis_my_model,openemis_core.group_admin,1,1,1,1
access_my_model_teacher,my.model.teacher,model_openemis_my_model,openemis_core.group_teacher,1,1,1,0
access_my_model_student,my.model.student,model_openemis_my_model,openemis_core.group_student,1,0,0,0
```

### 6. Create views

`views/my_model_views.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">openemis.my.model.form</field>
        <field name="model">openemis.my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <statusbar statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="student_id"/>
                        <field name="date"/>
                    </group>
                    <field name="notes"/>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <!-- List View -->
    <record id="view_my_model_list" model="ir.ui.view">
        <field name="name">openemis.my.model.list</field>
        <field name="model">openemis.my.model</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="student_id"/>
                <field name="date"/>
                <field name="state"/>
            </list>
        </field>
    </record>

    <!-- Action -->
    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Models</field>
        <field name="res_model">openemis.my.model</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

`views/menu.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="menu_my_module_root"
              name="My Module"
              parent="openemis_core.menu_openemis_root"
              sequence="50"/>

    <menuitem id="menu_my_model"
              name="My Models"
              parent="menu_my_module_root"
              action="action_my_model"
              sequence="10"/>
</odoo>
```

### 7. Install the module

```bash
python /opt/odoo18/odoo-bin -c odoo.conf -i openemis_mymodule --stop-after-init
```

Or from the Odoo UI: Settings → Apps → search for "openEMIS My Module" → Install.

---

## Extending an Existing Module

To add fields or methods to an existing model without modifying its source:

```python
from odoo import models, fields

class StudentExtension(models.Model):
    _inherit = 'openemis.student'   # extend the existing model

    my_new_field = fields.Char(string='My New Field')
    my_computed = fields.Float(string='Computed', compute='_compute_my_computed')

    def _compute_my_computed(self):
        for record in self:
            record.my_computed = 42.0  # your logic here
```

To extend a view:
```xml
<record id="view_student_form_inherit" model="ir.ui.view">
    <field name="name">openemis.student.form.inherit.mymodule</field>
    <field name="model">openemis.student</field>
    <field name="inherit_id" ref="openemis_core.view_student_form"/>
    <field name="arch" type="xml">
        <field name="name" position="after">
            <field name="my_new_field"/>
        </field>
    </field>
</record>
```

---

## Running Tests

```bash
# Test a single module
bash scripts/run_module_tests.sh openemis_core

# Test all modules
bash scripts/run_module_tests.sh ALL

# Or directly with Odoo test runner
python /opt/odoo18/odoo-bin \
  -c odoo.conf \
  --test-enable \
  --stop-after-init \
  -i openemis_mymodule
```

Write tests in `tests/test_my_model.py`:
```python
from odoo.tests.common import TransactionCase

class TestMyModel(TransactionCase):

    def setUp(self):
        super().setUp()
        self.student = self.env['openemis.student'].create({'name': 'Test Student'})

    def test_create_my_model(self):
        record = self.env['openemis.my.model'].create({
            'name': 'Test',
            'student_id': self.student.id,
        })
        self.assertEqual(record.state, 'draft')

    def test_confirm(self):
        record = self.env['openemis.my.model'].create({
            'name': 'Test',
            'student_id': self.student.id,
        })
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

---

## Generating Demo Data

```bash
python scripts/generate_demo_data.py
```

This creates 100 classrooms, 100 staff, 100 parents, and 100 students per class.

---

## Updating the Module After Code Changes

After changing Python models:
```bash
python /opt/odoo18/odoo-bin -c odoo.conf -u openemis_mymodule --stop-after-init
```

After changing only views/data (no model changes), use `--dev=all` mode — changes are picked up automatically.

---

## Useful Odoo Shell Commands

```bash
# Open Odoo shell (Python REPL with ORM access)
python /opt/odoo18/odoo-bin shell -c odoo.conf --database openemis_odoo

# In the shell:
# Count students
env['openemis.student'].search_count([])

# Find a student
student = env['openemis.student'].search([('name', 'like', 'John')], limit=1)
print(student.name, student.id)

# Create a record
env['openemis.my.model'].create({'name': 'Test', 'student_id': student.id})
env.cr.commit()  # commit the transaction
```

---

## Odoo Coding Guidelines Summary

- Model names: `openemis.module.entity` (dots, lowercase)
- XML IDs: `module_name.record_type_description`
- Field names: `snake_case`
- Method names: `snake_case`, prefix computed fields with `_compute_`, onchange with `_onchange_`
- Every model needs `_name` and `_description`
- Every new model needs an entry in `security/ir.model.access.csv`
- Use `tracking=True` on important fields to log changes in chatter
- Use `@api.depends()` for computed fields, `@api.onchange()` for UI reactivity

Full guidelines: https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html
