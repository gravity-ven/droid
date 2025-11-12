#!/bin/bash
# Start auto-sync daemon for Droid settings

# Configuration
FACTORY_DIR="$HOME/.factory"
SYNC_SCRIPT="$FACTORY_DIR/scripts/auto_sync_github.py"
LOG_DIR="$FACTORY_DIR/logs"

# Ensure directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$FACTORY_DIR/scripts"

# Check if sync script exists
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "Auto-sync script not found at: $SYNC_SCRIPT"
    exit 1
fi

# Make executable
chmod +x "$SYNC_SCRIPT"

# Start auto-sync with logging
echo "Starting Droid settings auto-sync daemon..."
echo "Log file: $LOG_DIR/auto_sync.log"

# Check if already running
if pgrep -f "auto_sync_github.py" > /dev/null; then
    echo "Auto-sync daemon is already running"
    echo "PID: $(pgrep -f 'auto_sync_github.py')"
    exit 1
fi

# Start daemon
nohup python3 "$SYNC_SCRIPT" --daemon >> "$LOG_DIR/auto_sync.log" 2>&1 &

# Check if started successfully
sleep 2
if pgrep -f "auto_sync_github.py" > /dev/null; then
    echo "Auto-sync daemon started successfully"
    echo "PID: $(pgrep -f 'auto_sync_github.py')"
    echo "To stop: pkill -f 'auto_sync_github.py'"
    echo "To check status: python3 $SYNC_SCRIPT --status"
else
    echo "Failed to start auto-sync daemon"
    echo "Check log: $LOG_DIR/auto_sync.log"
    exit 1
fi

# Initial sync attempt
echo "Attempting initial sync..."
python3 "$SYNC_SCRIPT" --sync

exit 0
