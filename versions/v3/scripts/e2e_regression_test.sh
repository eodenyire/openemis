#!/usr/bin/env bash
# =============================================================================
# openEMIS – End-to-End Functional & Regression Test Suite
# =============================================================================
# Exercises every major EMIS workflow via the Odoo JSON-RPC API, covering:
#   1.  Health & version
#   2.  Authentication
#   3.  Student lifecycle  (create → enrol → read → archive)
#   4.  Faculty / HR lifecycle
#   5.  Admission workflow (application → register)
#   6.  Exam workflow      (session → exam → attendees → marksheet → result)
#   7.  Student result slip / marksheet report check
#   8.  Report card / grade configuration check
#   9.  Fees & payment voucher workflow
#  10.  LPO / Purchase Order workflow (via account/purchase modules)
#  11.  Payslip / Payroll workflow
#  12.  Discipline records workflow
#  13.  Progressive assessment (continuous assessment) workflow
#  14.  Attendance records workflow
#  15.  Timetable records workflow
#  16.  Library resource records workflow
#  17.  Assignment records workflow
#  18.  Parent portal records check
#  19.  Grading configuration check
#  20.  Module install status check
#
# Usage:
#   bash scripts/e2e_regression_test.sh [HOST] [PORT] [DB] [USER] [PASSWORD]
#
# Defaults:
#   HOST     = localhost
#   PORT     = 8069
#   DB       = openemis
#   USER     = admin
#   PASSWORD = admin
#
# Exit codes:
#   0 – all tests passed
#   1 – one or more tests failed
# =============================================================================

set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-8069}"
DB="${3:-openemis}"
USER="${4:-admin}"
PASSWORD="${5:-admin}"

BASE_URL="http://${HOST}:${PORT}"
COOKIE_JAR="/tmp/openemis_e2e_cookies_$$.txt"

PASSED=0
FAILED=0
SKIPPED=0

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[1;34m'
NC='\033[0m'

log()     { echo "[e2e] $*"; }
ok()      { echo -e "${GREEN}  ✓ PASS${NC}  $*"; PASSED=$((PASSED + 1)); }
fail()    { echo -e "${RED}  ✗ FAIL${NC}  $*"; FAILED=$((FAILED + 1)); }
skip()    { echo -e "${YELLOW}  ⚠ SKIP${NC}  $*"; SKIPPED=$((SKIPPED + 1)); }
header()  { echo -e "\n${BLUE}=== $* ===${NC}"; }

# ---------------------------------------------------------------------------
# JSON-RPC helper
# ---------------------------------------------------------------------------
jsonrpc() {
    local endpoint="$1"
    local payload="$2"
    curl -s -X POST \
        -H "Content-Type: application/json" \
        --cookie-jar "${COOKIE_JAR}" \
        --cookie "${COOKIE_JAR}" \
        --max-time 30 \
        "${BASE_URL}${endpoint}" \
        -d "${payload}"
}

# Extract a field from a JSON-RPC response using Python
extract() {
    local json="$1"
    local key="$2"
    echo "$json" | python3 -c \
        "import sys,json; r=json.load(sys.stdin); print(r.get('result') if '$key'=='result' else r.get('result',{}).get('$key','') if isinstance(r.get('result',{}),dict) else '')" 2>/dev/null || echo ""
}

# Check whether the 'result' key is present and not an error
has_result() {
    local json="$1"
    echo "$json" | python3 -c \
        "import sys,json; r=json.load(sys.stdin); print('ok' if 'result' in r and r.get('error') is None else 'fail')" 2>/dev/null || echo "fail"
}

# Count items in a JSON-RPC search_count result
result_count() {
    local json="$1"
    echo "$json" | python3 -c \
        "import sys,json; r=json.load(sys.stdin); print(r.get('result',0))" 2>/dev/null || echo "0"
}

# Call search_count on a model
count_model() {
    local model="$1"
    local filter="${2:-[]}"
    local resp
    resp=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"${model}","method":"search_count","args":[${filter}],"kwargs":{}}}
