#!/bin/bash
#
# Claude Code External Process Watcher
#
# Monitors files, processes, or directories for completion markers
# and triggers actions based on parsed results.
#

set -euo pipefail

# Configuration
CONFIG_FILE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
WATCHERS_DIR="${CLAUDE_DIR}/watchers"
STATE_DIR="${CLAUDE_DIR}/state"

# Ensure directories exist
mkdir -p "${STATE_DIR}" "${SCRIPT_DIR}/logs"

# Validate config file
if [[ -z "${CONFIG_FILE}" ]]; then
    echo "Error: Config file required" >&2
    echo "Usage: $0 <config.json>" >&2
    exit 1
fi

if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "Error: Config file not found: ${CONFIG_FILE}" >&2
    exit 1
fi

# Load configuration using jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: sudo apt-get install jq" >&2
    exit 1
fi

# Extract config values
WATCH_PATH=$(jq -r '.watch_path // ""' "${CONFIG_FILE}")
WATCH_TYPE=$(jq -r '.watch_type // "file"' "${CONFIG_FILE}")
POLL_INTERVAL=$(jq -r '.poll_interval // 5' "${CONFIG_FILE}")
MAX_WAIT_TIME=$(jq -r '.max_wait_time // 3600' "${CONFIG_FILE}")
SUCCESS_MARKER=$(jq -r '.success_marker // ""' "${CONFIG_FILE}")
FAILURE_MARKER=$(jq -r '.failure_marker // ""' "${CONFIG_FILE}")
PROCESS_NAME=$(jq -r '.process_name // ""' "${CONFIG_FILE}")
PROCESS_PID=$(jq -r '.process_pid // ""' "${CONFIG_FILE}")
PARSER_SCRIPT=$(jq -r '.parser_script // ""' "${CONFIG_FILE}")
ACTION_SCRIPT=$(jq -r '.action_script // ""' "${CONFIG_FILE}")
WATCHER_ID=$(jq -r '.watcher_id // "unknown"' "${CONFIG_FILE}")

# Setup logging
LOG_FILE="${STATE_DIR}/${WATCHER_ID}.log"
EXECUTION_LOG="${SCRIPT_DIR}/logs/$(date +%Y%m%d_%H%M%S)_${WATCHER_ID}.log"

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}" "${EXECUTION_LOG}"
}

log_info() {
    log "INFO" "$@"
}

log_warn() {
    log "WARN" "$@"
}

log_error() {
    log "ERROR" "$@"
}

# Validation
validate_config() {
    log_info "Validating configuration..."

    if [[ "${WATCH_TYPE}" == "file" && -z "${WATCH_PATH}" ]]; then
        log_error "watch_path required for file watcher"
        return 1
    fi

    if [[ "${WATCH_TYPE}" == "process" && -z "${PROCESS_PID}" && -z "${PROCESS_NAME}" ]]; then
        log_error "process_pid or process_name required for process watcher"
        return 1
    fi

    if [[ -z "${PARSER_SCRIPT}" ]]; then
        log_error "parser_script required"
        return 1
    fi

    if [[ -z "${ACTION_SCRIPT}" ]]; then
        log_error "action_script required"
        return 1
    fi

    log_info "Configuration valid"
    return 0
}

