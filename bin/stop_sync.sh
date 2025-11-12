#!/bin/bash
# Stop the sync daemon
if [ -f "$HOME/.factory/logs/sync_daemon.pid" ]; then
    PID=$(cat "$HOME/.factory/logs/sync_daemon.pid")
    kill $PID 2>/dev/null
    rm "$HOME/.factory/logs/sync_daemon.pid"
    echo "Stopped sync daemon (PID: $PID)"
else
    echo "Sync daemon not running"
fi