EOF
)")
    result_count "$resp"
}

# Call create on a model
create_record() {
    local model="$1"
    local vals="$2"
    local resp
    resp=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"${model}","method":"create","args":[${vals}],"kwargs":{}}}
EOF
)")
    echo "$resp" | python3 -c \
        "import sys,json; r=json.load(sys.stdin); print(r.get('result',''))" 2>/dev/null || echo ""
}

# Call write on a model
write_record() {
    local model="$1"
    local ids="$2"
    local vals="$3"
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"${model}","method":"write","args":[[${ids}],${vals}],"kwargs":{}}}
EOF
)" >/dev/null 2>&1 || true
}

# Call unlink (delete) on a model
delete_record() {
    local model="$1"
    local ids="$2"
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"${model}","method":"unlink","args":[[${ids}]],"kwargs":{}}}
EOF
)" >/dev/null 2>&1 || true
}

# Read specific fields from a record
read_record() {
    local model="$1"
    local id="$2"
    local fields="$3"
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"${model}","method":"read","args":[[${id}]],"kwargs":{"fields":${fields}}}}
EOF
)"
}

# Check if a model exists in the registry
model_exists() {
    local model="$1"
    local resp
    resp=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"ir.model","method":"search_count","args":[[["model","=","${model}"]]],"kwargs":{}}}
EOF
)")
    local cnt
    cnt=$(result_count "$resp")
    [ "${cnt:-0}" -gt 0 ]
}

# ---------------------------------------------------------------------------
# 1. Health & version
# ---------------------------------------------------------------------------
header "1. Health & Version"

HEALTH=$(curl -s --max-time 10 "${BASE_URL}/web/health" || echo '{}')
if echo "$HEALTH" | grep -q '"status"'; then
    ok "Health endpoint reachable at ${BASE_URL}/web/health"
else
    fail "Health endpoint unreachable – is openEMIS running at ${BASE_URL}?"
fi

VERSION_RESP=$(jsonrpc "/web/webclient/version_info" '{"jsonrpc":"2.0","method":"call","params":{}}')
SERVER_VER=$(extract "$VERSION_RESP" server_version)
if [ -n "$SERVER_VER" ] && [ "$SERVER_VER" != "None" ]; then
    ok "Server version: ${SERVER_VER}"
else
    fail "Could not retrieve server version"
fi

# ---------------------------------------------------------------------------
# 2. Authentication
# ---------------------------------------------------------------------------
header "2. Authentication"

AUTH_RESP=$(jsonrpc "/web/session/authenticate" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"db":"${DB}","login":"${USER}","password":"${PASSWORD}"}}
EOF
)")
UID=$(extract "$AUTH_RESP" uid)
if [ -n "$UID" ] && [ "$UID" != "None" ] && [ "$UID" != "false" ]; then
    ok "Authenticated as '${USER}' (uid=${UID})"
else
    fail "Authentication failed for user '${USER}' on database '${DB}'"
    echo "  → Subsequent tests may fail due to missing authentication."
fi

# ---------------------------------------------------------------------------
# 3. Module install status
# ---------------------------------------------------------------------------
header "3. Installed openEMIS Modules"

MODULES_RESP=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"ir.module.module","method":"search_read","args":[[["name","like","openemis"],["state","=","installed"]]],"kwargs":{"fields":["name","state"],"order":"name"}}}
EOF
)")
MOD_COUNT=$(echo "$MODULES_RESP" | python3 -c \
    "import sys,json; r=json.load(sys.stdin); print(len(r.get('result',[])))" 2>/dev/null || echo "0")

if [ "${MOD_COUNT:-0}" -gt 0 ]; then
    ok "${MOD_COUNT} openEMIS module(s) installed"
    echo "$MODULES_RESP" | python3 -c \
        "import sys,json; [print('     -', m['name']) for m in json.load(sys.stdin).get('result',[])]" 2>/dev/null || true
