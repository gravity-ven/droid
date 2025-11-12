#!/usr/bin/env python3
"""
Claude Autonomous Manager
Manages autonomous operations for ~/.claude directory
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/claude_autonomous_manager.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeAutonomousManager:
    """Manages autonomous operations for Claude directory"""
    
    def __init__(self):
        self.claude_path = Path(os.path.expanduser('~/.claude'))
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.config = self.load_config()
        
    def load_config(self):
        """Load Claude autonomous configuration"""
        default_config = {
            "auto_cleanup": True,
            "backup_enabled": True,
            "max_backups": 10,
            "cleanup_interval": 86400,  # 24 hours
            "stats_tracking": True,
            "health_checks": True,
            "auto_optimize": True,
            "sync_priority": "bidirectional"
        }
        
        config_file = self.factory_path / 'agents' / 'claude_autonomous_config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load Claude config: {e}")
        
        return default_config
    
    def run_autonomous_cycle(self):
        """Run complete autonomous management cycle"""
        logger.info("Starting Claude autonomous management cycle")
        
        operations_completed = 0
        
        # Directory maintenance
        if self.claude_path.exists():
            operations_completed += self.maintain_directory_structure()
            operations_completed += self.cleanup_old_files()
            operations_completed += self.optimize_performance()
            operations_completed += self.health_checks()
            operations_completed += self.sync_with_factory()
        else:
            logger.warning("Claude directory does not exist")
            self.claude_path.mkdir(parents=True, exist_ok=True)
            operations_completed += 1
        
        logger.info(f"Completed {operations_completed} autonomous operations")
        return operations_completed
    
    def maintain_directory_structure(self):
        """Maintain required Claude directory structure"""
        operations = 0
        
        required_dirs = [
            '.claude/hooks',
            '.claude/watchers', 
            '.claude/agents',
            '.claude/skills',
            'histories',
            'state',
            'backups',
            'stats',
            'todos'
        ]
        
        for dir_path in required_dirs:
            full_path = self.claude_path / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {full_path}")
                operations += 1
        
        return operations
    
    def cleanup_old_files(self):
        """Clean up old files and temporary data"""
        if not self.config["auto_cleanup"]:
            return 0
        
        operations = 0
        
        # Clean old backups
        backups_dir = self.claude_path / 'backups'
        if backups_dir.exists():
            cutoff_time = datetime.now() - timedelta(days=7)
            for backup_file in backups_dir.glob('*'):
                if backup_file.is_file():
                    mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if mtime < cutoff_time:
                        backup_file.unlink()
                        logger.info(f"Cleaned old backup: {backup_file.name}")
                        operations += 1
                        
            # Keep only max_backups recent files
            backup_files = sorted(
                backups_dir.glob('*'), 
                key=lambda x: x.stat().st_mtime, 
                reverse=True
            )
            if len(backup_files) > self.config["max_backups"]:
                for old_backup in backup_files[self.config["max_backups"]:]:
                    old_backup.unlink()
                    logger.info(f"Removed excess backup: {old_backup.name}")
                    operations += 1
        
        # Clean temporary files
        temp_patterns = ['*.tmp', '*.temp', '*.bak', '*.old']
        for pattern in temp_patterns:
            for temp_file in self.claude_path.rglob(pattern):
                if temp_file.is_file() and 'backups' not in str(temp_file):
                    temp_file.unlink()
                    logger.info(f"Cleaned temp file: {temp_file.name}")
                    operations += 1
        
        return operations
    
    def optimize_performance(self):
        """Optimize Claude configuration for performance"""
        if not self.config["auto_optimize"]:
            return 0
        
        operations = 0
        
        # Check and optimize settings.json
        settings_file = self.claude_path / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Add performance optimizations if missing
                optimizations = {
                    "cache_enabled": True,
                    "cache_size_mb": 100,
                    "log_level": "INFO",
                    "max_concurrent_operations": 3,
                    "sync_compression": True
                }
                
                settings_modified = False
                for key, value in optimizations.items():
                    if key not in settings:
                        settings[key] = value
                        settings_modified = True
                
                if settings_modified:
                    with open(settings_file, 'w') as f:
                        json.dump(settings, f, indent=2)
                    logger.info("Applied performance optimizations")
                    operations += 1
                    
            except Exception as e:
                logger.error(f"Failed to optimize settings: {e}")
        
        return operations
    
    def health_checks(self):
        """Perform system health checks"""
        if not self.config["health_checks"]:
            return 0
        
        operations = 0
        
        # Check directory permissions
        for root, dirs, files in os.walk(self.claude_path):
            for name in files:
                filepath = Path(root) / name
                if not os.access(filepath, os.R_OK) or not os.access(filepath, os.W_OK):
                    logger.warning(f"Permission issue: {filepath}")
        
        # Validate JSON files
        for json_file in self.claude_path.rglob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {json_file}: {e}")
                # Create backup of invalid file
                backup_file = json_file.with_suffix('.json.backup')
                json_file.rename(backup_file)
                operations += 1
        
        return operations
    
    def sync_with_factory(self):
        """Ensure sync with factory is active"""
        operations = 0
        
        # Check if sync daemon is running
        sync_pid_file = self.factory_path / 'logs' / 'claude_sync_daemon.pid'
        if sync_pid_file.exists():
            try:
                pid = int(sync_pid_file.read_text().strip())
                # Check if process is still running
                if os.path.exists(f'/proc/{pid}'):
                    operations += 1
                else:
                    # Restart sync daemon
                    subprocess.Popen([
                        'python3', str(self.factory_path / 'agents' / 'claude_factory_sync.py')
                    ])
                    logger.info("Restarted Claude-Factory sync daemon")
                    operations += 1
            except (ValueError, ProcessLookupError):
                # Restart sync daemon
                subprocess.Popen([
                    'python3', str(self.factory_path / 'agents' / 'claude_factory_sync.py')
                ])
                logger.info("Started Claude-Factory sync daemon")
                operations += 1
        else:
            # Start sync daemon
            subprocess.Popen([
                'python3', str(self.factory_path / 'agents' / 'claude_factory_sync.py')
            ])
            logger.info("Initialized Claude-Factory sync daemon")
            operations += 1
        
        return operations
    
    def generate_status_report(self):
        """Generate comprehensive Claude status report"""
        if not self.config["stats_tracking"]:
            return
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "directory_status": self.get_directory_status(),
            "sync_status": self.get_sync_status(),
            "health_status": self.get_health_status(),
            "optimizations": self.get_optimization_status()
        }
        
        # Save report
        report_file = self.claude_path / 'state' / 'status_report.json'
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def get_directory_status(self):
        """Get status of Claude directory structure"""
        status = {}
        for item in self.claude_path.iterdir():
            if item.is_dir():
                file_count = len([f for f in item.rglob('*') if f.is_file()])
                status[item.name] = {
                    "type": "directory",
                    "file_count": file_count
                }
            else:
                size = item.stat().st_size if item.exists() else 0
                status[item.name] = {
                    "type": "file",
                    "size_bytes": size
                }
        return status
    
    def get_sync_status(self):
        """Get sync status with factory"""
        sync_health_file = self.factory_path / 'claude_sync' / '.sync_healthy'
        if sync_health_file.exists():
            try:
                timestamp = sync_health_file.read_text().replace('healthy_', '')
                return {
                    "status": "active",
                    "last_health_check": timestamp,
                    "direction": self.config["sync_priority"]
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "unknown"}
    
    def get_health_status(self):
        """Get system health status"""
        issues = []
        
        # Check for permission issues
        if not os.access(self.claude_path, os.R_OK | os.W_OK):
            issues.append("Claude directory permission issues")
        
        # Check disk space
        stat = os.statvfs(self.claude_path)
        free_space_mb = (stat.f_bavail * stat.f_frsize) // (1024 * 1024)
        if free_space_mb < 100:  # Less than 100MB free
            issues.append("Low disk space")
        
        return {
            "status": "healthy" if not issues else "issues_found",
            "issues": issues,
            "free_space_mb": free_space_mb
        }
    
    def get_optimization_status(self):
        """Get optimization status"""
        settings_file = self.claude_path / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                optimizations = [
                    'cache_enabled',
                    'cache_size_mb', 
                    'log_level',
                    'max_concurrent_operations',
                    'sync_compression'
                ]
                
                optimized = sum(1 for opt in optimizations if opt in settings)
                return {
                    "status": "optimized" if optimized >= 3 else "partially_optimized",
                    "optimizations_applied": optimized,
                    "total_optimizations": len(optimizations)
                }
            except Exception:
                pass
        
        return {"status": "not_optimized"}

if __name__ == "__main__":
    manager = ClaudeAutonomousManager()
    
    # Run autonomous cycle
    operations = manager.run_autonomous_cycle()
    
    # Generate status report
    report = manager.generate_status_report()
    
    if report:
        logger.info(f"Status report generated with {len(report)} sections")