# File watcher
watch_file() {
    local file_path="$1"
    local start_time=$(date +%s)
    local elapsed=0

    log_info "Watching file: ${file_path}"
    log_info "Poll interval: ${POLL_INTERVAL}s, Max wait: ${MAX_WAIT_TIME}s"

    while [[ ${elapsed} -lt ${MAX_WAIT_TIME} ]]; do
        # Check if file exists
        if [[ ! -f "${file_path}" ]]; then
            log_info "Waiting for file to appear... (${elapsed}/${MAX_WAIT_TIME}s)"
            sleep "${POLL_INTERVAL}"
            elapsed=$(( $(date +%s) - start_time ))
            continue
        fi

        # Check for markers if specified
        if [[ -n "${SUCCESS_MARKER}" ]] && grep -q "${SUCCESS_MARKER}" "${file_path}" 2>/dev/null; then
            log_info "Success marker found!"
            return 0
        fi

        if [[ -n "${FAILURE_MARKER}" ]] && grep -q "${FAILURE_MARKER}" "${file_path}" 2>/dev/null; then
            log_error "Failure marker found!"
            return 1
        fi

        # Check file stability (not modified in last poll interval)
        if [[ -n "$(find "${file_path}" -mmin +$(echo "${POLL_INTERVAL}/60" | bc -l))" ]]; then
            log_info "File appears stable, proceeding to parse"
            return 0
        fi

        log_info "File exists but still changing... (${elapsed}/${MAX_WAIT_TIME}s)"
        sleep "${POLL_INTERVAL}"
        elapsed=$(( $(date +%s) - start_time ))
    done

    log_error "Timeout waiting for file completion (${MAX_WAIT_TIME}s)"
    return 2
}

# Process watcher
watch_process() {
    local pid="${PROCESS_PID}"
    local name="${PROCESS_NAME}"
    local start_time=$(date +%s)
    local elapsed=0

    log_info "Watching process: PID=${pid}, Name=${name}"

    while [[ ${elapsed} -lt ${MAX_WAIT_TIME} ]]; do
        # Check by PID
        if [[ -n "${pid}" ]]; then
            if ! ps -p "${pid}" > /dev/null 2>&1; then
                log_info "Process ${pid} has exited"
                return 0
            fi
        # Check by name
        elif [[ -n "${name}" ]]; then
            if ! pgrep -f "${name}" > /dev/null 2>&1; then
                log_info "Process '${name}' has exited"
                return 0
            fi
        fi

        log_info "Process still running... (${elapsed}/${MAX_WAIT_TIME}s)"
        sleep "${POLL_INTERVAL}"
        elapsed=$(( $(date +%s) - start_time ))
    done

    log_error "Timeout waiting for process completion (${MAX_WAIT_TIME}s)"
    return 2
}

# Directory watcher
watch_directory() {
    local dir_path="$1"
    local start_time=$(date +%s)
    local elapsed=0
    local initial_count=0

    log_info "Watching directory: ${dir_path}"

    if [[ -d "${dir_path}" ]]; then
        initial_count=$(find "${dir_path}" -type f | wc -l)
        log_info "Initial file count: ${initial_count}"
    fi

    while [[ ${elapsed} -lt ${MAX_WAIT_TIME} ]]; do
        if [[ ! -d "${dir_path}" ]]; then
            log_info "Waiting for directory to appear... (${elapsed}/${MAX_WAIT_TIME}s)"
            sleep "${POLL_INTERVAL}"
            elapsed=$(( $(date +%s) - start_time ))
            continue
        fi

        current_count=$(find "${dir_path}" -type f | wc -l)

        if [[ ${current_count} -gt ${initial_count} ]]; then
            log_info "New files detected: ${current_count} (was ${initial_count})"
            return 0
        fi

        log_info "No new files yet... (${elapsed}/${MAX_WAIT_TIME}s)"
        sleep "${POLL_INTERVAL}"
        elapsed=$(( $(date +%s) - start_time ))
    done

    log_error "Timeout waiting for directory changes (${MAX_WAIT_TIME}s)"
    return 2
}

# Parse output
parse_output() {
    log_info "Parsing output with: ${PARSER_SCRIPT}"

    local parser_path="${SCRIPT_DIR}/${PARSER_SCRIPT}"

    if [[ ! -f "${parser_path}" ]]; then
        log_error "Parser script not found: ${parser_path}"
        return 1
    fi

    if [[ ! -x "${parser_path}" ]]; then
        chmod +x "${parser_path}"
    fi

    # Run parser
    if "${parser_path}" "${WATCH_PATH}" 2>&1 | tee -a "${LOG_FILE}" "${EXECUTION_LOG}"; then
        log_info "Parsing successful"
        return 0
    else
        log_error "Parsing failed"
        return 1
    fi
}

