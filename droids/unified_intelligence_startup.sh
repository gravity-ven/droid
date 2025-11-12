#!/bin/bash
# Unified Intelligence Startup Hook
# Runs at session start to initialize intelligence systems

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize intelligence systems
echo -e "${GREEN}⚡ Initializing Intelligence Systems...${NC}"

# Check for agent system
AGENT_DIR="$HOME/.claude/agents"
if [ -d "$AGENT_DIR" ]; then
    AGENT_COUNT=$(find "$AGENT_DIR" -maxdepth 1 -type f -name "*.py" | wc -l)
    echo -e "${GREEN}✓ Agent System: $AGENT_COUNT agents available${NC}"
fi

# Check for MCP servers
if command -v python3 &> /dev/null; then
    # Check if meta-orchestrator is available
    if [ -f "$HOME/.claude/agents/meta_orchestrator_server.py" ]; then
        echo -e "${GREEN}✓ Meta-Orchestrator: Ready${NC}"
    fi

    # Check if autonomous systems are available
    if [ -f "$HOME/.claude/autonomous_orchestrator.py" ]; then
        echo -e "${GREEN}✓ Autonomous Systems: Available${NC}"
    fi
fi

# Check for skills
SKILLS_DIR="$HOME/.claude/skills"
if [ -d "$SKILLS_DIR" ]; then
    SKILL_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -type d ! -name skills | wc -l)
    echo -e "${GREEN}✓ Skills: $SKILL_COUNT loaded${NC}"
fi

echo -e "${GREEN}⚡ Intelligence Systems: ONLINE${NC}"

exit 0