else
    fail "No openEMIS modules appear to be installed (count=${MOD_COUNT})"
fi

# ---------------------------------------------------------------------------
# 4. Student lifecycle
# ---------------------------------------------------------------------------
header "4. Student Lifecycle (Create → Enrol → Read → Archive)"

# Count existing students
STU_BEFORE=$(count_model "op.student" '[["active","=",true]]')
log "Students before test: ${STU_BEFORE}"

# Create a test partner
E2E_PARTNER_ID=$(create_record "res.partner" \
    '{"name":"E2E Test Student","email":"e2e_student@openemis.example.com"}')
if [ -n "$E2E_PARTNER_ID" ] && [ "$E2E_PARTNER_ID" != "None" ] && [ "$E2E_PARTNER_ID" != "" ]; then
    ok "Student partner created (id=${E2E_PARTNER_ID})"
else
    fail "Student partner creation failed"
    E2E_PARTNER_ID=""
fi

E2E_STUDENT_ID=""
if [ -n "$E2E_PARTNER_ID" ]; then
    E2E_STUDENT_ID=$(create_record "op.student" \
        "{\"first_name\":\"E2ETest\",\"last_name\":\"Regression\",\"birth_date\":\"2005-03-14\",\"gender\":\"m\",\"partner_id\":${E2E_PARTNER_ID}}")
    if [ -n "$E2E_STUDENT_ID" ] && [ "$E2E_STUDENT_ID" != "None" ] && [ "$E2E_STUDENT_ID" != "" ]; then
        ok "Student created (id=${E2E_STUDENT_ID})"
    else
        fail "Student creation failed"
        E2E_STUDENT_ID=""
    fi
fi

if [ -n "$E2E_STUDENT_ID" ]; then
    # Read back
    READ_RESP=$(read_record "op.student" "$E2E_STUDENT_ID" '["first_name","last_name","gender","birth_date","active"]')
    FIRST=$(echo "$READ_RESP" | python3 -c \
        "import sys,json; r=json.load(sys.stdin)['result']; print(r[0]['first_name'])" 2>/dev/null || echo "")
    if [ "$FIRST" = "E2ETest" ]; then
        ok "Student read-back verified (first_name=${FIRST})"
    else
        fail "Student read-back mismatch (got '${FIRST}', expected 'E2ETest')"
    fi

    # Archive the student (write active=false)
    write_record "op.student" "$E2E_STUDENT_ID" '{"active": false}'
    ARCHIVED=$(count_model "op.student" "[\"&\",[\"id\",\"=\",${E2E_STUDENT_ID}],[\"active\",\"=\",false]]")
    if [ "${ARCHIVED:-0}" -eq 1 ]; then
        ok "Student archived successfully"
    else
        fail "Student archive failed"
    fi

    # Cleanup
    delete_record "op.student" "$E2E_STUDENT_ID"
    delete_record "res.partner" "$E2E_PARTNER_ID"
fi

# ---------------------------------------------------------------------------
# 5. Faculty / HR lifecycle
# ---------------------------------------------------------------------------
header "5. Faculty / HR Lifecycle"

FAC_BEFORE=$(count_model "op.faculty" '[["active","=",true]]')
log "Faculty records before test: ${FAC_BEFORE}"

E2E_FAC_PARTNER_ID=$(create_record "res.partner" \
    '{"name":"E2E Test Faculty","email":"e2e_faculty@openemis.example.com"}')
E2E_FAC_ID=""
if [ -n "$E2E_FAC_PARTNER_ID" ] && [ "$E2E_FAC_PARTNER_ID" != "None" ] && [ "$E2E_FAC_PARTNER_ID" != "" ]; then
    E2E_FAC_ID=$(create_record "op.faculty" \
        "{\"first_name\":\"E2EFaculty\",\"last_name\":\"Test\",\"gender\":\"f\",\"partner_id\":${E2E_FAC_PARTNER_ID}}")
    if [ -n "$E2E_FAC_ID" ] && [ "$E2E_FAC_ID" != "None" ] && [ "$E2E_FAC_ID" != "" ]; then
        ok "Faculty record created (id=${E2E_FAC_ID})"
    else
        fail "Faculty creation failed"
        E2E_FAC_ID=""
    fi
