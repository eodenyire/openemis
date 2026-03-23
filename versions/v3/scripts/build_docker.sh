#!/usr/bin/env bash
# =============================================================================
# openEMIS – Docker Image Build & Push Script
# =============================================================================
# Builds (and optionally pushes) the openEMIS Docker image with proper tagging.
#
# Usage:
#   bash scripts/build_docker.sh [OPTIONS]
#
# Options:
#   --tag TAG          Image tag (default: latest)
#   --registry REG     Registry prefix, e.g. docker.io/myorg (default: openemis)
#   --push             Push the image to the registry after building
#   --no-cache         Build without using the Docker layer cache
#   --platform PLAT    Target platform(s), e.g. linux/amd64,linux/arm64
#                      (requires docker buildx; default: current platform)
#   --help             Show this message
#
# Examples:
#   # Build a 'latest' image locally
#   bash scripts/build_docker.sh
#
#   # Build and tag a release image
#   bash scripts/build_docker.sh --tag v1.0.0
#
#   # Build a multi-platform image and push to Docker Hub
#   bash scripts/build_docker.sh \
#       --tag v1.0.0 \
#       --registry docker.io/openemis \
#       --platform linux/amd64,linux/arm64 \
#       --push
#
# Prerequisites:
#   - Docker >= 20.x
#   - For multi-platform builds: docker buildx with a suitable builder instance
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ---- Defaults ---------------------------------------------------------------
TAG="latest"
REGISTRY="openemis"
PUSH=false
NO_CACHE=false
PLATFORM=""

# ---- Helpers ----------------------------------------------------------------
log()  { echo "[build-docker] $*"; }
ok()   { echo -e "\033[0;32m  ✓ $*\033[0m"; }
fail() { echo -e "\033[0;31m  ✗ $*\033[0m"; exit 1; }

usage() {
    grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \{0,1\}//'
    exit 0
}

# ---- Parse arguments --------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)       TAG="$2";      shift 2 ;;
        --registry)  REGISTRY="$2"; shift 2 ;;
        --push)      PUSH=true;     shift ;;
        --no-cache)  NO_CACHE=true; shift ;;
        --platform)  PLATFORM="$2"; shift 2 ;;
        --help|-h)   usage ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ---- Derived values ---------------------------------------------------------
IMAGE_NAME="${REGISTRY}:${TAG}"
BUILD_DATE=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git -C "${REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# ---- Pre-flight -------------------------------------------------------------
command -v docker >/dev/null 2>&1 || fail "Docker is not installed or not on PATH."

log "openEMIS Docker image builder"
log "  Image   : ${IMAGE_NAME}"
log "  Commit  : ${GIT_COMMIT} (${GIT_BRANCH})"
log "  Push    : ${PUSH}"
if [ -n "$PLATFORM" ]; then
    log "  Platform: ${PLATFORM}"
fi

# ---- Build ------------------------------------------------------------------
echo ""
log "Building image …"

BUILD_ARGS=(
    "--file=${REPO_ROOT}/Dockerfile"
    "--tag=${IMAGE_NAME}"
    "--label=org.opencontainers.image.created=${BUILD_DATE}"
    "--label=org.opencontainers.image.revision=${GIT_COMMIT}"
    "--label=org.opencontainers.image.ref.name=${GIT_BRANCH}"
)

if [ "$NO_CACHE" = "true" ]; then
    BUILD_ARGS+=("--no-cache")
fi

if [ -n "$PLATFORM" ]; then
    # Multi-platform build via buildx
    command -v docker >/dev/null 2>&1 || fail "docker buildx is required for multi-platform builds."
    BUILD_CMD=(docker buildx build "${BUILD_ARGS[@]}" "--platform=${PLATFORM}")
    if [ "$PUSH" = "true" ]; then
        BUILD_CMD+=("--push")
    else
        BUILD_CMD+=("--load")
    fi
    BUILD_CMD+=("${REPO_ROOT}")
    log "Running: ${BUILD_CMD[*]}"
    "${BUILD_CMD[@]}"
else
    # Single-platform build via standard docker build
    BUILD_CMD=(docker build "${BUILD_ARGS[@]}" "${REPO_ROOT}")
    log "Running: ${BUILD_CMD[*]}"
    "${BUILD_CMD[@]}"
fi

ok "Image built successfully: ${IMAGE_NAME}"

# ---- Optionally push --------------------------------------------------------
if [ "$PUSH" = "true" ] && [ -z "$PLATFORM" ]; then
    # Single-platform push (multi-platform already pushed above via --push)
    log "Pushing ${IMAGE_NAME} …"
    docker push "${IMAGE_NAME}"
    ok "Image pushed: ${IMAGE_NAME}"
fi

# ---- Also tag as 'latest' if a version tag was specified --------------------
if [ "$TAG" != "latest" ]; then
    LATEST_IMAGE="${REGISTRY}:latest"
    log "Also tagging as: ${LATEST_IMAGE}"
    docker tag "${IMAGE_NAME}" "${LATEST_IMAGE}" 2>/dev/null || true
    ok "Tagged: ${LATEST_IMAGE}"
    if [ "$PUSH" = "true" ] && [ -z "$PLATFORM" ]; then
        docker push "${LATEST_IMAGE}"
        ok "Pushed: ${LATEST_IMAGE}"
    fi
fi

# ---- Summary ----------------------------------------------------------------
echo ""
echo "======================================================"
echo "  openEMIS Docker Build Complete"
echo "======================================================"
echo "  Image   : ${IMAGE_NAME}"
echo "  Commit  : ${GIT_COMMIT}"
echo "  Branch  : ${GIT_BRANCH}"
echo "  Built   : ${BUILD_DATE}"
if [ "$PUSH" = "true" ]; then
    echo "  Pushed  : yes"
fi
echo "======================================================"
echo ""
echo "  To run the image locally:"
echo "    docker compose up -d"
echo "  or:"
echo "    docker run -p 8069:8069 \\"
echo "      -e HOST=<postgres-host> -e USER=odoo -e PASSWORD=odoo \\"
echo "      ${IMAGE_NAME}"
echo ""
