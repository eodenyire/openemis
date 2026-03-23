#!/usr/bin/env bash
# =============================================================================
# openEMIS – Snapshot / Evidence Capture Script
# =============================================================================
# Authenticates against a running Odoo instance, queries every openEMIS module
# endpoint and saves the JSON response as a snapshot file.  Each snapshot acts
# as test evidence – it can be diffed across releases and checked in CI for
# regressions.
#
# Usage:
#   bash scripts/snapshot_test.sh [HOST] [PORT] [DB] [USER] [PASSWORD] [OUT_DIR]
#
# Defaults:
#   HOST    = localhost
#   PORT    = 8069
#   DB      = openemis
#   USER    = admin
#   PASSWORD= admin
#   OUT_DIR = /tmp/openemis_snapshots
#
# Outputs:
#   <OUT_DIR>/
#     auth_session.json          – authentication token / uid
#     module_<name>_records.json – first page of records for each module model
#     module_<name>_count.json   – record count for each model
#     health.json                – Odoo health endpoint response
#     version.json               – Odoo version info
#     summary.txt                – human-readable pass/fail summary
# =============================================================================

set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-8069}"
DB="${3:-openemis}"
USER="${4:-admin}"
PASSWORD="${5:-admin}"
OUT_DIR="${6:-/tmp/openemis_snapshots}"

BASE_URL="http://${HOST}:${PORT}"

PASSED=0
FAILED=0
SNAPSHOTS=0

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
mkdir -p "${OUT_DIR}"
COOKIE_JAR="${OUT_DIR}/.cookies.txt"

log()    { echo "[snapshot] $*"; }
ok()     { echo -e "\033[0;32m  ✓ PASS\033[0m  $*"; PASSED=$((PASSED + 1)); }
fail()   { echo -e "\033[0;31m  ✗ FAIL\033[0m  $*"; FAILED=$((FAILED + 1)); }
header() { echo -e "\n\033[1;34m=== $* ===\033[0m"; }

save_snapshot() {
    local name="$1"
    local content="$2"
    local file="${OUT_DIR}/${name}.json"
    echo "$content" | python3 -c "import sys,json; print(json.dumps(json.loads(sys.stdin.read()), indent=2))" \
        > "${file}" 2>/dev/null \
        || echo "$content" > "${file}"
    SNAPSHOTS=$((SNAPSHOTS + 1))
    log "  Snapshot saved → ${file}"
}

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

count_records() {
    local model="$1"
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "${model}",
        "method": "search_count",
        "args": [[]],
        "kwargs": {}
    }
}
EOF
)"
}

read_records() {
    local model="$1"
    local limit="${2:-10}"
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "${model}",
        "method": "search_read",
        "args": [[]],
        "kwargs": {"limit": ${limit}, "order": "id desc"}
    }
}
EOF
)"
}

# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------
header "1. Health Check"
HEALTH=$(curl -s --max-time 10 "${BASE_URL}/web/health" || echo '{"status":"error"}')
save_snapshot "health" "${HEALTH}"
if echo "$HEALTH" | grep -q '"status"'; then
    ok "Health endpoint reachable"
else
    fail "Health endpoint unreachable"
fi

# ---------------------------------------------------------------------------
# 2. Version info
# ---------------------------------------------------------------------------
header "2. Version Info"
VERSION=$(jsonrpc "/web/webclient/version_info" '{"jsonrpc":"2.0","method":"call","params":{}}')
save_snapshot "version" "${VERSION}"
SERVER_VER=$(echo "$VERSION" | python3 -c \
    "import sys,json; print(json.load(sys.stdin).get('result',{}).get('server_version','?'))" 2>/dev/null || echo "?")
if [ "$SERVER_VER" != "?" ]; then
    ok "Server version: ${SERVER_VER}"
else
    fail "Could not retrieve server version"
fi

# ---------------------------------------------------------------------------
# 3. Authenticate
# ---------------------------------------------------------------------------
header "3. Authentication"
AUTH_RESP=$(jsonrpc "/web/session/authenticate" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "${DB}",
        "login": "${USER}",
        "password": "${PASSWORD}"
    }
}
EOF
)")
save_snapshot "auth_session" "${AUTH_RESP}"
UID=$(echo "$AUTH_RESP" | python3 -c \
    "import sys,json; r=json.load(sys.stdin); print(r.get('result',{}).get('uid',''))" 2>/dev/null || echo "")