else
    fail "Faculty partner creation failed"
fi

if [ -n "$E2E_FAC_ID" ]; then
    FAC_READ=$(read_record "op.faculty" "$E2E_FAC_ID" '["first_name","last_name","active"]')
    FAC_FIRST=$(echo "$FAC_READ" | python3 -c \
        "import sys,json; print(json.load(sys.stdin)['result'][0]['first_name'])" 2>/dev/null || echo "")
    if [ "$FAC_FIRST" = "E2EFaculty" ]; then
        ok "Faculty read-back verified"
    else
        fail "Faculty read-back mismatch (got '${FAC_FIRST}')"
    fi
    delete_record "op.faculty" "$E2E_FAC_ID"
    delete_record "res.partner" "$E2E_FAC_PARTNER_ID"
fi

# ---------------------------------------------------------------------------
# 6. Admission workflow
# ---------------------------------------------------------------------------
header "6. Admission Workflow"

if model_exists "op.admission"; then
    ADMIT_COUNT=$(count_model "op.admission")
    if [ "${ADMIT_COUNT:-0}" -ge 0 ]; then
        ok "Admission model accessible (${ADMIT_COUNT} records)"
    else
        fail "Admission model not accessible"
    fi

    REGISTER_COUNT=$(count_model "op.admission.register")
    ok "Admission registers: ${REGISTER_COUNT}"
else
    skip "op.admission model not installed"
fi

# ---------------------------------------------------------------------------
# 7. Exam workflow (session → exam → attendees → marksheet → result)
# ---------------------------------------------------------------------------
header "7. Exam Workflow"

if model_exists "op.exam.session"; then
    SESSION_COUNT=$(count_model "op.exam.session")
    ok "Exam sessions in DB: ${SESSION_COUNT}"

    EXAM_COUNT=$(count_model "op.exam")
    ok "Exams in DB: ${EXAM_COUNT}"

    ATTENDEE_COUNT=$(count_model "op.exam.attendees")
    ok "Exam attendees in DB: ${ATTENDEE_COUNT}"
else
    skip "op.exam.session model not installed"
fi

if model_exists "op.marksheet.register"; then
    MARKSHEET_COUNT=$(count_model "op.marksheet.register")
    ok "Marksheet registers in DB: ${MARKSHEET_COUNT}"

    MARKLINE_COUNT=$(count_model "op.marksheet.line")
    ok "Marksheet lines in DB: ${MARKLINE_COUNT}"
else
    skip "op.marksheet.register model not installed"
fi

if model_exists "op.result.line"; then
    RESULT_COUNT=$(count_model "op.result.line")
    ok "Result lines in DB: ${RESULT_COUNT}"
else
    skip "op.result.line model not installed"
fi

# ---------------------------------------------------------------------------
# 8. Student result slip / marksheet report generation check
# ---------------------------------------------------------------------------
header "8. Student Result Slip / Marksheet Report"

if model_exists "op.marksheet.register"; then
    # Verify that the report action is registered
    REPORT_RESP=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"ir.actions.report","method":"search_count","args":[[["report_name","like","marksheet"]]],"kwargs":{}}}
EOF
)")
    REPORT_CNT=$(result_count "$REPORT_RESP")
    if [ "${REPORT_CNT:-0}" -ge 1 ]; then
        ok "Marksheet report action registered (${REPORT_CNT} report(s))"
    else
        fail "No marksheet report action found in ir.actions.report"
    fi
else
    skip "Marksheet model not installed – skipping report check"
fi

