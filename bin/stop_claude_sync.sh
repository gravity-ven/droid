#!/bin/bash
# Stop Claude-Factory sync daemon
if [ -f "$HOME/.factory/logs/claude_sync_daemon.pid" ]; then
    PID=$(cat "$HOME/.factory/logs/claude_sync_daemon.pid")
    kill $PID 2>/dev/null
    rm "$HOME/.factory/logs/claude_sync_daemon.pid"
    echo "Stopped Claude-Factory sync daemon (PID: $PID)"
else
    echo "Claude-Factory sync daemon not running"
fi
