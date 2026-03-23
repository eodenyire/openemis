#!/usr/bin/env python3
"""
openEMIS – Playwright Screenshot Capture Script
=================================================
Launches a headless Chromium browser via Playwright, authenticates against a
running Odoo/openEMIS instance, navigates to every major module view, and
captures full-page screenshots with real data visible.

Screenshots saved to:
    <OUT_DIR>/                          (default: screenshots/)
        00_login.png
        01_home.png
        02_students_list.png
        03_student_detail.png
        04_faculty_list.png
        05_admissions.png
        06_exam_sessions.png
        07_result_slips.png
        08_report_card.png
        09_fees_invoices.png
        10_payment_vouchers.png
        11_purchase_orders_lpo.png
        12_payslips.png
        13_discipline_records.png
        14_progressive_assessments.png
        15_attendance.png
        16_timetable.png
        17_library.png
        18_assignments.png
        19_parents.png
        20_grading_config.png
        21_dashboards.png
        22_human_resources.png
        23_cbc_strands.png
        24_cbc_learning_outcomes.png
        25_cbc_formative_assessments.png
        26_cbc_portfolios.png
        27_cbc_report_cards.png
        28_hostel.png
        29_transportation.png
        30_health.png
        31_lms.png
        32_scholarships.png
        33_digiguide.png
        34_mentorship.png
        35_all_modules.png

Usage::

    # Install dependencies (once)
    pip install playwright
    playwright install chromium

    # Run capture (openEMIS must be running)
    python scripts/capture_screenshots.py

    # Custom target
    python scripts/capture_screenshots.py \\
        --url http://localhost:8069 \\
        --db openemis \\
        --user admin \\
        --password admin \\
        --out screenshots/
"""

import argparse
import os
import sys
import time

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
DEFAULT_URL = os.environ.get("ODOO_URL", "http://localhost:8069")
DEFAULT_DB = os.environ.get("ODOO_DB", "openemis")
DEFAULT_USER = os.environ.get("ODOO_USER", "admin")
DEFAULT_PASS = os.environ.get("ODOO_PASSWORD", "admin")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(REPO_ROOT, "screenshots")


def parse_args():
    p = argparse.ArgumentParser(description="openEMIS screenshot capture")
    p.add_argument("--url", default=DEFAULT_URL, help="Odoo base URL")
    p.add_argument("--db", default=DEFAULT_DB, help="Odoo database name")
    p.add_argument("--user", default=DEFAULT_USER, help="Odoo login username")
    p.add_argument("--password", default=DEFAULT_PASS, help="Odoo login password")
    p.add_argument("--out", default=DEFAULT_OUT, help="Output directory for screenshots")
    p.add_argument("--headless", default=True, action=argparse.BooleanOptionalAction,
                   help="Run browser in headless mode (default: True)")
    p.add_argument("--timeout", type=int, default=30000,
                   help="Navigation timeout in milliseconds (default: 30000)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Screenshot helper
# ---------------------------------------------------------------------------

def screenshot(page, out_dir: str, filename: str, description: str) -> bool:
    """Take a full-page screenshot and save it.  Returns True on success."""
    path = os.path.join(out_dir, filename)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
        page.screenshot(path=path, full_page=True)
        print(f"  ✓ {filename:45s}  {description}")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"  ✗ {filename:45s}  FAILED – {exc}")
        return False


def navigate(page, url: str, timeout: int = 30000) -> bool:
    """Navigate to a URL, returning False if navigation fails."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"  ✗ Navigation to {url} failed – {exc}")
        return False


def wait_for_selector_safe(page, selector: str, timeout: int = 10000) -> bool:
    """Wait for a CSS/XPath selector; return False if it does not appear."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


# ---------------------------------------------------------------------------
# Main capture workflow
# ---------------------------------------------------------------------------