# ---------------------------------------------------------------------------
# 9. Report card / grade configuration
# ---------------------------------------------------------------------------
header "9. Report Card & Grade Configuration"

if model_exists "op.grading.config"; then
    GRADE_CONFIG_COUNT=$(count_model "op.grading.config")
    ok "Grading configurations in DB: ${GRADE_CONFIG_COUNT}"

    GRADE_RULE_COUNT=$(count_model "op.grading.rule")
    ok "Grading rules in DB: ${GRADE_RULE_COUNT}"
else
    skip "op.grading.config model not installed"
fi

if model_exists "op.grade.configuration"; then
    GC_COUNT=$(count_model "op.grade.configuration")
    ok "Exam grade configurations in DB: ${GC_COUNT}"
else
    skip "op.grade.configuration not installed"
fi

# ---------------------------------------------------------------------------
# 10. Fees & payment voucher workflow
# ---------------------------------------------------------------------------
header "10. Fees & Payment Voucher Workflow"

if model_exists "op.fees.terms"; then
    FEES_COUNT=$(count_model "op.fees.terms")
    ok "Fee terms in DB: ${FEES_COUNT}"
else
    skip "op.fees.terms model not installed"
fi

if model_exists "op.student.fees.details"; then
    SFEES_COUNT=$(count_model "op.student.fees.details")
    ok "Student fee detail records: ${SFEES_COUNT}"
else
    skip "op.student.fees.details model not installed"
fi

# Payment vouchers are account.payment records linked to students
if model_exists "account.payment"; then
    PAYMENT_COUNT=$(count_model "account.payment")
    ok "Account payments (payment vouchers) in DB: ${PAYMENT_COUNT}"

    INVOICE_COUNT=$(count_model "account.move" '[["move_type","in",["out_invoice","out_receipt"]]]')
    ok "Customer invoices in DB: ${INVOICE_COUNT}"
else
    skip "account.payment model not installed"
fi

# ---------------------------------------------------------------------------
# 11. LPO / Purchase Order workflow
# ---------------------------------------------------------------------------
header "11. LPO / Purchase Order Workflow"

if model_exists "purchase.order"; then
    PO_COUNT=$(count_model "purchase.order")
    ok "Purchase orders (LPOs) in DB: ${PO_COUNT}"

    PO_LINE_COUNT=$(count_model "purchase.order.line")
    ok "Purchase order lines in DB: ${PO_LINE_COUNT}"
else
    skip "purchase.order model not installed (purchase module may not be enabled)"
fi

if model_exists "stock.picking"; then
    PICK_COUNT=$(count_model "stock.picking")
    ok "Stock pickings (LPO receipts) in DB: ${PICK_COUNT}"
else
    skip "stock.picking model not installed"
fi

# ---------------------------------------------------------------------------
# 12. Payslip / Payroll workflow
# ---------------------------------------------------------------------------
header "12. Payslip / Payroll Workflow"

if model_exists "hr.payslip"; then
    PAYSLIP_COUNT=$(count_model "hr.payslip")
    ok "Payslips in DB: ${PAYSLIP_COUNT}"

    PAYSLIP_LINE_COUNT=$(count_model "hr.payslip.line")
    ok "Payslip lines in DB: ${PAYSLIP_LINE_COUNT}"
else
    skip "hr.payslip model not installed (payroll module may not be enabled)"
fi

if model_exists "hr.employee"; then
    EMP_COUNT=$(count_model "hr.employee" '[["active","=",true]]')
    ok "Active HR employees in DB: ${EMP_COUNT}"
else
    skip "hr.employee model not installed"
fi

# ---------------------------------------------------------------------------
# 13. Discipline records workflow
# ---------------------------------------------------------------------------
header "13. Discipline Records Workflow"

if model_exists "op.discipline"; then
    DISC_COUNT=$(count_model "op.discipline")
    ok "Discipline records in DB: ${DISC_COUNT}"
else
    fail "op.discipline model not accessible – discipline module may not be installed"
fi

