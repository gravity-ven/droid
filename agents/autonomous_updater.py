#!/usr/bin/env python3
"""
Autonomous Updater System
Proactively updates and maintains the Claude-Droid integration
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/autonomous_updates.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousUpdater:
    """Handles autonomous updates for Claude-Droid system"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.claude_repo = Path(os.path.expanduser('~/Desktop/claude-repos/Claude_Code'))
        self.last_updates = self.load_update_history()
        
    def load_update_history(self):
        """Load history of last updates"""
        history_file = self.factory_path / 'logs' / 'update_history.json'
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load update history: {e}")
        return {}
    
    def save_update_history(self):
        """Save update history"""
        history_file = self.factory_path / 'logs' / 'update_history.json'
        try:
            history_file.parent.mkdir(exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(self.last_updates, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save update history: {e}")
    
    def check_for_updates(self):
        """Check for available updates"""
        updates = {
            "repository_updates": self.check_repository_updates(),
            "dependency_updates": self.check_dependencies(),
            "configuration_updates": self.check_configuration_updates(),
            "security_updates": self.check_security_updates()
        }
        
        return updates
    
    def check_repository_updates(self):
        """Check for repository updates"""
        try:
            if not self.claude_repo.exists():
                return {"status": "error", "message": "Repository not found"}
            
            # Get current commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.claude_repo,
                capture_output=True,
                text=True
            )
            current_commit = result.stdout.strip()
            
            # Fetch latest changes
            subprocess.run(['git', 'fetch', 'origin'], cwd=self.claude_repo, capture_output=True)
            
            # Get latest remote commit
            result = subprocess.run(
                ['git', 'rev-parse', 'origin/main'],
                cwd=self.claude_repo,
                capture_output=True,
                text=True
            )
            latest_commit = result.stdout.strip()
            
            if current_commit != latest_commit:
                commits_behind = subprocess.run(
                    ['git', 'rev-list', '--count', f'{current_commit}..{latest_commit}'],
                    cwd=self.claude_repo,
                    capture_output=True,
                    text=True
                )
                count = int(commits_behind.stdout.strip())
                
                return {
                    "status": "available",
                    "commits_behind": count,
                    "current_commit": current_commit[:8],
                    "latest_commit": latest_commit[:8]
                }
            
            return {"status": "current"}
            
        except Exception as e:
            logger.error(f"Failed to check repository updates: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_dependencies(self):
        """Check for dependency updates"""
        updates = []
        
        # Check Python packages
        try:
            result = subprocess.run(
                ['pip3', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                for pkg in outdated:
                    updates.append({
                        "type": "python_package",
                        "name": pkg['name'],
                        "current": pkg['version'],
                        "latest": pkg['latest_version']
                    })
        except Exception as e:
            logger.warning(f"Failed to check Python packages: {e}")
        
        return updates
    
    def check_configuration_updates(self):
        """Check for configuration updates"""
        config_updates = []
        
        # Compare current config with defaults
        default_config = self.get_default_settings()
        current_config_file = self.factory_path / 'settings.json'
        
        if current_config_file.exists():
            try:
                with open(current_config_file, 'r') as f:
                    current_config = json.load(f)
                
                # Check for missing default settings
                for key, value in default_config.items():
                    if key not in current_config:
                        config_updates.append({
                            "type": "missing_setting",
                            "key": key,
                            "default_value": value
                        })
            except Exception as e:
                logger.error(f"Failed to check configuration: {e}")
        
        return config_updates
    
    def check_security_updates(self):
        """Check for security-related updates"""
        security_updates = []
        
        # Check for outdated security-related configs
        settings_file = self.factory_path / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Check commandDenylist for completeness
                if 'commandDenylist' in settings:
                    denylist = settings['commandDenylist']
                    
                    # Check for dangerous commands that might be missing
                    dangerous_commands = [
                        'sudo rm -rf',
                        'chmod +x /bin/',
                        'curl | sudo sh',
                        'wget -O - | sudo sh'
                    ]
                    
                    for cmd in dangerous_commands:
                        if not any(cmd in denied for denied in denylist):
                            security_updates.append({
                                "type": "missing_denied_command",
                                "command": cmd,
                                "severity": "high"
                            })
            except Exception as e:
                logger.error(f"Failed security check: {e}")
        
        return security_updates
    
    def get_default_settings(self):
        """Get default factory settings"""
        return {
            "model": "glm-4.6",
            "reasoningEffort": "none",
            "cloudSessionSync": True,
            "diffMode": "github",
            "autonomyMode": "auto-high",
            "enableCustomDroids": True,
            "includeCoAuthoredByDroid": True,
            "enableDroidShield": True,
            "enableReadinessReport": False,
            "todoDisplayMode": "pinned"
        }
    
    def apply_updates(self, updates):
        """Apply available updates"""
        applied = []
        
        # Apply repository updates
        if updates["repository_updates"]["status"] == "available":
            result = self.update_repository()
            if result:
                applied.append({
                    "type": "repository",
                    "status": "success",
                    "commits": updates["repository_updates"]["commits_behind"]
                })
        
        # Apply dependency updates
        for dep in updates["dependency_updates"]:
            result = self.update_dependency(dep)
            if result:
                applied.append({
                    "type": "dependency",
                    "package": dep["name"],
                    "status": "success"
                })
        
        # Apply configuration updates
        for config in updates["configuration_updates"]:
            result = self.update_configuration(config)
            if result:
                applied.append({
                    "type": "configuration",
                    "setting": config["key"],
                    "status": "success"
                })
        
        # Apply security updates
        for security in updates["security_updates"]:
            result = self.update_security(security)
            if result:
                applied.append({
                    "type": "security",
                    "command": security["command"],
                    "status": "success"
                })
        
        return applied
    
    def update_repository(self):
        """Update repository to latest"""
        try:
            # Reset any local changes
            subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=self.claude_repo, capture_output=True)
            
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.claude_repo,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Repository updated successfully")
                return True
            else:
                logger.error(f"Repository update failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update repository: {e}")
            return False
    
    def update_dependency(self, dependency):
        """Update a specific dependency"""
        try:
            if dependency["type"] == "python_package":
                result = subprocess.run(
                    ['pip3', 'install', '--upgrade', dependency["name"]],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to update {dependency['name']}: {e}")
        return False
    
    def update_configuration(self, config):
        """Update configuration setting"""
        try:
            settings_file = self.factory_path / 'settings.json'
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            settings[config["key"]] = config["default_value"]
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Added configuration: {config['key']}")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def update_security(self, security):
        """Update security settings"""
        try:
            settings_file = self.factory_path / 'settings.json'
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            if "commandDenylist" not in settings:
                settings["commandDenylist"] = []
            
            settings["commandDenylist"].append(security["command"])
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Added security block: {security['command']}")
            return True
        except Exception as e:
            logger.error(f"Failed to update security: {e}")
            return False
    
    def run_autonomous_cycle(self):
        """Run one complete autonomous update cycle"""
        logger.info("Starting autonomous update cycle")
        
        # Check for updates
        updates = self.check_for_updates()
        
        # Count total updates available
        total_updates = (
            1 if updates["repository_updates"]["status"] == "available" else 0
        ) + len(updates["dependency_updates"]) + len(updates["configuration_updates"]) + len(updates["security_updates"])
        
        if total_updates > 0:
            logger.info(f"Found {total_updates} updates available")
            
            # Apply updates
            applied = self.apply_updates(updates)
            
            # Save update history
            timestamp = datetime.now().isoformat()
            self.last_updates[timestamp] = {
                "checked": updates,
                "applied": applied
            }
            self.save_update_history()
            
            logger.info(f"Applied {len(applied)} updates")
        else:
            logger.info("No updates available")
        
        return total_updates

if __name__ == "__main__":
    updater = AutonomousUpdater()
    
    # Run single cycle
    updater.run_autonomous_cycle()