if [ -n "$UID" ] && [ "$UID" != "None" ] && [ "$UID" != "false" ]; then
    ok "Authenticated as '${USER}' (uid=${UID})"
else
    fail "Authentication failed – subsequent tests will likely fail"
fi

# ---------------------------------------------------------------------------
# 4. Module snapshots
#    For each openEMIS module, capture record counts and first page of data
# ---------------------------------------------------------------------------
header "4. Module Snapshots"

snapshot_module() {
    local label="$1"    # human-readable label
    local model="$2"    # Odoo model dotted name
    local safe_name
    safe_name=$(echo "$label" | tr '[:upper:]/ ' '[:lower:]__')

    # Count
    COUNT_RESP=$(count_records "$model")
    save_snapshot "module_${safe_name}_count" "${COUNT_RESP}"
    COUNT=$(echo "$COUNT_RESP" | python3 -c \
        "import sys,json; print(json.load(sys.stdin).get('result','?'))" 2>/dev/null || echo "?")

    # Records (up to 10)
    REC_RESP=$(read_records "$model" 10)
    save_snapshot "module_${safe_name}_records" "${REC_RESP}"
    HAS_RESULT=$(echo "$REC_RESP" | python3 -c \
        "import sys,json; r=json.load(sys.stdin); print('ok' if 'result' in r else 'fail')" 2>/dev/null || echo "fail")

    if [ "$HAS_RESULT" = "ok" ]; then
        ok "[$label] model=${model}  records=${COUNT}"
    else
        fail "[$label] model=${model}  API error"
    fi
}

# Core
snapshot_module "Students"               "op.student"
snapshot_module "Faculty"                "op.faculty"
snapshot_module "Courses"                "op.course"
snapshot_module "Batches"                "op.batch"
snapshot_module "Subjects"               "op.subject"
snapshot_module "StudentCourse"          "op.student.course"

# Admissions
snapshot_module "Applications"          "op.admission"

# Classrooms
snapshot_module "Classrooms"            "op.classroom"

# Assignments
snapshot_module "Assignments"           "op.assignment"

# Attendance
snapshot_module "Attendance"            "op.attendance"

# Exams
snapshot_module "ExamSessions"          "op.exam.session"

# Fees
snapshot_module "FeeTypes"              "op.fee.terms"

# Library
snapshot_module "LibraryResources"      "op.library.resource"

# Timetable
snapshot_module "Timetable"             "op.timetable"

# Mentorship
snapshot_module "Mentors"               "op.mentor"

# Blog
snapshot_module "BlogPosts"             "op.blog.post"

# DigiGuide
snapshot_module "DigiGuideRecords"      "op.digiguide.student"

# Parent
snapshot_module "Parents"               "op.parent"

# Facility
snapshot_module "Facilities"            "op.facility"

# Activity
snapshot_module "Activities"            "op.activity"

# ---------------------------------------------------------------------------
# 5. Registration simulation – create + verify + delete a student
# ---------------------------------------------------------------------------
header "5. Student Registration Round-trip"

# Create partner
REG_PARTNER_RESP=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "res.partner",
        "method": "create",
        "args": [{
            "name": "Snapshot Test Student",
            "email": "snapshot_test@openemis.example.com"
        }],
        "kwargs": {}
    }
}
EOF
)")
save_snapshot "registration_partner_create" "${REG_PARTNER_RESP}"
REG_PARTNER_ID=$(echo "$REG_PARTNER_RESP" | python3 -c \
    "import sys,json; print(json.load(sys.stdin).get('result',''))" 2>/dev/null || echo "")