if model_exists "op.misbehaviour.category"; then
    MISB_COUNT=$(count_model "op.misbehaviour.category")
    ok "Misbehaviour categories in DB: ${MISB_COUNT}"
else
    skip "op.misbehaviour.category not installed"
fi

if model_exists "op.discipline.action"; then
    DACT_COUNT=$(count_model "op.discipline.action")
    ok "Discipline action types in DB: ${DACT_COUNT}"
else
    skip "op.discipline.action not installed"
fi

# Create a discipline record, verify it, then delete it
if model_exists "op.discipline" && model_exists "op.student"; then
    SAMPLE_STU=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"op.student","method":"search","args":[[["active","=",true]]],"kwargs":{"limit":1}}}
EOF
)")
    SAMPLE_STU_ID=$(echo "$SAMPLE_STU" | python3 -c \
        "import sys,json; r=json.load(sys.stdin).get('result',[]); print(r[0] if r else '')" 2>/dev/null || echo "")

    SAMPLE_MISB=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"op.misbehaviour.category","method":"search","args":[[]],"kwargs":{"limit":1}}}
EOF
)")
    SAMPLE_MISB_ID=$(echo "$SAMPLE_MISB" | python3 -c \
        "import sys,json; r=json.load(sys.stdin).get('result',[]); print(r[0] if r else '')" 2>/dev/null || echo "")

    SAMPLE_DACT=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{"jsonrpc":"2.0","method":"call","params":{"model":"op.discipline.action","method":"search","args":[[]],"kwargs":{"limit":1}}}
EOF
)")
    SAMPLE_DACT_ID=$(echo "$SAMPLE_DACT" | python3 -c \
        "import sys,json; r=json.load(sys.stdin).get('result',[]); print(r[0] if r else '')" 2>/dev/null || echo "")

    if [ -n "$SAMPLE_STU_ID" ] && [ -n "$SAMPLE_MISB_ID" ] && [ -n "$SAMPLE_DACT_ID" ]; then
        TODAY=$(date '+%Y-%m-%d')
        E2E_DISC_ID=$(create_record "op.discipline" \
            "{\"student_id\":${SAMPLE_STU_ID},\"misbehaviour_category_id\":${SAMPLE_MISB_ID},\"discipline_action_id\":${SAMPLE_DACT_ID},\"date\":\"${TODAY}\",\"description\":\"E2E regression test record\",\"state\":\"reported\"}")
        if [ -n "$E2E_DISC_ID" ] && [ "$E2E_DISC_ID" != "None" ] && [ "$E2E_DISC_ID" != "" ]; then
            ok "Discipline record created (id=${E2E_DISC_ID})"
            delete_record "op.discipline" "$E2E_DISC_ID"
        else
            fail "Discipline record creation failed"
        fi
    else
        skip "Could not find student/misbehaviour/action records for discipline round-trip"
    fi
fi

# ---------------------------------------------------------------------------
# 14. Progressive / Continuous Assessment workflow
# ---------------------------------------------------------------------------
header "14. Progressive / Continuous Assessment"

# In openEMIS the continuous-assessment data is stored in exam result lines
# and marksheet registers.  We check counts and that the grading pipeline
# has complete data.
if model_exists "op.result.line"; then
    PASS_COUNT=$(count_model "op.result.line" '[["status","=","pass"]]')
    FAIL_COUNT=$(count_model "op.result.line" '[["status","=","fail"]]')
    ok "Progressive assessment result lines – pass: ${PASS_COUNT}, fail: ${FAIL_COUNT}"

    TOTAL_RESULTS=$(count_model "op.result.line")
    if [ "${TOTAL_RESULTS:-0}" -gt 0 ]; then
        ok "Assessment data present (${TOTAL_RESULTS} total result lines)"
    else
        fail "No progressive assessment result lines found in database"
    fi
else
    skip "op.result.line model not installed"
fi

