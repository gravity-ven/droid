#!/usr/bin/env python3
"""
Auto-Sync Script for Droid Settings to GitHub
Handles synchronization with retry logic and error handling
"""

import os
import subprocess
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/auto_sync.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DroidGitHubSync:
    """Handles synchronization of Droid settings to GitHub"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.repo_url = "https://github.com/gravity-ven/Droid_Settings.git"
        self.sync_config_file = self.factory_path / ".sync_config.json"
        self.max_retries = 3
        self.retry_delay = 30
        
    def load_sync_config(self):
        """Load sync configuration"""
        default_config = {
            "enabled": True,
            "auto_commit": True,
            "commit_prefix": "Auto-sync",
            "sync_interval": 300,  # 5 minutes
            "last_sync": None,
            "retry_count": 0
        }
        
        if self.sync_config_file.exists():
            try:
                with open(self.sync_config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Failed to load sync config: {e}")
        
        return default_config
    
    def save_sync_config(self, config):
        """Save sync configuration"""
        try:
            with open(self.sync_config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sync config: {e}")
    
    def execute_git_command(self, command, timeout=180):
        """Execute git command with timeout and retry logic"""
        for attempt in range(self.max_retries):
            try:
                os.chdir(self.factory_path)
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.factory_path
                )
                
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    logger.warning(f"Git command failed (attempt {attempt + 1}): {result.stderr}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return False, result.stderr
                        
            except subprocess.TimeoutExpired:
                logger.error(f"Git command timed out (attempt {attempt + 1}): {command}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * 2)
                    continue
                else:
                    return False, "Command timed out after all retries"
            
            except Exception as e:
                logger.error(f"Git command exception (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return False, str(e)
        
        return False, "All retry attempts failed"
    
    def ensure_repo_setup(self):
        """Ensure git repository is properly set up"""
        success, output = self.execute_git_command("git remote -v", timeout=30)
        if not success:
            # Try to initialize repo
            logger.info("Initializing git repository...")
            success, output = self.execute_git_command("git init", timeout=30)
            if not success:
                logger.error(f"Failed to initialize git repo: {output}")
                return False
            
            # Add remote
            success, output = self.execute_git_command(f"git remote add origin {self.repo_url}", timeout=30)
            if not success:
                logger.error(f"Failed to add remote: {output}")
                return False
        
        # Check if main branch exists and is tracked
        success, output = self.execute_git_command("git branch -a", timeout=30)
        if "remotes/origin/main" not in output:
            logger.info("Setting up main branch...")
            self.execute_git_command("git branch -M main", timeout=30)
        
        return True
    
    def check_for_changes(self):
        """Check if there are any changes to sync"""
        success, output = self.execute_git_command("git status --porcelain", timeout=30)
        if not success:
            return False, False  # Error checking status
        
        changes = output.strip()
        return changes != "", changes
    
    def commit_changes(self, commit_message):
        """Commit changes with retry logic"""
        # Add all changes
        success, output = self.execute_git_command("git add .", timeout=60)
        if not success:
            logger.error(f"Failed to add changes: {output}")
            return False
        
        # Commit changes
        commit_cmd = f'git commit -m "{commit_message}\n\nCo-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"'
        success, output = self.execute_git_command(commit_cmd, timeout=90)
        if not success:
            if "nothing to commit" not in output.lower():
                logger.error(f"Failed to commit changes: {output}")
                return False
            else:
                logger.info("No changes to commit")
                return True
        
        logger.info("Successfully committed changes")
        return True
    
    def push_changes(self):
        """Push changes to GitHub with chunked push if needed"""
        # First try normal push
        success, output = self.execute_git_command("git push -u origin main", timeout=300)
        if success:
            logger.info("Successfully pushed to GitHub")
            return True
        
        # If push failed, try splitting into smaller pushes
        logger.warning("Large repository detected, attempting chunked push...")
        
        # Get list of files to push
        success, output = self.execute_git_command("git ls-files", timeout=60)
        if not success:
            logger.error(f"Failed to list files: {output}")
            return False
        
        files = output.strip().split('\n')
        chunk_size = 50  # Push 50 files at a time
        
        for i in range(0, len(files), chunk_size):
            chunk_files = files[i:i + chunk_size]
            
            # Add chunk
            files_arg = ' '.join(f'"{f}"' for f in chunk_files)
            success, output = self.execute_git_command(f"git add {files_arg}", timeout=90)
            if not success:
                logger.error(f"Failed to add chunk {i//chunk_size + 1}: {output}")
                continue
            
            # Commit chunk
            chunk_commit = f"git commit -m \"Chunk {i//chunk_size + 1}/{(len(files)-1)//chunk_size + 1} - Auto-sync configuration update"
            success, output = self.execute_git_command(chunk_commit, timeout=120)
            if not success:
                if "nothing to commit" not in output.lower():
                    logger.error(f"Failed to commit chunk {i//chunk_size + 1}: {output}")
                    continue
            
            # Push chunk
            success, output = self.execute_git_command("git push origin main", timeout=180)
            if not success:
                logger.error(f"Failed to push chunk {i//chunk_size + 1}: {output}")
                # Don't give up, continue with next chunk
                continue
            else:
                logger.info(f"Successfully pushed chunk {i//chunk_size + 1}")
        
        return True
    
    def sync_to_github(self, commit_message=None):
        """Main sync function"""
        config = self.load_sync_config()
        
        if not config.get("enabled", True):
            logger.info("Auto-sync is disabled")
            return False
        
        # Ensure repository is set up
        if not self.ensure_repo_setup():
            logger.error("Failed to set up repository")
            return False
        
        # Check for changes
        has_changes, changes = self.check_for_changes()
        if not has_changes:
            logger.info("No changes to sync")
            return True
        
        logger.info(f"Changes detected: {changes}")
        
        # Create commit message
        if not commit_message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"{config.get('commit_prefix', 'Auto-sync')} - {timestamp}"
        
        # Commit changes
        if not self.commit_changes(commit_message):
            logger.error("Failed to commit changes")
            return False
        
        # Push to GitHub
        if not self.push_changes():
            logger.error("Failed to push to GitHub")
            return False
        
        # Update sync timestamp
        config["last_sync"] = datetime.now().isoformat()
        config["retry_count"] = 0
        self.save_sync_config(config)
        
        logger.info("Successfully synced to GitHub")
        return True
    
    def schedule_auto_sync(self):
        """Schedule automatic sync runs"""
        import asyncio
        
        config = self.load_sync_config()
        sync_interval = config.get("sync_interval", 300)
        
        async def sync_loop():
            while config.get("enabled", True):
                try:
                    await asyncio.get_event_loop().run_in_executor(None, self.sync_to_github)
                    await asyncio.sleep(sync_interval)
                except Exception as e:
                    logger.error(f"Auto-sync error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute on error
        
        # Run sync loop
        asyncio.run(sync_loop())
    
    def enable_auto_sync(self):
        """Enable auto-sync and start daemon"""
        config = self.load_sync_config()
        config["enabled"] = True
        self.save_sync_config(config)
        
        # Write systemd service file (optional)
        service_content = f"""[Unit]
