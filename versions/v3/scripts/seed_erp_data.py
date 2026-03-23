#!/usr/bin/env python3
"""
openEMIS – ERP & Financial Demo Data Seeder
============================================
Seeds the openEMIS/Odoo database with ERP and financial demonstration data
including:

  - HR employees (linked to faculty records)
  - HR payslip batches and individual payslips
  - Supplier / vendor partners for LPO creation
  - Purchase orders (LPOs – Local Purchase Orders)
  - Customer invoices for student fees
  - Payment vouchers (account.payment records)
  - Additional discipline records with realistic content
  - Additional progressive assessment result data

This script uses the Odoo JSON-RPC API, so it works against any running
openEMIS/Odoo instance without requiring direct database access.

Usage::

    # Default (localhost:8069, openemis DB, admin/admin)
    python scripts/seed_erp_data.py

    # Custom target
    python scripts/seed_erp_data.py \\
        --url http://localhost:8069 \\
        --db openemis \\
        --user admin \\
        --password admin

Prerequisites:
  - requests>=2.28  (pip install requests)
  - A running openEMIS / Odoo instance with the relevant modules installed
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package is not installed. Run: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="openEMIS ERP demo data seeder")
    p.add_argument("--url", default=os.environ.get("ODOO_URL", "http://localhost:8069"))
    p.add_argument("--db", default=os.environ.get("ODOO_DB", "openemis"))
    p.add_argument("--user", default=os.environ.get("ODOO_USER", "admin"))
    p.add_argument("--password", default=os.environ.get("ODOO_PASSWORD", "admin"))
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be created without actually creating records")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Odoo JSON-RPC client
# ---------------------------------------------------------------------------

class OdooRPC:
    """Minimal Odoo JSON-RPC client."""

    def __init__(self, url: str, db: str):
        self.base = url.rstrip("/")
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.uid = None

    # ---- low-level helpers --------------------------------------------------

    def _call(self, endpoint: str, method: str, *args, **kwargs):
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": method,
                **kwargs,
            },
        }
        # /web/dataset/call_kw style
        if endpoint == "/web/dataset/call_kw":
            payload["params"] = kwargs
        resp = self.session.post(f"{self.base}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(f"RPC error: {data['error']}")
        return data.get("result")

    def _jsonrpc(self, endpoint: str, payload: dict):
        resp = self.session.post(f"{self.base}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            err = data["error"]
            raise RuntimeError(f"RPC error at {endpoint}: {err.get('data', {}).get('message', err)}")
        return data.get("result")

    # ---- public API ---------------------------------------------------------

    def authenticate(self, user: str, password: str) -> int:
        result = self._jsonrpc("/web/session/authenticate", {
            "jsonrpc": "2.0", "method": "call",
            "params": {"db": self.db, "login": user, "password": password},
        })
        uid = result.get("uid") if result else None
        if not uid:
            raise RuntimeError(f"Authentication failed for user '{user}'")
        self.uid = uid
        return uid

    def call_kw(self, model: str, method: str, args=None, kwargs=None):
        return self._jsonrpc("/web/dataset/call_kw", {
            "jsonrpc": "2.0", "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {},
            },
        })

    def search(self, model: str, domain=None, limit: int = 100, order: str = "id"):
        return self.call_kw(model, "search",
                            args=[domain or []],
                            kwargs={"limit": limit, "order": order}) or []

    def search_read(self, model: str, domain=None, fields=None, limit: int = 50):
        return self.call_kw(model, "search_read",
                            args=[domain or []],
                            kwargs={"fields": fields or [], "limit": limit}) or []

    def create(self, model: str, vals: dict):
        return self.call_kw(model, "create", args=[vals])

    def write(self, model: str, ids: list, vals: dict):
        return self.call_kw(model, "write", args=[ids, vals])

    def read(self, model: str, ids: list, fields=None):
        return self.call_kw(model, "read", args=[ids],
                            kwargs={"fields": fields or []}) or []

    def search_count(self, model: str, domain=None) -> int:
        return self.call_kw(model, "search_count", args=[domain or []]) or 0

    def model_exists(self, model: str) -> bool:
        return self.search_count("ir.model", [["model", "=", model]]) > 0

    def get_ref(self, xmlid: str):
        """Resolve an XMLID to a record id, or return None."""
        try:
            result = self.call_kw("ir.model.data", "xmlid_to_res_id",
                                  args=[xmlid], kwargs={})
            return result or None
        except Exception:  # pylint: disable=broad-except
            return None


# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------



def log(msg: str):
    print(f"  {msg}")


def header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def skip(msg: str):
    print(f"  ⚠ SKIP  {msg}")


def today_str(offset_days: int = 0) -> str:
    return (date.today() + timedelta(days=offset_days)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# 1. Seed HR Employees (link to faculty)
# ---------------------------------------------------------------------------

def seed_hr_employees(odoo: OdooRPC, dry_run: bool):
    header("1. HR Employees (linked to Faculty)")
    if not odoo.model_exists("hr.employee"):
        skip("hr.employee model not installed")
        return []

    # Get faculty who don't yet have an employee record
    faculty_list = odoo.search_read("op.faculty",
                                    [["active", "=", True]],
                                    fields=["id", "first_name", "last_name", "partner_id"],
                                    limit=20)
    existing_partners = set()
    for emp in odoo.search_read("hr.employee", fields=["address_home_id"], limit=200):
        if emp.get("address_home_id"):
            existing_partners.add(emp["address_home_id"][0])

    dept_id = None
    if odoo.model_exists("hr.department"):
        depts = odoo.search("hr.department", [], limit=1)
        dept_id = depts[0] if depts else None

    created = []
    for fac in faculty_list:
        name = f"{fac['first_name']} {fac['last_name']}"
        partner_id = fac["partner_id"][0] if fac.get("partner_id") else None
        if partner_id and partner_id in existing_partners:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create HR employee: {name}")
            continue

        try:
            vals = {"name": name}
            if partner_id:
                vals["address_home_id"] = partner_id
            if dept_id:
                vals["department_id"] = dept_id
            emp_id = odoo.create("hr.employee", vals)
            created.append(emp_id)
            log(f"✓ HR employee created: {name} (id={emp_id})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Could not create employee {name}: {exc}")

    if not created and not dry_run:
        log("  (All faculty already have employee records or no faculty found)")
    return created


# ---------------------------------------------------------------------------
# 2. Seed Payslips
# ---------------------------------------------------------------------------

def seed_payslips(odoo: OdooRPC, dry_run: bool):
    header("2. Payslips")
    if not odoo.model_exists("hr.payslip"):
        skip("hr.payslip model not installed (install 'payroll' module to enable)")
        return

    employees = odoo.search_read("hr.employee",
                                 [["active", "=", True]],
                                 fields=["id", "name"],
                                 limit=10)
    if not employees:
        skip("No employees found for payslip generation")
        return

    # Find or detect a salary structure
    struct_id = None
    if odoo.model_exists("hr.payroll.structure"):
        structs = odoo.search("hr.payroll.structure", [], limit=1)
        struct_id = structs[0] if structs else None

    created_count = 0
    for emp in employees:
        # Check if a payslip already exists for this employee this month
        month_start = today_str(-date.today().day + 1)
        existing = odoo.search_count("hr.payslip",
                                     [["employee_id", "=", emp["id"]],
                                      ["date_from", ">=", month_start]])
        if existing:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create payslip for {emp['name']}")
            continue

        try:
            vals = {
                "name": f"Payslip – {emp['name']} – {date.today().strftime('%B %Y')}",
                "employee_id": emp["id"],
                "date_from": today_str(-date.today().day + 1),
                "date_to": today_str(0),
            }
            if struct_id:
                vals["struct_id"] = struct_id
            slip_id = odoo.create("hr.payslip", vals)
            # Compute the payslip
            try:
                odoo.call_kw("hr.payslip", "compute_sheet", args=[[slip_id]])
            except Exception:  # pylint: disable=broad-except
                pass
            created_count += 1
            log(f"✓ Payslip created for {emp['name']} (id={slip_id})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Payslip for {emp['name']} failed: {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new payslips needed or payslip creation not supported)")


# ---------------------------------------------------------------------------
# 3. Seed Purchase Orders (LPOs)
# ---------------------------------------------------------------------------

def seed_purchase_orders(odoo: OdooRPC, dry_run: bool):
    header("3. Purchase Orders (LPOs)")
    if not odoo.model_exists("purchase.order"):
        skip("purchase.order model not installed (install 'purchase' module to enable)")
        return

    # Ensure we have vendor partners
    vendor_data = [
        {"name": "ABC School Supplies Ltd",       "supplier_rank": 1},
        {"name": "Global Educational Resources",  "supplier_rank": 1},
        {"name": "TechEdge Computing",            "supplier_rank": 1},
        {"name": "Premier Library Distributors",  "supplier_rank": 1},
        {"name": "Sports & Recreation Wholesale", "supplier_rank": 1},
    ]
    vendor_ids = []
    for vdata in vendor_data:
        existing = odoo.search("res.partner",
                               [["name", "=", vdata["name"]], ["supplier_rank", ">", 0]],
                               limit=1)
        if existing:
            vendor_ids.append(existing[0])
        else:
            if not dry_run:
                try:
                    vid = odoo.create("res.partner", vdata)
                    vendor_ids.append(vid)
                    log(f"✓ Vendor created: {vdata['name']} (id={vid})")
                except Exception as exc:  # pylint: disable=broad-except
                    log(f"  ✗ Vendor creation failed: {exc}")
            else:
                log(f"[DRY-RUN] Would create vendor: {vdata['name']}")

    if not vendor_ids and not dry_run:
        skip("No vendors available – skipping LPO creation")
        return

    # Find a product or use a generic service product
    product_id = None
    if odoo.model_exists("product.product"):
        prods = odoo.search("product.product",
                            [["purchase_ok", "=", True], ["type", "in", ["consu", "service"]]],
                            limit=1)
        product_id = prods[0] if prods else None

    # Find UoM
    uom_id = None
    if odoo.model_exists("uom.uom"):
        uoms = odoo.search("uom.uom", [["name", "in", ["Units", "Unit", "pcs", "piece"]]], limit=1)
        if not uoms:
            uoms = odoo.search("uom.uom", [], limit=1)
        uom_id = uoms[0] if uoms else None

    lpo_descriptions = [
        ("LPO-2024-001 – Science Lab Equipment",
         "Science Lab Supplies",   50,   120.00),
        ("LPO-2024-002 – Library Books Q3",
         "Library Reference Books", 200,   45.00),
        ("LPO-2024-003 – Computer Lab Consumables",
         "Computer Accessories",   30,   200.00),
        ("LPO-2024-004 – Sports Equipment",
         "Sports Kit",             20,   350.00),
        ("LPO-2024-005 – Office Stationery",
         "Stationery Supplies",   500,    8.50),
    ]

    created_count = 0
    for i, (po_name, line_desc, qty, unit_price) in enumerate(lpo_descriptions):
        vendor_id = vendor_ids[i % len(vendor_ids)] if vendor_ids else None
        if vendor_id is None:
            continue

        existing = odoo.search("purchase.order", [["name", "=", po_name]], limit=1)
        if existing:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create LPO: {po_name}")
            continue

        try:
            order_line: list[dict] = []
            line_vals: dict = {
                "name": line_desc,
                "product_qty": qty,
                "price_unit": unit_price,
                "date_planned": today_str(14),
            }
            if product_id:
                line_vals["product_id"] = product_id
            if uom_id:
                line_vals["product_uom"] = uom_id

            po_id = odoo.create("purchase.order", {
                "partner_id": vendor_id,
                "date_order": today_str(),
                "notes": f"openEMIS demo purchase order – {po_name}",
                "order_line": [(0, 0, line_vals)],
            })
            created_count += 1
            log(f"✓ LPO created: {po_name} (id={po_id})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ LPO creation failed ({po_name}): {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new LPOs created – they may already exist)")


# ---------------------------------------------------------------------------
# 4. Seed Payment Vouchers (account.payment)
# ---------------------------------------------------------------------------

def seed_payment_vouchers(odoo: OdooRPC, dry_run: bool):
    header("4. Payment Vouchers (account.payment)")
    if not odoo.model_exists("account.payment"):
        skip("account.payment model not installed")
        return

    # Find a currency
    currency_id = None
    currencies = odoo.search("res.currency", [["active", "=", True], ["name", "=", "USD"]], limit=1)
    if currencies:
        currency_id = currencies[0]

    # Find a payment method / journal
    journal_id = None
    journals = odoo.search("account.journal",
                           [["type", "in", ["bank", "cash"]]],
                           limit=1)
    if journals:
        journal_id = journals[0]

    if not journal_id:
        skip("No bank/cash journal found – skipping payment vouchers")
        return

    # Find student partners to link payments to
    student_partners = odoo.search_read(
        "op.student",
        [["active", "=", True]],
        fields=["id", "partner_id", "first_name", "last_name"],
        limit=10,
    )

    voucher_amounts = [500.00, 350.00, 750.00, 1200.00, 200.00,
                       450.00, 600.00, 900.00, 1500.00, 250.00]

    created_count = 0
    for idx, stu in enumerate(student_partners):
        partner_id = stu["partner_id"][0] if stu.get("partner_id") else None
        if not partner_id:
            continue

        amount = voucher_amounts[idx % len(voucher_amounts)]
        ref = f"FEE-PAY-{stu['id']:04d}-{today_str().replace('-', '')}"

        # Check if already exists
        existing = odoo.search("account.payment",
                               [["ref", "=", ref]], limit=1)
        if existing:
            continue

        if dry_run:
            name = f"{stu.get('first_name', '')} {stu.get('last_name', '')}".strip()
            log(f"[DRY-RUN] Would create payment voucher for {name}: {amount}")
            continue

        try:
            vals: dict = {
                "partner_id": partner_id,
                "amount": amount,
                "payment_type": "inbound",
                "partner_type": "customer",
                "journal_id": journal_id,
                "date": today_str(-(idx * 3)),
                "ref": ref,
                "memo": f"School fees payment – {stu.get('first_name', '')} {stu.get('last_name', '')}",
            }
            if currency_id:
                vals["currency_id"] = currency_id
            pay_id = odoo.create("account.payment", vals)
            created_count += 1
            log(f"✓ Payment voucher created (id={pay_id}, amount={amount}, ref={ref})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Payment voucher failed: {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new payment vouchers created – they may already exist)")


# ---------------------------------------------------------------------------
# 5. Seed additional Discipline Records
# ---------------------------------------------------------------------------

def seed_discipline_records(odoo: OdooRPC, dry_run: bool):
    header("5. Additional Discipline Records")
    if not odoo.model_exists("op.discipline"):
        skip("op.discipline model not installed")
        return

    students = odoo.search("op.student", [["active", "=", True]], limit=20)
    faculty_list = odoo.search("op.faculty", [["active", "=", True]], limit=10)
    categories = odoo.search("op.misbehaviour.category", [], limit=10)
    actions = odoo.search("op.discipline.action", [], limit=10)

    if not students or not categories or not actions:
        skip("Missing students/categories/actions for discipline seeding")
        return

    descriptions = [
        "Student repeatedly failed to submit homework on time.",
        "Student was found using a mobile phone during an examination.",
        "Student was caught fighting with a classmate in the corridor.",
        "Student used inappropriate language towards a teacher.",
        "Student was absent without explanation for three consecutive days.",
        "Student was found vandalising school property.",
        "Student arrived 30 minutes late to class without a valid reason.",
        "Student was caught cheating during a mid-term assessment.",
        "Student disrupted the class by playing loud music.",
        "Student failed to follow dress code regulations repeatedly.",
    ]
    states = ["reported", "under_review", "resolved", "reported", "under_review"]

    created_count = 0
    for i, desc in enumerate(descriptions):
        stu_id = students[i % len(students)]
        cat_id = categories[i % len(categories)]
        act_id = actions[i % len(actions)]
        fac_id = faculty_list[i % len(faculty_list)] if faculty_list else None
        state = states[i % len(states)]
        record_date = today_str(-(i * 7))

        # Check duplicates roughly (same student+date)
        existing = odoo.search_count("op.discipline",
                                     [["student_id", "=", stu_id],
                                      ["date", "=", record_date]])
        if existing:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create discipline record for student_id={stu_id}")
            continue

        try:
            vals: dict = {
                "student_id": stu_id,
                "misbehaviour_category_id": cat_id,
                "discipline_action_id": act_id,
                "date": record_date,
                "description": desc,
                "state": state,
            }
            if fac_id:
                vals["faculty_id"] = fac_id
            disc_id = odoo.create("op.discipline", vals)
            created_count += 1
            log(f"✓ Discipline record created (id={disc_id}, state={state})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Discipline record failed: {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new discipline records created – they may already exist)")


# ---------------------------------------------------------------------------
# 6. Seed Progressive / Continuous Assessment Data
# ---------------------------------------------------------------------------

def seed_progressive_assessments(odoo: OdooRPC, dry_run: bool):
    header("6. Progressive / Continuous Assessment Data")
    if not odoo.model_exists("op.result.line"):
        skip("op.result.line model not installed")
        return

    # Check if we already have rich result data
    existing_count = odoo.search_count("op.result.line")
    if existing_count >= 30:
        log(f"  (Already {existing_count} result lines present – skipping extra seeding)")
        return

    # We need marksheet_line_ids and exam_ids to create result lines
    marksheet_lines = odoo.search("op.marksheet.line", [], limit=20)
    exams = odoo.search("op.exam", [], limit=10)
    students = odoo.search("op.student", [["active", "=", True]], limit=20)

    if not marksheet_lines or not exams:
        skip("No marksheet lines or exams found for progressive assessment seeding")
        return

    marks_data = [78, 65, 92, 55, 83, 70, 45, 88, 61, 74,
                  50, 95, 68, 77, 82, 59, 91, 63, 85, 72]
    statuses = ["pass" if m >= 50 else "fail" for m in marks_data]

    created_count = 0
    for i in range(min(len(marks_data), len(marksheet_lines))):
        ml_id = marksheet_lines[i]
        exam_id = exams[i % len(exams)]
        stu_id = students[i % len(students)] if students else None
        marks = marks_data[i]
        status = statuses[i]

        # Check for duplicate
        existing = odoo.search_count("op.result.line",
                                     [["marksheet_line_id", "=", ml_id],
                                      ["exam_id", "=", exam_id]])
        if existing:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create result line: marks={marks}, status={status}")
            continue

        try:
            vals: dict = {
                "marksheet_line_id": ml_id,
                "exam_id": exam_id,
                "marks": marks,
                "status": status,
            }
            if stu_id:
                vals["student_id"] = stu_id
            rl_id = odoo.create("op.result.line", vals)
            created_count += 1
            log(f"✓ Assessment result created (id={rl_id}, marks={marks}, status={status})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Result line failed: {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new result lines created – they may already exist)")


# ---------------------------------------------------------------------------
# 7. Seed Student Fee Invoices
# ---------------------------------------------------------------------------

def seed_fee_invoices(odoo: OdooRPC, dry_run: bool):
    header("7. Student Fee Invoices")
    if not odoo.model_exists("account.move"):
        skip("account.move model not installed")
        return

    students = odoo.search_read("op.student",
                                [["active", "=", True]],
                                fields=["id", "partner_id", "first_name", "last_name"],
                                limit=15)
    if not students:
        skip("No students found for invoice seeding")
        return

    # Find or create a fee income account
    account_id = None
    if odoo.model_exists("account.account"):
        accounts = odoo.search("account.account",
                               [["account_type", "in", ["income", "income_other"]]],
                               limit=1)
        account_id = accounts[0] if accounts else None

    # Find a sales journal
    journal_id = None
    journals = odoo.search("account.journal", [["type", "=", "sale"]], limit=1)
    if journals:
        journal_id = journals[0]

    if not journal_id or not account_id:
        skip("No sale journal or income account found – skipping fee invoices")
        return

    fee_items = [
        ("Tuition Fees – Term 1", 1500.00),
        ("Boarding Fees – Term 1", 800.00),
        ("Library Fee",             50.00),
        ("Sports Activity Fee",    100.00),
        ("Examination Fee",        200.00),
    ]

    created_count = 0
    for stu in students:
        partner_id = stu["partner_id"][0] if stu.get("partner_id") else None
        if not partner_id:
            continue

        name = f"{stu.get('first_name', '')} {stu.get('last_name', '')}".strip()
        inv_ref = f"INV-STU-{stu['id']:04d}-{today_str().replace('-', '')}"

        existing = odoo.search("account.move",
                               [["ref", "=", inv_ref], ["move_type", "=", "out_invoice"]],
                               limit=1)
        if existing:
            continue

        if dry_run:
            log(f"[DRY-RUN] Would create fee invoice for {name}")
            continue

        try:
            lines = []
            for desc, price in fee_items:
                line: dict = {
                    "name": desc,
                    "quantity": 1.0,
                    "price_unit": price,
                    "account_id": account_id,
                }
                lines.append((0, 0, line))

            inv_id = odoo.create("account.move", {
                "partner_id": partner_id,
                "move_type": "out_invoice",
                "invoice_date": today_str(),
                "ref": inv_ref,
                "invoice_line_ids": lines,
                "journal_id": journal_id,
                "narration": f"Academic fees invoice for {name}",
            })
            created_count += 1
            log(f"✓ Fee invoice created for {name} (id={inv_id})")
        except Exception as exc:  # pylint: disable=broad-except
            log(f"  ✗ Fee invoice for {name} failed: {exc}")

    if created_count == 0 and not dry_run:
        log("  (No new fee invoices created – they may already exist)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    print(f"\nopenEMIS ERP Demo Data Seeder")
    print(f"  URL     : {args.url}")
    print(f"  DB      : {args.db}")
    print(f"  User    : {args.user}")
    print(f"  Dry-run : {args.dry_run}\n")

    odoo = OdooRPC(args.url, args.db)
    try:
        uid = odoo.authenticate(args.user, args.password)
        print(f"  ✓ Authenticated (uid={uid})\n")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"  ✗ Authentication failed: {exc}")
        sys.exit(1)

    seed_hr_employees(odoo, args.dry_run)
    seed_payslips(odoo, args.dry_run)
    seed_purchase_orders(odoo, args.dry_run)
    seed_payment_vouchers(odoo, args.dry_run)
    seed_discipline_records(odoo, args.dry_run)
    seed_progressive_assessments(odoo, args.dry_run)
    seed_fee_invoices(odoo, args.dry_run)

    print(f"\n{'=' * 60}")
    print("  openEMIS ERP data seeding complete.")
    if args.dry_run:
        print("  (DRY-RUN mode – no records were actually created)")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
