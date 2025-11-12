#!/bin/bash
#
# Handle Process Completion Action
#
# Generic handler for external process completion.
# Reports results and can trigger follow-up actions.
#

set -euo pipefail

WATCH_PATH="${1:-}"
LOG_FILE="${2:-}"
PARSED_FILE="${WATCH_PATH}.parsed.json"

# Logging
log() {
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [handle_process_completion] ${message}"
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[${timestamp}] [handle_process_completion] ${message}" >> "${LOG_FILE}"
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
EXIT_CODE=$(jq -r '.exit_code // "unknown"' "${PARSED_FILE}")
ERROR_COUNT=$(jq -r '.errors | length' "${PARSED_FILE}")
WARNING_COUNT=$(jq -r '.warnings | length' "${PARSED_FILE}")
OUTPUT_LINES=$(jq -r '.output_lines' "${PARSED_FILE}")
PROCESS_TYPE=$(jq -r '.metadata.process_type // "unknown"' "${PARSED_FILE}")
EXEC_TIME=$(jq -r '.metadata.execution_time // "unknown"' "${PARSED_FILE}")

log "Process completed:"
log "  Status: ${STATUS}"
log "  Success: ${SUCCESS}"
log "  Exit code: ${EXIT_CODE}"
log "  Process type: ${PROCESS_TYPE}"
log "  Errors: ${ERROR_COUNT}"
log "  Warnings: ${WARNING_COUNT}"
log "  Output lines: ${OUTPUT_LINES}"
log "  Execution time: ${EXEC_TIME}"

# Handle based on status
if [[ "${SUCCESS}" == "true" ]]; then
    log "Process completed successfully"

    if [[ ${WARNING_COUNT} -gt 0 ]]; then
        log "WARN: Process completed with ${WARNING_COUNT} warning(s):"
        jq -r '.warnings[]' "${PARSED_FILE}" | head -n 5 | while read -r warning; do
            log "  - ${warning}"
        done
    fi

    # Add custom follow-up actions here
    log "Process successful - ready for next step"

    exit 0
else
    log "ERROR: Process failed"

    if [[ "${EXIT_CODE}" != "unknown" && "${EXIT_CODE}" != "null" ]]; then
        log "Exit code: ${EXIT_CODE}"
    fi

    if [[ ${ERROR_COUNT} -gt 0 ]]; then
        log "Errors encountered:"
        jq -r '.errors[]' "${PARSED_FILE}" | head -n 10 | while read -r error; do
            log "  - ${error}"
        done
    fi

    log "Review process output and errors"

    exit 1
fi