Description=Droid Settings Auto-Sync
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {__file__} --daemon
Restart=always
RestartSec=30
User={os.getenv('USER')}
WorkingDirectory={self.factory_path}
Environment=PYTHONPATH={self.factory_path}

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path.home() / ".config/systemd/user/droid-autosync.service"
        service_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        logger.info("Auto-sync enabled. Run: systemctl --user enable --now droid-autosync.service")
        logger.info(f"Service file written to: {service_file}")

# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Droid Settings GitHub Auto-Sync")
    parser.add_argument("--sync", action="store_true", help="Sync to GitHub now")
    parser.add_argument("--enable", action="store_true", help="Enable auto-sync")
    parser.add_argument("--disable", action="store_true", help="Disable auto-sync")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--message", help="Custom commit message")
    
    args = parser.parse_args()
    
    sync = DroidGitHubSync()
    
    if args.enable:
        sync.enable_auto_sync()
    
    elif args.disable:
        config = sync.load_sync_config()
        config["enabled"] = False
        sync.save_sync_config(config)
        logger.info("Auto-sync disabled")
    
    elif args.status:
        config = sync.load_sync_config()
        has_changes, changes = sync.check_for_changes()
        
        print(f"Auto-sync enabled: {config.get('enabled', False)}")
        print(f"Last sync: {config.get('last_sync', 'Never')}")
        print(f"Sync interval: {config.get('sync_interval', 300)} seconds")
        print(f"Changes pending: {'Yes' if has_changes else 'No'}")
        
        if has_changes:
            print(f"Pending changes:\n{changes}")
    
    elif args.daemon:
        logger.info("Starting auto-sync daemon...")
        sync.schedule_auto_sync()
    
    elif args.sync:
        success = sync.sync_to_github(args.message)
        exit(0 if success else 1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