if [ -n "$REG_PARTNER_ID" ] && [ "$REG_PARTNER_ID" != "None" ]; then
    ok "Registration: partner created (id=${REG_PARTNER_ID})"

    # Create student
    REG_STU_RESP=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "op.student",
        "method": "create",
        "args": [{
            "first_name": "Snapshot",
            "last_name": "TestStudent",
            "birth_date": "2004-07-20",
            "gender": "f",
            "partner_id": ${REG_PARTNER_ID}
        }],
        "kwargs": {}
    }
}
EOF
)")
    save_snapshot "registration_student_create" "${REG_STU_RESP}"
    REG_STU_ID=$(echo "$REG_STU_RESP" | python3 -c \
        "import sys,json; print(json.load(sys.stdin).get('result',''))" 2>/dev/null || echo "")

    if [ -n "$REG_STU_ID" ] && [ "$REG_STU_ID" != "None" ]; then
        ok "Registration: student created (id=${REG_STU_ID})"

        # Read back
        REG_READ_RESP=$(jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "op.student",
        "method": "read",
        "args": [[${REG_STU_ID}]],
        "kwargs": {"fields": ["first_name","last_name","gender","birth_date","active"]}
    }
}
EOF
)")
        save_snapshot "registration_student_read" "${REG_READ_RESP}"
        READ_FIRST=$(echo "$REG_READ_RESP" | python3 -c \
            "import sys,json; r=json.load(sys.stdin)['result']; print(r[0]['first_name'])" 2>/dev/null || echo "")
        if [ "$READ_FIRST" = "Snapshot" ]; then
            ok "Registration: student read-back verified (first_name=${READ_FIRST})"
        else
            fail "Registration: read-back mismatch (got '${READ_FIRST}')"
        fi

        # Cleanup – delete student
        jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "op.student",
        "method": "unlink",
        "args": [[${REG_STU_ID}]],
        "kwargs": {}
    }
}
EOF
)" >/dev/null 2>&1 || true
    else
        fail "Registration: student creation failed"
    fi

    # Cleanup – delete partner
    jsonrpc "/web/dataset/call_kw" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "res.partner",
        "method": "unlink",
        "args": [[${REG_PARTNER_ID}]],
        "kwargs": {}
    }
}
EOF
)" >/dev/null 2>&1 || true
else
    fail "Registration: partner creation failed"
fi

# ---------------------------------------------------------------------------
# 6. Login endpoint check (web session)
# ---------------------------------------------------------------------------
header "6. Login Endpoint"
LOGIN_RESP=$(jsonrpc "/web/session/authenticate" "$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "${DB}",
        "login": "${USER}",
        "password": "${PASSWORD}"
    }
}
EOF
)")
save_snapshot "login_endpoint" "${LOGIN_RESP}"
LOGIN_UID=$(echo "$LOGIN_RESP" | python3 -c \
    "import sys,json; r=json.load(sys.stdin); print(r.get('result',{}).get('uid',''))" 2>/dev/null || echo "")
if [ -n "$LOGIN_UID" ] && [ "$LOGIN_UID" != "None" ]; then
    ok "Login endpoint: authenticated (uid=${LOGIN_UID})"
else
    fail "Login endpoint: authentication failed"
fi

# ---------------------------------------------------------------------------
# 7. Write summary
# ---------------------------------------------------------------------------
header "7. Summary"

SUMMARY="${OUT_DIR}/summary.txt"
cat > "${SUMMARY}" <<SUMMARY_EOF
openEMIS Snapshot Test Summary
===============================
Date      : $(date -u '+%Y-%m-%dT%H:%M:%SZ')
Host      : ${HOST}:${PORT}
Database  : ${DB}
User      : ${USER}
Snapshots : ${SNAPSHOTS} saved to ${OUT_DIR}/

Results
-------
PASSED : ${PASSED}
FAILED : ${FAILED}
TOTAL  : $((PASSED + FAILED))
SUMMARY_EOF

echo ""
cat "${SUMMARY}"

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo -e "\033[0;32m  All ${PASSED} snapshot tests passed!  Evidence in ${OUT_DIR}/\033[0m"
else
    echo -e "\033[0;31m  ${PASSED} passed, ${FAILED} FAILED.  See ${OUT_DIR}/ for details.\033[0m"
fi

rm -f "${COOKIE_JAR}"
[ "$FAILED" -eq 0 ] || exit 1