def run_capture(args):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: 'playwright' package is not installed.")
        print("  Install it with: pip install playwright && playwright install chromium")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    base = args.url.rstrip("/")
    passed = 0
    failed = 0

    print(f"\nopenEMIS Screenshot Capture")
    print(f"  URL  : {base}")
    print(f"  DB   : {args.db}")
    print(f"  User : {args.user}")
    print(f"  Out  : {args.out}\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless)
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 900},
            locale="en_US",
        )
        page = ctx.new_page()
        page.set_default_timeout(args.timeout)

        # ── 0. Login page ──────────────────────────────────────────────────
        print("=== Login ===")
        navigate(page, f"{base}/web#action=login")
        wait_for_selector_safe(page, "input[name='login']")
        ok = screenshot(page, args.out, "00_login.png", "Login page")
        if ok:
            passed += 1
        else:
            failed += 1

        # Perform login
        try:
            page.fill("input[name='login']", args.user)
            page.fill("input[name='password']", args.password)
            page.click("button[type='submit'], .btn-primary")
            page.wait_for_load_state("networkidle", timeout=args.timeout)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"  ✗ Login action failed – {exc}")
            failed += 1

        # ── 1. Home / all apps ─────────────────────────────────────────────
        print("\n=== Home & Navigation ===")
        navigate(page, f"{base}/odoo")
        wait_for_selector_safe(page, ".o_home_menu, .o_apps, .o_action_manager", 15000)
        if screenshot(page, args.out, "01_home.png", "Home / all apps"):
            passed += 1
        else:
            failed += 1

        # ── 2. Students list ───────────────────────────────────────────────
        print("\n=== Students ===")
        navigate(page, f"{base}/odoo/students")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_view_controller", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "02_students_list.png", "Students list view"):
            passed += 1
        else:
            failed += 1

        # Open first student detail
        try:
            first_row = page.query_selector(".o_list_view tbody tr:first-child td, "
                                            ".o_kanban_record:first-child")
            if first_row:
                first_row.click()
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(0.5)
                if screenshot(page, args.out, "03_student_detail.png", "Student detail form"):
                    passed += 1
                else:
                    failed += 1
            else:
                print("  ⚠ SKIP  03_student_detail.png  – no student rows visible")
        except Exception:  # pylint: disable=broad-except
            pass

        # ── 3. Faculty list ────────────────────────────────────────────────
        print("\n=== Faculty ===")
        navigate(page, f"{base}/odoo/faculties")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "04_faculty_list.png", "Faculty list / kanban"):
            passed += 1
        else:
            failed += 1

        # ── 4. Admissions ──────────────────────────────────────────────────
        print("\n=== Admissions ===")
        navigate(page, f"{base}/odoo/admissions")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "05_admissions.png", "Admissions list"):
            passed += 1
        else:
            failed += 1

        # ── 5. Exam sessions ───────────────────────────────────────────────
        print("\n=== Exams ===")
        navigate(page, f"{base}/odoo/exam-sessions")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "06_exam_sessions.png", "Exam sessions list"):
            passed += 1
        else:
            failed += 1

        # ── 6. Result slips / marksheets ───────────────────────────────────
        print("\n=== Result Slips / Marksheets ===")
        navigate(page, f"{base}/odoo/marksheet-registers")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "07_result_slips.png", "Marksheet register (result slips)"):
            passed += 1
        else:
            failed += 1

        # ── 7. Report card / grade config ──────────────────────────────────
        print("\n=== Report Card / Grading ===")
        navigate(page, f"{base}/odoo/grading-configs")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "08_report_card.png", "Grading configurations (report card setup)"):
            passed += 1
        else:
            failed += 1

        # ── 8. Fees / invoices ─────────────────────────────────────────────
        print("\n=== Fees & Invoices ===")
        navigate(page, f"{base}/odoo/accounting/customer-invoices")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "09_fees_invoices.png", "Customer invoices (fees)"):
            passed += 1
        else:
            failed += 1

        # ── 9. Payment vouchers ────────────────────────────────────────────
        print("\n=== Payment Vouchers ===")
        navigate(page, f"{base}/odoo/accounting/payments")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "10_payment_vouchers.png", "Payments (payment vouchers)"):
            passed += 1
        else:
            failed += 1

        # ── 10. Purchase orders / LPOs ─────────────────────────────────────
        print("\n=== Purchase Orders / LPOs ===")
        navigate(page, f"{base}/odoo/purchase")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "11_purchase_orders_lpo.png", "Purchase orders (LPOs)"):
            passed += 1
        else:
            failed += 1

        # ── 11. Payslips ───────────────────────────────────────────────────
        print("\n=== Payslips ===")
        navigate(page, f"{base}/odoo/payroll")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "12_payslips.png", "Payslips / payroll"):
            passed += 1
        else:
            failed += 1

        # ── 12. Discipline records ─────────────────────────────────────────
        print("\n=== Discipline Records ===")
        navigate(page, f"{base}/odoo/disciplines")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "13_discipline_records.png", "Discipline records"):
            passed += 1
        else:
            failed += 1

        # ── 13. Progressive assessments ────────────────────────────────────
        print("\n=== Progressive / Continuous Assessments ===")
        navigate(page, f"{base}/odoo/result-lines")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "14_progressive_assessments.png",
                      "Progressive assessment result lines"):
            passed += 1
        else:
            failed += 1

        # ── 14. Attendance ─────────────────────────────────────────────────
        print("\n=== Attendance ===")
        navigate(page, f"{base}/odoo/attendances")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "15_attendance.png", "Attendance records"):
            passed += 1
        else:
            failed += 1

        # ── 15. Timetable ──────────────────────────────────────────────────
        print("\n=== Timetable ===")
        navigate(page, f"{base}/odoo/timetables")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "16_timetable.png", "Timetable"):
            passed += 1
        else:
            failed += 1

        # ── 16. Library ────────────────────────────────────────────────────
        print("\n=== Library ===")
        navigate(page, f"{base}/odoo/library")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "17_library.png", "Library resources"):
            passed += 1
        else:
            failed += 1

        # ── 17. Assignments ────────────────────────────────────────────────
        print("\n=== Assignments ===")
        navigate(page, f"{base}/odoo/assignments")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "18_assignments.png", "Assignments"):
            passed += 1
        else:
            failed += 1

        # ── 18. Parents ────────────────────────────────────────────────────
        print("\n=== Parent Portal ===")
        navigate(page, f"{base}/odoo/parents")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "19_parents.png", "Parent records"):
            passed += 1
        else:
            failed += 1

        # ── 19. Grading ────────────────────────────────────────────────────
        print("\n=== Grading Configuration ===")
        navigate(page, f"{base}/odoo/grading")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "20_grading_config.png", "Grading scale configuration"):
            passed += 1
        else:
            failed += 1

        # ── 20. Finance dashboard ──────────────────────────────────────────
        print("\n=== Finance Dashboard ===")
        navigate(page, f"{base}/odoo/accounting")
        wait_for_selector_safe(page, ".o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "21_dashboards.png", "Finance / accounting dashboard"):
            passed += 1
        else:
            failed += 1

        # ── 21. HR / Employees ─────────────────────────────────────────────
        print("\n=== Human Resources ===")
        navigate(page, f"{base}/odoo/employees")
        wait_for_selector_safe(page, ".o_list_view, .o_kanban_view, .o_action_manager", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "22_human_resources.png", "HR employees"):
            passed += 1
        else:
            failed += 1

        # ── 22. CBC Competency Strands ─────────────────────────────────────
        print("\n=== CBC – Competency Based Curriculum ===")
        navigate(page, f"{base}/odoo/cbc-strands")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "23_cbc_strands.png", "CBC competency strands"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/cbc-outcomes")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "24_cbc_learning_outcomes.png", "CBC learning outcomes"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/cbc-formative")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "25_cbc_formative_assessments.png",
                      "CBC formative assessments"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/cbc-portfolios")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "26_cbc_portfolios.png", "CBC student portfolios"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/cbc-report-cards")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "27_cbc_report_cards.png", "CBC report cards"):
            passed += 1
        else:
            failed += 1

        # ── 23. Additional modules ─────────────────────────────────────────
        print("\n=== Additional Modules ===")
        navigate(page, f"{base}/odoo/hostel-blocks")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "28_hostel.png", "Hostel management"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/vehicles")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "29_transportation.png", "Transportation / vehicles"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/student-health")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "30_health.png", "Student health records"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/lms-courses")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "31_lms.png", "LMS online courses"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/scholarships")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "32_scholarships.png", "Scholarships"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/digiguide-performance")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "33_digiguide.png", "DigiGuide – CBC career guidance"):
            passed += 1
        else:
            failed += 1

        navigate(page, f"{base}/odoo/mentors")
        wait_for_selector_safe(page, ".o_list_view, .o_action_manager", 12000)
        time.sleep(1)
        if screenshot(page, args.out, "34_mentorship.png", "Mentorship platform"):
            passed += 1
        else:
            failed += 1

        # ── 24. All modules menu ───────────────────────────────────────────
        print("\n=== All Modules Menu ===")
        navigate(page, f"{base}/odoo")
        wait_for_selector_safe(page, ".o_home_menu, .o_apps", 15000)
        time.sleep(1)
        if screenshot(page, args.out, "35_all_modules.png", "All installed modules menu"):
            passed += 1
        else:
            failed += 1

        browser.close()

    # Summary
    total = passed + failed
    print(f"\n{'=' * 54}")
    print(f"  Screenshot Capture Summary")
    print(f"{'=' * 54}")
    print(f"  Captured : {passed}")
    print(f"  Failed   : {failed}")
    print(f"  Total    : {total}")
    print(f"  Output   : {args.out}")
    print(f"{'=' * 54}\n")

    return failed == 0


if __name__ == "__main__":
    args = parse_args()
    success = run_capture(args)
    sys.exit(0 if success else 1)
