#!/usr/bin/env python3
"""
Auto-Sync Daemon for Claude-Droid Integration
Monitors Claude repository and syncs changes automatically
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/auto_sync.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeSyncHandler(FileSystemEventHandler):
    """Handles file system events for auto-sync"""
    
    def __init__(self, claude_repo_path, factory_path, config):
        self.claude_repo = Path(claude_repo_path)
        self.factory_path = Path(factory_path)
        self.config = config
        self.last_sync = {}
        self.sync_delay = 2  # Delay in seconds before syncing
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Ignore certain files and directories
        if any(pattern in str(event.src_path) for pattern in ['.git/', '__pycache__', '.pyc', '.log']):
            return
            
        # Get relative path within claude repo
        try:
            rel_path = Path(event.src_path).relative_to(self.claude_repo)
            logger.info(f"Change detected: {rel_path}")
            
            # Schedule sync with delay
            time.sleep(self.sync_delay)
            self.sync_file_to_factory(rel_path)
            
        except ValueError:
            # File is outside claude repo
            return
    
    def sync_file_to_factory(self, rel_path):
        """Sync a file from Claude repo to Factory config"""
        source = self.claude_repo / rel_path
        target = self.factory_path / 'claude_sync' / rel_path
        
        # Determine sync target based on file type
        if rel_path.name.endswith('.sh') and 'hooks' in str(rel_path):
            target = self.factory_path / 'droids' / rel_path.name
        elif rel_path.name.endswith('.py') and 'watchers' in str(rel_path):
            target = self.factory_path / 'watchers' / rel_path.name
        elif 'settings' in str(rel_path) and rel_path.name.endswith('.json'):
            self.merge_settings(source)
            return
        elif rel_path.name == 'auto_sync_settings.sh':
            target = self.factory_path / 'droids' / rel_path.name
        else:
            target = self.factory_path / 'claude_sync' / rel_path
            
        try:
            # Create target directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if source.is_file():
                shutil.copy2(source, target)
                logger.info(f"Synced: {rel_path} -> {target}")
                
                # Make script files executable
                if target.name.endswith('.sh'):
                    os.chmod(target, 0o755)
                    
        except Exception as e:
            logger.error(f"Failed to sync {rel_path}: {e}")
    
    def merge_settings(self, source):
        """Merge Claude settings with Factory settings"""
        try:
            with open(source, 'r') as f:
                claude_settings = json.load(f)
            
            factory_settings_file = self.factory_path / 'settings.json'
            with open(factory_settings_file, 'r') as f:
                factory_settings = json.load(f)
            
            # Merge Claude settings
            if 'claudeIntegration' not in factory_settings:
                factory_settings['claudeIntegration'] = {}
            
            factory_settings['claudeIntegration'].update(claude_settings)
            
            # Write merged settings
            with open(factory_settings_file, 'w') as f:
                json.dump(factory_settings, f, indent=2)
                
            logger.info("Merged Claude settings with Factory settings")
            
        except Exception as e:
            logger.error(f"Failed to merge settings: {e}")

class AutoSyncDaemon:
    """Main auto-sync daemon"""
    
    def __init__(self):
        self.config = self.load_config()
        self.claude_repo = Path(os.path.expanduser('~/Desktop/claude-repos/Claude_Code'))
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.observer = None
        
    def load_config(self):
        """Load daemon configuration"""
        default_config = {
            "sync_interval": 30,  # seconds
            "git_sync_interval": 300,  # 5 minutes
            "auto_commit": True,
            "auto_push": False,  # Requires manual auth setup
            "backup_enabled": True,
            "max_backups": 10
        }
        
        config_file = Path(os.path.expanduser('~/.factory/agents/sync_config.json'))
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def start_monitoring(self):
        """Start file system monitoring"""
        if not self.claude_repo.exists():
            logger.error(f"Claude repo not found: {self.claude_repo}")
            return False
            
        event_handler = ClaudeSyncHandler(self.claude_repo, self.factory_path, self.config)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.claude_repo), recursive=True)
        self.observer.start()
        
        logger.info(f"Started monitoring {self.claude_repo}")
        return True
    
    def sync_git_changes(self):
        """Auto-sync Git changes"""
        try:
            # Pull latest changes from remote
            subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.claude_repo,
                capture_output=True,
                text=True
            )
            
            # Check for changes to commit
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.claude_repo,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip() and self.config['auto_commit']:
                # Add and commit changes
                subprocess.run(['git', 'add', '.'], cwd=self.claude_repo)
                commit_msg = f"Auto-sync update {datetime.now().isoformat()}"
                subprocess.run(['git', 'commit', '-m', commit_msg], cwd=self.claude_repo)
                
                if self.config['auto_push']:
                    subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.claude_repo)
                    
                logger.info("Auto-committed changes to Git")
                
        except Exception as e:
            logger.error(f"Git sync failed: {e}")
    
    def run_daemon(self):
        """Main daemon loop"""
        logger.info("Auto-sync daemon started")
        
        if not self.start_monitoring():
            return
        
        last_git_sync = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Periodic Git sync
                if current_time - last_git_sync > self.config['git_sync_interval']:
                    self.sync_git_changes()
                    last_git_sync = current_time
                
                time.sleep(self.config['sync_interval'])
                
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()

if __name__ == "__main__":
    daemon = AutoSyncDaemon()
    daemon.run_daemon()
