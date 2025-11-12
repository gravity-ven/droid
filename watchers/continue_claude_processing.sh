#!/bin/bash
#
# Continue Claude Processing Action
#
# Analyzes parsed Claude output and determines next steps.
# Triggers continuation if actions are needed.
#

set -euo pipefail

WATCH_PATH="${1:-}"
LOG_FILE="${2:-}"
PARSED_FILE="${WATCH_PATH}.parsed.json"

# Logging
log() {
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [continue_claude_processing] ${message}"
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[${timestamp}] [continue_claude_processing] ${message}" >> "${LOG_FILE}"
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
ACTIONS_COUNT=$(jq -r '.actions_needed | length' "${PARSED_FILE}")
ERRORS_COUNT=$(jq -r '.errors | length' "${PARSED_FILE}")

log "Parsed Claude output:"
log "  Status: ${STATUS}"
log "  Success: ${SUCCESS}"
log "  Actions needed: ${ACTIONS_COUNT}"
log "  Errors: ${ERRORS_COUNT}"

# Handle based on status
case "${STATUS}" in
    complete)
        log "Claude processing completed successfully"

        if [[ ${ACTIONS_COUNT} -gt 0 ]]; then
            log "Actions still needed:"
            jq -r '.actions_needed[]' "${PARSED_FILE}" | while read -r action; do
                log "  - ${action}"
            done
            log "NOTE: Manual intervention may be required for these actions"
        fi

        exit 0
        ;;

    pending)
        log "Claude processing is pending - awaiting user input or external event"

        # Could trigger notification here
        log "Consider checking Claude Code session for pending tasks"

        exit 0
        ;;

    error)
        log "ERROR: Claude processing failed with errors:"

        jq -r '.errors[]' "${PARSED_FILE}" | while read -r error; do
            log "  - ${error}"
        done

        # Could trigger error notification or recovery here
        log "Review errors and restart processing if needed"

        exit 1
        ;;

    in_progress)
        log "Claude processing still in progress"
        log "Output may be incomplete - consider extending watch time"

        exit 0
        ;;

    *)
        log "WARN: Unknown status: ${STATUS}"
        exit 0
        ;;
esac
