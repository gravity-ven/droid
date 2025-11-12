#!/bin/bash
#
# Handle Build Result Action
#
# Processes build completion and triggers next steps (e.g., tests).
#

set -euo pipefail

WATCH_PATH="${1:-}"
LOG_FILE="${2:-}"
PARSED_FILE="${WATCH_PATH}.parsed.json"

# Logging
log() {
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [handle_build_result] ${message}"
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[${timestamp}] [handle_build_result] ${message}" >> "${LOG_FILE}"
    fi
}

# Validate inputs
if [[ -z "${WATCH_PATH}" ]]; then
    log "ERROR: watch_path required"
    exit 1
fi

if [[ ! -f "${PARSED_FILE}" ]]; then
    log "ERROR: Parsed file not found: ${PARSED_FILE}"
    exit 1
fi

# Read parsed data
if ! command -v jq &> /dev/null; then
    log "ERROR: jq required but not installed"
    exit 1
fi

STATUS=$(jq -r '.status' "${PARSED_FILE}")
SUCCESS=$(jq -r '.success' "${PARSED_FILE}")
ERROR_COUNT=$(jq -r '.error_count' "${PARSED_FILE}")
WARNING_COUNT=$(jq -r '.warning_count' "${PARSED_FILE}")
BUILD_TIME=$(jq -r '.build_time // "unknown"' "${PARSED_FILE}")
BUILD_SYSTEM=$(jq -r '.metadata.build_system // "unknown"' "${PARSED_FILE}")

log "Build completed:"
log "  Status: ${STATUS}"
log "  Success: ${SUCCESS}"
log "  Errors: ${ERROR_COUNT}"
log "  Warnings: ${WARNING_COUNT}"
log "  Build time: ${BUILD_TIME}"
log "  Build system: ${BUILD_SYSTEM}"

# Handle based on status
if [[ "${SUCCESS}" == "true" ]]; then
    log "Build succeeded!"

    if [[ ${WARNING_COUNT} -gt 0 ]]; then
        log "WARN: Build completed with ${WARNING_COUNT} warning(s):"
        jq -r '.warnings[]' "${PARSED_FILE}" | head -n 5 | while read -r warning; do
            log "  - ${warning}"
        done
    fi

    # Trigger tests if configured
    # This is where you would start a test watcher
    log "Build successful - ready for testing"

    # Example: Start test watcher (uncomment to enable)
    # TEST_WATCHER=$(python3 ~/.claude/watchers/session_manager.py create test_runner test-results/results.xml)
    # python3 ~/.claude/watchers/session_manager.py start "${TEST_WATCHER}"
    # log "Started test watcher: ${TEST_WATCHER}"

    exit 0
else
    log "ERROR: Build failed with ${ERROR_COUNT} error(s):"

    jq -r '.errors[]' "${PARSED_FILE}" | head -n 10 | while read -r error; do
        log "  - ${error}"
    done

    log "Fix build errors before proceeding"

    exit 1
fi
