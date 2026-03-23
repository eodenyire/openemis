#!/usr/bin/env bash
# =============================================================================
# openEMIS – Kubernetes Smoke Test Script
# =============================================================================
# Deploys the openEMIS Kubernetes manifests to a target cluster and validates
# that all pods are running and the Odoo health endpoint is accessible.
#
# Usage:
#   bash scripts/k8s_test.sh [KUBECONFIG] [IMAGE_TAG] [ODOO_URL]
#
# Defaults:
#   KUBECONFIG = $HOME/.kube/config (kubectl default)
#   IMAGE_TAG  = latest
#   ODOO_URL   = http://localhost:8069
#
# Prerequisites:
#   - kubectl configured to access your target cluster
#   - kustomize or kubectl >= 1.14 (kubectl apply -k)
#   - The openEMIS Docker image already built and available on the node(s)
#
# For a local test with kind:
#   kind create cluster --name openemis-local
#   docker build -t openemis:latest .
#   kind load docker-image openemis:latest --name openemis-local
#   bash scripts/k8s_test.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

KUBECONFIG="${1:-${HOME}/.kube/config}"
IMAGE_TAG="${2:-latest}"
ODOO_URL="${3:-http://localhost:8069}"
NAMESPACE="openemis"

WAIT_TIMEOUT="300s"
HEALTH_RETRIES=30
HEALTH_INTERVAL=10

PASSED=0
FAILED=0

export KUBECONFIG

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()    { echo "[k8s-test] $*"; }
ok()     { echo -e "\033[0;32m  ✓ PASS\033[0m  $*"; PASSED=$((PASSED + 1)); }
fail()   { echo -e "\033[0;31m  ✗ FAIL\033[0m  $*"; FAILED=$((FAILED + 1)); }
header() { echo -e "\n\033[1;34m=== $* ===\033[0m"; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "ERROR: required command not found: $1" >&2
        exit 1
    }
}

require_cmd kubectl
require_cmd curl

# ---------------------------------------------------------------------------
# 1. Cluster connectivity
# ---------------------------------------------------------------------------
header "1. Cluster Connectivity"
if kubectl cluster-info >/dev/null 2>&1; then
    SERVER=$(kubectl cluster-info 2>/dev/null | head -1 | sed 's/.*at //')
    ok "kubectl can reach cluster: ${SERVER}"
else
    fail "kubectl cannot reach cluster – check KUBECONFIG (${KUBECONFIG})"
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Apply Kubernetes manifests
# ---------------------------------------------------------------------------
header "2. Apply Kubernetes Manifests"
log "Applying manifests from ${REPO_ROOT}/kubernetes/ …"
kubectl apply -k "${REPO_ROOT}/kubernetes/" 2>&1
ok "Manifests applied"

# ---------------------------------------------------------------------------
# 3. Wait for PostgreSQL
# ---------------------------------------------------------------------------
header "3. Wait for PostgreSQL"
log "Waiting for PostgreSQL deployment (timeout: ${WAIT_TIMEOUT})…"
if kubectl -n "${NAMESPACE}" rollout status deployment/postgres \
        --timeout="${WAIT_TIMEOUT}" 2>&1; then
    ok "PostgreSQL pod is running"
else
    fail "PostgreSQL deployment did not become ready in time"
    kubectl -n "${NAMESPACE}" describe deployment/postgres || true
    kubectl -n "${NAMESPACE}" logs -l app=postgres --tail=30 || true
fi

# ---------------------------------------------------------------------------
# 4. Wait for openEMIS
# ---------------------------------------------------------------------------
header "4. Wait for openEMIS"
log "Waiting for openEMIS deployment (timeout: ${WAIT_TIMEOUT})…"
if kubectl -n "${NAMESPACE}" rollout status deployment/openemis \
        --timeout="${WAIT_TIMEOUT}" 2>&1; then
    ok "openEMIS pod is running"
else
    fail "openEMIS deployment did not become ready in time"
    kubectl -n "${NAMESPACE}" describe deployment/openemis || true
    kubectl -n "${NAMESPACE}" logs -l app=openemis --tail=50 || true
fi

# ---------------------------------------------------------------------------
# 5. Pod status check
# ---------------------------------------------------------------------------
header "5. Pod Status"
log "Current pod status in namespace '${NAMESPACE}':"
kubectl -n "${NAMESPACE}" get pods -o wide

# Verify all pods are Running or Completed (not Pending/Error/CrashLoopBackOff)
BAD_PODS=$(kubectl -n "${NAMESPACE}" get pods \
    --field-selector=status.phase!=Running,status.phase!=Succeeded \
    -o name 2>/dev/null | wc -l || echo "0")
if [ "${BAD_PODS}" -eq 0 ]; then
    ok "All pods in '${NAMESPACE}' are Running/Succeeded"
else
    fail "${BAD_PODS} pod(s) are not in Running/Succeeded state"
fi

# ---------------------------------------------------------------------------
# 6. Odoo health endpoint
# ---------------------------------------------------------------------------
header "6. Odoo Health Check"
log "Polling ${ODOO_URL}/web/health (${HEALTH_RETRIES} attempts, ${HEALTH_INTERVAL}s interval)…"

SUCCESS=false
for i in $(seq 1 "${HEALTH_RETRIES}"); do
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time 10 \
        "${ODOO_URL}/web/health" 2>/dev/null || echo "000")
    if [ "$HTTP" = "200" ]; then
        SUCCESS=true
        ok "Odoo health endpoint responded with HTTP ${HTTP} (attempt ${i})"
        break
    fi
    log "  Attempt ${i}/${HEALTH_RETRIES} – HTTP ${HTTP} – sleeping ${HEALTH_INTERVAL}s…"
    sleep "${HEALTH_INTERVAL}"
done

if [ "$SUCCESS" != "true" ]; then
    fail "Odoo health endpoint did not return HTTP 200 after ${HEALTH_RETRIES} attempts"
    kubectl -n "${NAMESPACE}" logs -l app=openemis --tail=30 || true
fi

# ---------------------------------------------------------------------------
# 7. Service / endpoint check
# ---------------------------------------------------------------------------
header "7. Service Endpoint"
SVC_INFO=$(kubectl -n "${NAMESPACE}" get svc openemis -o json 2>/dev/null || echo "{}")
SVC_TYPE=$(echo "$SVC_INFO" | python3 -c \
    "import sys,json; print(json.load(sys.stdin).get('spec',{}).get('type','?'))" 2>/dev/null || echo "?")
if [ "$SVC_TYPE" != "?" ]; then
    ok "openEMIS service exists (type=${SVC_TYPE})"
else
    fail "openEMIS service not found in namespace '${NAMESPACE}'"
fi

# ---------------------------------------------------------------------------
# 8. Summary
# ---------------------------------------------------------------------------
echo ""
echo "======================================================"
if [ "$FAILED" -eq 0 ]; then
    echo -e "\033[0;32m  All ${PASSED} Kubernetes tests passed!\033[0m"
    echo "  Cluster is ready.  Access Odoo at: ${ODOO_URL}"
else
    echo -e "\033[0;31m  ${PASSED} passed, ${FAILED} FAILED.\033[0m"
fi
echo "======================================================"

[ "$FAILED" -eq 0 ] || exit 1
