#!/bin/bash
#
# Handle Test Results Action
#
# Processes test completion and reports results.
# Can trigger deployment or other follow-up actions.
#

set -euo pipefail

WATCH_PATH="${1:-}"
LOG_FILE="${2:-}"
PARSED_FILE="${WATCH_PATH}.parsed.json"

# Logging
log() {
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [handle_test_results] ${message}"
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[${timestamp}] [handle_test_results] ${message}" >> "${LOG_FILE}"
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
TOTAL=$(jq -r '.total_tests' "${PARSED_FILE}")
PASSED=$(jq -r '.passed' "${PARSED_FILE}")
FAILED=$(jq -r '.failed' "${PARSED_FILE}")
ERRORS=$(jq -r '.errors' "${PARSED_FILE}")
SKIPPED=$(jq -r '.skipped' "${PARSED_FILE}")
TEST_TIME=$(jq -r '.test_time // "unknown"' "${PARSED_FILE}")
FRAMEWORK=$(jq -r '.metadata.framework // "unknown"' "${PARSED_FILE}")

log "Test results:"
log "  Status: ${STATUS}"
log "  Success: ${SUCCESS}"
log "  Total: ${TOTAL}"
log "  Passed: ${PASSED}"
log "  Failed: ${FAILED}"
log "  Errors: ${ERRORS}"
log "  Skipped: ${SKIPPED}"
log "  Test time: ${TEST_TIME}"
log "  Framework: ${FRAMEWORK}"

# Calculate pass rate
if [[ ${TOTAL} -gt 0 ]]; then
    PASS_RATE=$(echo "scale=2; ${PASSED} * 100 / ${TOTAL}" | bc)
    log "  Pass rate: ${PASS_RATE}%"
fi

# Handle based on status
if [[ "${SUCCESS}" == "true" ]]; then
    log "All tests passed!"

    if [[ ${SKIPPED} -gt 0 ]]; then
        log "NOTE: ${SKIPPED} test(s) were skipped"
    fi

    # Trigger deployment or next step if configured
    log "Tests successful - ready for deployment"

    # Example: Start deployment (uncomment to enable)
    # log "Triggering deployment..."
    # ./deploy.sh 2>&1 | tee -a "${LOG_FILE}"

    exit 0
else
    log "ERROR: Tests failed"

    # Show failure details
    FAILURE_COUNT=$(jq -r '.failures | length' "${PARSED_FILE}")
    if [[ ${FAILURE_COUNT} -gt 0 ]]; then
        log "Failed tests:"
        jq -r '.failures[] | "  - \(.test): \(.message)"' "${PARSED_FILE}" | head -n 10
    fi

    ERROR_DETAIL_COUNT=$(jq -r '.error_details | length' "${PARSED_FILE}")
    if [[ ${ERROR_DETAIL_COUNT} -gt 0 ]]; then
        log "Test errors:"
        jq -r '.error_details[] | "  - \(.test): \(.message)"' "${PARSED_FILE}" | head -n 10
    fi

    log "Fix failing tests before proceeding"

    exit 1
fi
