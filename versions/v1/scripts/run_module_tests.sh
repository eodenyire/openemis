#!/usr/bin/env bash
# =============================================================================
# openEMIS – Per-Module Test Runner
# =============================================================================
# Runs Odoo's built-in unit-test runner for a single openEMIS module (or all
# modules if no module is specified).  Useful for quickly validating changes
# in isolation and for generating per-module test evidence.
#
# Usage:
#   bash scripts/run_module_tests.sh [MODULE] [DB_HOST] [DB_PORT] [DB_NAME] \
#                                    [DB_USER] [DB_PASS] [ODOO_BIN]
#
# Examples:
#   # Run all module tests (Docker Compose stack must be running)
#   bash scripts/run_module_tests.sh
#
#   # Run only the core module tests
#   bash scripts/run_module_tests.sh openeducat_core
#
#   # Run classroom tests against a custom DB host
#   bash scripts/run_module_tests.sh openeducat_classroom db 5432 openemis odoo odoo
#
# Prerequisites:
#   - A running PostgreSQL instance (default: localhost:5432)
#   - Odoo installed (or Docker image odoo:18.0 available)
#
# When running without a local Odoo installation, the script automatically
# uses 'docker run odoo:18.0' so no local Odoo install is required.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ---- Parameters (with defaults) -------------------------------------------
MODULE="${1:-ALL}"          # Module name, e.g. openeducat_core, or ALL
DB_HOST="${2:-localhost}"
DB_PORT="${3:-5432}"
DB_NAME="${4:-openemis_test}"
DB_USER="${5:-odoo}"
DB_PASS="${6:-odoo}"
ODOO_BIN="${7:-}"           # Path to odoo binary; auto-detected if empty

ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons"
LOG_LEVEL="test"

# All modules that ship unit tests
ALL_MODULES=(
    openeducat_core
    openeducat_admission
    openeducat_activity
    openeducat_assignment
    openeducat_attendance
    openeducat_blog
    openeducat_classroom
    openeducat_digiguide
    openeducat_exam
    openeducat_facility
    openeducat_fees
    openeducat_library
    openeducat_mentorship
    openeducat_parent
    openeducat_timetable
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()    { echo "[module-test] $*"; }
ok()     { echo -e "\033[0;32m  ✓ PASS\033[0m  $*"; }
fail()   { echo -e "\033[0;31m  ✗ FAIL\033[0m  $*"; }
header() { echo -e "\n\033[1;34m=== $* ===\033[0m"; }

PASSED_MODULES=0
FAILED_MODULES=0

# ---------------------------------------------------------------------------
# Detect Odoo binary / Docker image
# ---------------------------------------------------------------------------
detect_odoo() {
    if [ -n "$ODOO_BIN" ]; then
        log "Using provided Odoo binary: ${ODOO_BIN}"
        return
    fi

    # Check for local odoo binary
    if command -v odoo >/dev/null 2>&1; then
        ODOO_BIN="odoo"
        log "Found local Odoo binary: $(which odoo)"
        return
    fi
    if command -v odoo-bin >/dev/null 2>&1; then
        ODOO_BIN="odoo-bin"
        log "Found local Odoo binary: $(which odoo-bin)"
        return
    fi

    # Fall back to Docker
    if command -v docker >/dev/null 2>&1; then
        log "No local Odoo found – will use Docker image odoo:18.0"
        ODOO_BIN="__docker__"
        return
    fi

    echo "ERROR: Neither a local Odoo binary nor Docker is available." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Run tests for a single module
# ---------------------------------------------------------------------------
run_tests_for_module() {
    local module="$1"

    header "Testing module: ${module}"

    local common_args=(
        "--db_host=${DB_HOST}"
        "--db_port=${DB_PORT}"
        "--db_user=${DB_USER}"
        "--db_password=${DB_PASS}"
        "--database=${DB_NAME}"
        "--addons-path=${ADDONS_PATH}"
        "--init=${module}"
        "--load-language=en_US"
        "--without-demo=False"
        "--test-enable"
        "--stop-after-init"
        "--log-level=${LOG_LEVEL}"
    )

    local exit_code=0
    local log_file="/tmp/openemis_test_${module}.log"

    if [ "$ODOO_BIN" = "__docker__" ]; then
        docker run --rm \
            --network host \
            -v "${REPO_ROOT}:/mnt/extra-addons" \
            odoo:18.0 \
            odoo "${common_args[@]}" 2>&1 | tee "${log_file}" || exit_code=$?
    else
        ADDONS_PATH="${REPO_ROOT}:$(python3 -c \
            "import odoo; import os; print(os.path.join(os.path.dirname(odoo.__file__),'addons'))" \
            2>/dev/null || echo '/usr/lib/python3/dist-packages/odoo/addons')"
        common_args[5]="--addons-path=${ADDONS_PATH}"
        "${ODOO_BIN}" "${common_args[@]}" 2>&1 | tee "${log_file}" || exit_code=$?
    fi

    # Analyse log for failures
    if grep -qE "ERROR|CRITICAL|At least one test failed" "${log_file}" 2>/dev/null; then
        exit_code=1
    fi

    if [ "$exit_code" -eq 0 ]; then
        ok "Module ${module}: all tests passed"
        PASSED_MODULES=$((PASSED_MODULES + 1))
    else
        fail "Module ${module}: tests FAILED  (log: ${log_file})"
        FAILED_MODULES=$((FAILED_MODULES + 1))
    fi

    return "$exit_code"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
detect_odoo

log "openEMIS per-module test runner"
log "  DB   : ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
log "  Odoo : ${ODOO_BIN}"

if [ "$MODULE" = "ALL" ]; then
    log "Running tests for all ${#ALL_MODULES[@]} modules…"
    OVERALL_EXIT=0
    for mod in "${ALL_MODULES[@]}"; do
        run_tests_for_module "$mod" || OVERALL_EXIT=1
    done
else
    run_tests_for_module "$MODULE" || true
    OVERALL_EXIT=$FAILED_MODULES
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "======================================================"
echo "  Module Test Summary"
echo "======================================================"
echo "  Passed : ${PASSED_MODULES}"
echo "  Failed : ${FAILED_MODULES}"
echo "======================================================"

[ "$FAILED_MODULES" -eq 0 ] || exit 1
