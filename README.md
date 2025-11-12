# Droid Settings Repository

This repository contains the complete configuration and agent system for the Factory Droid CLI with intelligent task routing, cross-agent knowledge sharing, and auto-sync capabilities.

## 🚀 Features

### Core Intelligence Systems
- **Enhanced Meta-Orchestrator**: Intelligent task routing with performance-based agent selection
- **Cross-Agent Knowledge Sharing**: Automatic learning transfer between agents
- **Nested Learning Manager**: Continual learning without catastrophic forgetting
- **TOON Integration**: Token optimization (30-60% reduction) for efficient communications
- **Parallel Task Scheduler**: Advanced concurrent execution with resource management

### Agent Capabilities
- **22 Specialized Agents** with task-specific expertise
- **Dynamic Load Balancing** across available agents
- **Performance Monitoring** with real-time metrics
- **Adaptive Learning** from task results and user feedback
- **Fault Tolerance** with automatic recovery mechanisms

### Auto-Sync Features
- **GitHub Integration**: Automatic synchronization of configurations
- **Version Control**: Complete history of all agent configurations
- **Cross-Environment Consistency**: Settings sync across multiple systems
- **Rollback Capability**: Easy reversion to previous configurations

## 📁 Configuration Structure

```
~/.factory/
├── agents/                    # Agent system files
│   ├── enhanced_meta_orchestrator.py
│   ├── nested_learning_manager.py
│   ├── parallel_task_scheduler.py
│   ├── toon_core_system.py
│   └── [18 more agents...]
├── settings.json             # Main configuration
├── agents/                    # Agent configurations
├── watchers/                  # File monitoring system
├── logs/                      # System logs
└── skills/                    # Skill configurations
```

## 🤖 Agent System Overview

### Core Agents
1. **Enhanced Meta-Orchestrator** - Intelligent task routing and coordination
2. **Nested Learning Manager** - Knowledge accumulation and pattern recognition
3. **Parallel Task Scheduler** - Concurrent execution and resource management
4. **TOON Core System** - Token optimization and format conversion
5. **Mojo Integration Agent** - Performance analysis and optimization

### Supporting Agents
- **File Operations Agent** - File system management and operations
- **Code Generation Agent** - Automated code creation and analysis
- **Tool Executor Agent** - Command execution and process management
- **Integration Agents** - External system connections and data flow

## ⚙️ Key Settings

### TOON Configuration
```json
"toonIntegration": {
  "enabled": true,
  "coreSystem": true,
  "autoConvert": true,
  "minSavingsPercent": 15,
  "tokenAware": true,
  "intelligentTruncation": true,
  "agentInterception": true,
  "nestedLearning": true
}
```

### Auto-Sync Configuration
```json
"cloudSessionSync": true,
"claudeIntegration": {
  "enabled": true,
  "watcherSystem": {"enabled": true},
  "agents": {"enabled": true},
  "skills": {"enabled": true}
}
```

### Security Settings
```json
"commandAllowlist": ["ls", "pwd", "python3", "python"],
"commandDenylist": ["rm -rf /*", "shutdown", "reboot"],
"enableCustomDroids": true,
"enableDroidShield": true
```

## 🔄 Auto-Sync Setup

The system automatically synchronizes configuration changes to this GitHub repository:

### Setup Commands
```bash
# Initialize auto-sync
cd ~/.factory
git remote add origin https://github.com/gravity-ven/Droid_Settings.git
git branch -M main
git push -u origin main
```

### Sync Operations
```bash
# Manual sync to GitHub
cd ~/.factory && git add . && git commit -m "Auto-sync configuration updates" && git push

# Pull latest changes from GitHub
cd ~/.factory && git pull origin main
```

## 📊 Performance Monitoring

### Real-Time Metrics
- **Total Tasks**: {routing_stats['total_tasks']}
- **Success Rate**: {routing_stats['successful_routes'] / total_tasks}
- **Active Agents**: {count of registered agents}
- **Knowledge Transfers**: {routing_stats['knowledge_transfers']}

### Performance Reports
```bash
# Get current orchestrator status
python agents/enhanced_meta_orchestrator.py

# View agent performance metrics
python agents/parallel_task_scheduler.py
```

## 🛠️ Integrations

### Claude Code
- **Watcher System**: Monitors Claude Code output for task completion
- **Parser Scripts**: Extract structured data from Claude responses
- **Action Scripts**: Handle task results and trigger follow-ups

### GitHub
- **Version Control**: Complete configuration history
- **Backup System**: Automatic configuration backups
- **Rollback**: Revert to previous working configurations

### TOON Format
- **Token Optimization**: 30-60% reduction in token usage
- **Intelligent Conversion**: Automatic format detection and conversion
- **Context Compression**: Efficient storage of large contexts

## 🔐 Security

### Command Filtering
- **Allowlist**: Commands that execute without confirmation
- **Denylist**: Dangerous commands that always require confirmation
- **Risk Assessment**: Dynamic evaluation based on context

### Data Protection
- **Tokenization**: Sensitive data protection in communications
- **Encryption**: Secure storage of configuration secrets
- **Audit Trails**: Complete tracking of all system actions

## 📝 Version History

- **v1.0**: Initial setup with basic agents
- **v2.0**: Enhanced meta-orchestrator with intelligent routing
- **v2.1**: Cross-agent knowledge sharing implementation
- **v2.2**: TOON integration and token optimization
- **v2.3**: Auto-sync and GitHub integration
- **v2.4**: Real-time performance monitoring
- **v3.0**: Complete agent ecosystem with 22 specialized agents

## 🚧 Development

### Adding New Agents
1. Create agent file in `/Users/spartan/.factory/agents/`
2. Define agent capabilities and supported tasks
3. Register with meta-orchestrator
4. Add to configuration
5. Commit to repository

### Testing Changes
```bash
# Test new agent
python agents/enhanced_meta_orchestrator.py

# Monitor performance
python agents/performance_monitor.py

# Sync changes
git add . && git commit -m "Add new agent" && git push
```

## 📄 License

This repository contains configuration files for the Factory Droid CLI system. The configurations are designed to work with Factory's intelligent agent system.

---

*Last updated: {current_date}*  
*Maintained by: Factory Droid System*  
*Auto-sync enabled: Yes*