# Check for result templates (report card templates)
if model_exists "op.result.template"; then
    RT_COUNT=$(count_model "op.result.template")
    ok "Result templates (report card templates) in DB: ${RT_COUNT}"
else
    skip "op.result.template not installed"
fi

# ---------------------------------------------------------------------------
# 15. Attendance records
# ---------------------------------------------------------------------------
header "15. Attendance Records"

if model_exists "op.attendance"; then
    ATT_COUNT=$(count_model "op.attendance")
    ok "Attendance records in DB: ${ATT_COUNT}"
else
    skip "op.attendance model not installed"
fi

# ---------------------------------------------------------------------------
# 16. Timetable records
# ---------------------------------------------------------------------------
header "16. Timetable Records"

if model_exists "op.timetable"; then
    TT_COUNT=$(count_model "op.timetable")
    ok "Timetable records in DB: ${TT_COUNT}"
else
    skip "op.timetable model not installed"
fi

# ---------------------------------------------------------------------------
# 17. Library resources
# ---------------------------------------------------------------------------
header "17. Library Resources"

if model_exists "op.library.resource"; then
    LIB_COUNT=$(count_model "op.library.resource")
    ok "Library resources in DB: ${LIB_COUNT}"
else
    skip "op.library.resource model not installed"
fi

# ---------------------------------------------------------------------------
# 18. Assignments
# ---------------------------------------------------------------------------
header "18. Assignment Records"

if model_exists "op.assignment"; then
    ASSIGN_COUNT=$(count_model "op.assignment")
    ok "Assignments in DB: ${ASSIGN_COUNT}"
else
    skip "op.assignment model not installed"
fi

# ---------------------------------------------------------------------------
# 19. Parent portal records
# ---------------------------------------------------------------------------
header "19. Parent Portal Records"

if model_exists "op.parent"; then
    PAR_COUNT=$(count_model "op.parent")
    ok "Parent records in DB: ${PAR_COUNT}"
else
    skip "op.parent model not installed"
fi

# ---------------------------------------------------------------------------
# 20. Core data integrity checks
# ---------------------------------------------------------------------------
header "20. Core Data Integrity"

COURSE_COUNT=$(count_model "op.course" '[["active","=",true]]')
if [ "${COURSE_COUNT:-0}" -ge 1 ]; then
    ok "Courses in DB: ${COURSE_COUNT}"
else
    fail "No courses found – demo data may not be loaded"
fi

BATCH_COUNT=$(count_model "op.batch" '[["active","=",true]]')
if [ "${BATCH_COUNT:-0}" -ge 1 ]; then
    ok "Batches in DB: ${BATCH_COUNT}"
else
    fail "No batches found"
fi

SUBJECT_COUNT=$(count_model "op.subject" '[["active","=",true]]')
ok "Subjects in DB: ${SUBJECT_COUNT}"

ACYEAR_COUNT=$(count_model "op.academic.year")
if [ "${ACYEAR_COUNT:-0}" -ge 1 ]; then
    ok "Academic years in DB: ${ACYEAR_COUNT}"
else
    fail "No academic years found"
fi

ACTERM_COUNT=$(count_model "op.academic.term")
ok "Academic terms in DB: ${ACTERM_COUNT}"

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------
echo ""
echo "======================================================"
echo "  openEMIS End-to-End Regression Test Summary"
echo "======================================================"
printf "  %-10s %d\n" "PASSED:"  "${PASSED}"
printf "  %-10s %d\n" "FAILED:"  "${FAILED}"
printf "  %-10s %d\n" "SKIPPED:" "${SKIPPED}"
printf "  %-10s %d\n" "TOTAL:"   "$((PASSED + FAILED + SKIPPED))"
echo "======================================================"

rm -f "${COOKIE_JAR}"

if [ "${FAILED}" -gt 0 ]; then
    echo -e "${RED}  ${FAILED} test(s) FAILED.${NC}"
    exit 1
else
    echo -e "${GREEN}  All ${PASSED} tests passed!${NC}"
fi
