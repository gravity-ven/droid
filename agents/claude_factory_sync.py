#!/usr/bin/env python3
"""
Claude-Factory Bidirectional Sync Daemon
Keeps ~/.claude and ~/.factory synchronized in real-time
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
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/claude_factory_sync.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeToFactoryHandler(FileSystemEventHandler):
    """Handles sync from ~/.claude to ~/.factory"""
    
    def __init__(self, claude_path, factory_path):
        self.claude_path = Path(claude_path)
        self.factory_path = Path(factory_path)
        self.sync_delay = 2
        
    def on_modified(self, event):
        if event.is_directory:
            return
        self.sync_event(event, "C->F")
    
    def on_created(self, event):
        if event.is_directory:
            return
        self.sync_event(event, "C->F")
    
    def sync_event(self, event, direction):
        time.sleep(self.sync_delay)
        
        try:
            source = Path(event.src_path)
            
            # Ignore certain patterns
            if any(pattern in str(source) for pattern in ['.DS_Store', '__pycache__', '.pyc', '.log']):
                return
            
            claude_rel = source.relative_to(self.claude_path)
            logger.info(f"[{direction}] Change detected: {claude_rel}")
            
            # Determine sync mapping
            if claude_rel.name == 'settings.json':
                self.sync_settings(source, direction)
            elif claude_rel.name.endswith('.sh') and 'hooks' in str(claude_rel):
                self.sync_shell_script(source, direction)
            elif claude_rel.name.endswith('.py') and 'agents' in str(claude_rel):
                self.sync_agent(source, direction)
            else:
                self.sync_file(source, direction)
                
        except Exception as e:
            logger.error(f"Sync error [{direction}]: {e}")
    
    def sync_settings(self, source, direction):
        """Sync settings with intelligent merging"""
        try:
            factory_settings = self.factory_path / 'settings.json'
            
            with open(source, 'r') as f:
                claude_settings = json.load(f)
            
            if not factory_settings.exists():
                # Initialize factory settings if missing
                with open(factory_settings, 'w') as f:
                    json.dump(claude_settings, f, indent=2)
            else:
                # Merge with existing factory settings
                with open(factory_settings, 'r') as f:
                    factory_data = json.load(f)
                
                # Add Claude integration section
                if 'claudeIntegration' not in factory_data:
                    factory_data['claudeIntegration'] = {}
                factory_data['claudeIntegration'].update(claude_settings)
                
                with open(factory_settings, 'w') as f:
                    json.dump(factory_data, f, indent=2)
            
            logger.info(f"[C->F] Settings merged successfully")
        except Exception as e:
            logger.error(f"[C->F] Settings sync failed: {e}")
    
    def sync_shell_script(self, source, direction):
        """Sync shell scripts to droids directory"""
        target = self.factory_path / 'droids' / source.name
        self.copy_file(source, target, direction)
        os.chmod(target, 0o755)
    
    def sync_agent(self, source, direction):
        """Sync agent files"""
        target = self.factory_path / 'agents' / source.name
        self.copy_file(source, target, direction)
        os.chmod(target, 0o755)
    
    def sync_file(self, source, direction):
        """General file sync"""
        claude_rel = source.relative_to(self.claude_path)
        target = self.factory_path / 'claude_sync' / claude_rel
        self.copy_file(source, target, direction)
    
    def copy_file(self, source, target, direction):
        """Copy file with directory creation"""
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        logger.info(f"[{direction}] Synced: {target}")

class FactoryToClaudeHandler(FileSystemEventHandler):
    """Handles sync from ~/.factory to ~/.claude"""
    
    def __init__(self, factory_path, claude_path):
        self.factory_path = Path(factory_path)
        self.claude_path = Path(claude_path)
        self.sync_delay = 2
        
    def on_modified(self, event):
        if event.is_directory:
            return
        self.sync_event(event, "F->C")
    
    def on_created(self, event):
        if event.is_directory:
            return
        self.sync_event(event, "F->C")
    
    def sync_event(self, event, direction):
        time.sleep(self.sync_delay)
        
        try:
            source = Path(event.src_path)
            
            # Only sync critical factory files to Claude
            if not any(pattern in str(source) for pattern in [
                'agents/', 'droids/', 'watchers/', 
                'settings.json'
            ]):
                return
            
            # Ignore Claude sync directory to prevent loops
            if 'claude_sync' in str(source):
                return
            
            factory_rel = source.relative_to(self.factory_path)
            logger.info(f"[{direction}] Change detected: {factory_rel}")
            
            if factory_rel.name == 'settings.json':
                self.sync_settings_to_claude(source, direction)
            elif source.name.endswith('.sh') and 'droids' in str(factory_rel):
                self.sync_script_to_claude(source, direction)
            elif source.name.endswith('.py') and 'agents' in str(factory_rel):
                self.sync_agent_to_claude(source, direction)
                
        except Exception as e:
            logger.error(f"Sync error [{direction}]: {e}")
    
    def sync_settings_to_claude(self, source, direction):
        """Extract Claude settings from factory settings"""
        try:
            with open(source, 'r') as f:
                factory_data = json.load(f)
            
            # Extract Claude integration settings
            claude_settings = factory_data.get('claudeIntegration', {})
            
            if claude_settings:
                target = self.claude_path / 'settings.json'
                with open(target, 'w') as f:
                    json.dump(claude_settings, f, indent=2)
                
                logger.info(f"[F->C] Claude settings synced")
        except Exception as e:
            logger.error(f"[F->C] Settings sync failed: {e}")
    
    def sync_script_to_claude(self, source, direction):
        """Sync scripts to Claude hooks directory"""
        if not any(script in source.name for script in ['orchestrator', 'startup', 'sync']):
            return
            
        hooks_dir = self.claude_path / '.claude' / 'hooks'
        hooks_dir.mkdir(parents=True, exist_ok=True)
        target = hooks_dir / source.name
        
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        os.chmod(target, 0o755)
        
        logger.info(f"[F->C] Script synced: {source.name}")
    
    def sync_agent_to_claude(self, source, direction):
        """Sync agents to Claude directory"""
        target = self.claude_path / 'agents' / source.name
        self.copy_file(source, target, direction)
    
    def copy_file(self, source, target, direction):
        """Copy file with directory creation"""
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        logger.info(f"[{direction}] Synced: {target}")

class ClaudeFactorySyncDaemon:
    """Main daemon for Claude-Factory bidirectional sync"""
    
    def __init__(self):
        self.claude_path = Path(os.path.expanduser('~/.claude'))
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.observers = []
        
    def start_monitoring(self):
        """Start both directions of monitoring"""
        logger.info("Starting Claude-Factory bidirectional sync")
        
        # Ensure directories exist
        self.claude_path.mkdir(exist_ok=True)
        self.factory_path.mkdir(exist_ok=True)
        (self.factory_path / 'claude_sync').mkdir(exist_ok=True)
        
        # Monitor Claude -> Factory
        try:
            if self.claude_path.exists():
                c_to_f_observer = Observer()
                c_handler = ClaudeToFactoryHandler(self.claude_path, self.factory_path)
                c_to_f_observer.schedule(c_handler, str(self.claude_path), recursive=True)
                c_to_f_observer.start()
                self.observers.append(c_to_f_observer)
                logger.info(f"Started monitoring {self.claude_path} -> {self.factory_path}")
        except Exception as e:
            logger.error(f"Failed to start Claude->Factory monitoring: {e}")
        
        # Monitor Factory -> Claude
        try:
            f_to_c_observer = Observer()
            f_handler = FactoryToClaudeHandler(self.factory_path, self.claude_path)
            f_to_c_observer.schedule(f_handler, str(self.factory_path), recursive=True)
            f_to_c_observer.start()
            self.observers.append(f_to_c_observer)
            logger.info(f"Started monitoring {self.factory_path} -> {self.claude_path}")
        except Exception as e:
            logger.error(f"Failed to start Factory->Claude monitoring: {e}")
        
        return len(self.observers) > 0
    
    def run_sync_daemon(self):
        """Main daemon loop"""
        if not self.start_monitoring():
            logger.error("Failed to start monitoring")
            return
        
        logger.info("Claude-Factory bidirectional sync started successfully")
        
        try:
            while True:
                time.sleep(10)
                # Periodic health check
                self.health_check()
                
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            for observer in self.observers:
                observer.stop()
                observer.join()
    
    def health_check(self):
        """Periodic health check of sync system"""
        try:
            # Check if both directories are accessible
            if not self.claude_path.exists():
                logger.warning("Claude directory not accessible")
            if not self.factory_path.exists():
                logger.warning("Factory directory not accessible")
                
            # Check sync health
            sync_file = self.factory_path / 'claude_sync' / '.sync_healthy'
            sync_file.write_text(f'healthy_{datetime.now().isoformat()}')
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")

if __name__ == "__main__":
    daemon = ClaudeFactorySyncDaemon()
    daemon.run_sync_daemon()
