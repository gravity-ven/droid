#!/bin/bash
# Start Claude-Factory bidirectional sync
python3 "$HOME/.factory/agents/claude_factory_sync.py" &
DAEMON_PID=$!
echo "Started Claude-Factory sync daemon with PID: $DAEMON_PID"
echo $DAEMON_PID > "$HOME/.factory/logs/claude_sync_daemon.pid"