# Execute action
execute_action() {
    log_info "Executing action: ${ACTION_SCRIPT}"

    local action_path="${SCRIPT_DIR}/${ACTION_SCRIPT}"

    if [[ ! -f "${action_path}" ]]; then
        log_error "Action script not found: ${action_path}"
        return 1
    fi

    if [[ ! -x "${action_path}" ]]; then
        chmod +x "${action_path}"
    fi

    # Run action
    if "${action_path}" "${WATCH_PATH}" "${LOG_FILE}" 2>&1 | tee -a "${LOG_FILE}" "${EXECUTION_LOG}"; then
        log_info "Action successful"
        return 0
    else
        log_error "Action failed"
        return 1
    fi
}

# Update watcher status
update_status() {
    local status="$1"
    local timestamp=$(date -Iseconds)

    # Update config file
    local temp_config=$(mktemp)
    jq --arg status "${status}" \
       --arg timestamp "${timestamp}" \
       '.status = $status | .completed_at = $timestamp' \
       "${CONFIG_FILE}" > "${temp_config}"
    mv "${temp_config}" "${CONFIG_FILE}"

    # Update session state
    local session_state="${WATCHERS_DIR}/session_state.json"
    if [[ -f "${session_state}" ]]; then
        temp_config=$(mktemp)
        jq --arg watcher_id "${WATCHER_ID}" \
           --arg status "${status}" \
           --arg timestamp "${timestamp}" \
           '(.active_watchers[] | select(.watcher_id == $watcher_id)) |= (.status = $status | .completed_at = $timestamp)' \
           "${session_state}" > "${temp_config}"
        mv "${temp_config}" "${session_state}"
    fi
}

# Call hooks
call_hook() {
    local hook_name="$1"
    local hook_script="${CLAUDE_DIR}/hooks/${hook_name}.sh"

    if [[ -f "${hook_script}" && -x "${hook_script}" ]]; then
        log_info "Calling hook: ${hook_name}"
        "${hook_script}" "${WATCHER_ID}" "${CONFIG_FILE}" 2>&1 | tee -a "${LOG_FILE}" "${EXECUTION_LOG}"
    fi
}

# Main execution
main() {
    log_info "Starting watcher: ${WATCHER_ID}"
    log_info "Config: ${CONFIG_FILE}"

    # Validate configuration
    if ! validate_config; then
        update_status "failed"
        exit 1
    fi

    # Watch based on type
    watch_result=0
    case "${WATCH_TYPE}" in
        file)
            watch_file "${WATCH_PATH}" || watch_result=$?
            ;;
        process)
            watch_process || watch_result=$?
            ;;
        directory)
            watch_directory "${WATCH_PATH}" || watch_result=$?
            ;;
        *)
            log_error "Unknown watch type: ${WATCH_TYPE}"
            update_status "failed"
            exit 1
            ;;
    esac

    # Handle watch result
    if [[ ${watch_result} -eq 2 ]]; then
        log_error "Watch timed out"
        update_status "timeout"
        call_hook "on_watcher_fail"
        exit 2
    elif [[ ${watch_result} -ne 0 ]]; then
        log_error "Watch failed"
        update_status "failed"
        call_hook "on_watcher_fail"
        exit 1
    fi

    # Parse output
    if ! parse_output; then
        log_error "Parsing failed"
        update_status "failed"
        call_hook "on_watcher_fail"
        exit 1
    fi

    # Execute action
    if ! execute_action; then
        log_error "Action failed"
        update_status "failed"
        call_hook "on_watcher_fail"
        exit 1
    fi

    # Success
    log_info "Watcher completed successfully"
    update_status "completed"
    call_hook "on_watcher_complete"
    exit 0
}

# Run main
main
