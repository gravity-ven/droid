#!/bin/bash
#
# Sync Watcher System to GitHub
#
# Synchronizes the local watcher system with the GitHub repository.
#

set -euo pipefail

# Paths
LOCAL_WATCHERS_DIR="${HOME}/.claude/watchers"
LOCAL_HOOKS_DIR="${HOME}/.claude/hooks"
LOCAL_IMPL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_DIR="${HOME}/Documents/GitHub/Claude_Code/watcher-system"

# Logging
log() {
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] ${message}"
}

log "Starting sync to GitHub..."

# Ensure GitHub directory exists
mkdir -p "${GITHUB_DIR}"/{.claude/{watchers,hooks,state},watchers/logs}

# Sync watchers config and session manager
log "Syncing watchers configuration..."
cp -r "${LOCAL_WATCHERS_DIR}"/* "${GITHUB_DIR}/.claude/watchers/" 2>/dev/null || true

# Don't sync session state (it's runtime state)
rm -f "${GITHUB_DIR}/.claude/watchers/session_state.json"

# Create placeholder for state
cat > "${GITHUB_DIR}/.claude/watchers/session_state.json" << 'EOF'
{
  "active_watchers": [],
  "completed_watchers": [],
  "session_start": null,
  "session_end": null
}
EOF

# Sync hooks
log "Syncing hooks..."
cp -r "${LOCAL_HOOKS_DIR}"/* "${GITHUB_DIR}/.claude/hooks/" 2>/dev/null || true

# Sync watcher implementation
log "Syncing watcher implementation..."
cp "${LOCAL_IMPL_DIR}"/*.sh "${GITHUB_DIR}/watchers/" 2>/dev/null || true
cp "${LOCAL_IMPL_DIR}"/*.py "${GITHUB_DIR}/watchers/" 2>/dev/null || true

# Preserve executable permissions
chmod +x "${GITHUB_DIR}/.claude/watchers/session_manager.py"
chmod +x "${GITHUB_DIR}/.claude/hooks"/*.sh
chmod +x "${GITHUB_DIR}/watchers"/*.sh
chmod +x "${GITHUB_DIR}/watchers"/*.py

# Create .gitignore
cat > "${GITHUB_DIR}/.gitignore" << 'EOF'
# Runtime state
.claude/state/
.claude/watchers/session_state.json
watchers/logs/

# Watcher config files (may contain sensitive paths)
.claude/watchers/watcher_*.json

# Parsed output files
*.parsed.json

# Log files
*.log
EOF

log "Sync completed successfully!"
log "GitHub directory: ${GITHUB_DIR}"

# Show what was synced
log "Synced files:"
find "${GITHUB_DIR}" -type f -name "*.py" -o -name "*.sh" -o -name "*.json" | sort
