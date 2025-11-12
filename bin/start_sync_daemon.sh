#!/bin/bash
# Start the Claude auto-sync daemon
python3 "$HOME/.factory/agents/auto_sync_daemon.py" &
DAEMON_PID=$!
echo "Started sync daemon with PID: $DAEMON_PID"
echo $DAEMON_PID > "$HOME/.factory/logs/sync_daemon.pid"
