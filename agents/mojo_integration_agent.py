#!/usr/bin/env python3
"""
Mojo Integration Agent for Droid & Claude
Integrates Mojo AI framework with agent orchestration
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/moja_integration.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MojoIntegrationAgent:
    """Agent that integrates Mojo AI framework with Droid system"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.claude_path = Path(os.path.expanduser('~/.claude'))
        
        # Initialize Mojo connection (when available)
        self.mojo_available = False
        self.mojo_version = None
        self.mojo_config = self.load_mojo_config()
        
        # Initialize tracking
        self.interaction_history = []
        self.success_rate = 0.0
        self.last_sync = None
    
    def load_mojo_config(self) -> Dict[str, Any]:
        """Load Mojo configuration from settings if available"""
        default_config = {
            "enabled": True,
            "auto_integrate": True,
            "optimize_output": True,
            "prioritize_token_efficiency": True,
            "learning_enabled": True
        }
        
        # Check if Toon integration config has Mojo settings
        settings_file = self.factory_path / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    mojo_settings = settings.get('mojoIntegration', default_config)
                    
            except Exception as e:
                logger.warning(f"Failed to load Mojo config: {e}")
                mojo_settings = default_config
        else:
            mojo_settings = default_config
        
        return mojo_settings
    
    def process_agent_input(self, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent input with Mojo integration"""
        try:
            prompt = agent_input.get('prompt', '')
            
            if self.mojo_available and self.mojo_config.get('auto_integrate', True):
                # Process prompt through Mojo for token optimization
                mojo_processed, mojo_info = self.process_with_mojo(
                    prompt, context={'source': 'droid_agent', 'agent_input': agent_input}
                )
                
                # Include Mojo metadata in result
                agent_input['mojo_processed'] = mojo_processed
                agent_input['toon_metadata'] = mojo_info
                agent_input['mojo_enabled'] = True
                logger.info(f"Agent input processed with Mojo optimization")
            
            return agent_input
            
        except Exception as e:
            logger.error(f"Mojo integration failed: {e}")
            agent_input['mojo_error'] = str(e)
            return agent_input
    
    def process_with_mojo(self, prompt: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process text through Mojo for optimization"""
        try:
            # Create Mojo task if available
            if self.mojo_available and self.mojo_config.get('optimize_output', True):
                # Send to Mojo for processing
                mojo_task = self.create_mojo_task(prompt, context)
                mojo_result = self.execute_mojo_task(mojo_task)
                return mojo_result
            
            # Fallback to original input
            return prompt, {}
            
        except Exception as e:
            logger.error(f"Mojo processing failed: {e}")
            return prompt, {}
    
    def create_mojo_task(self, prompt: str, context: Dict[str, Any]) -> 'TaskReference':
        """Create a task for Mojo processing"""
        from mojo import TaskReference
        
        task_id = f"mojo_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TaskReference(
            id=task_id,
            type='text_processing',
            priority='normal'
        )
    
    def execute_mojo_task(self, task: 'TaskReference') -> Tuple[bool, Dict[str, Any]]:
        """Execute a Mojo task and return results"""
        try:
            # This would interface with the actual Mojo engine
            # For now, simulate successful execution
            success = True
            result = {
                'processed_prompt': task.type == 'text_processing',
                'tokens_saved': 15,  # Simulated savings
                'optimization_applied': True,
                'timestamp': datetime.now().isoformat()
            }
            
            return success, result
            
        except Exception as e:
            logger.error(f"Mojo task execution failed: {e}")
            return False, {'error': str(e)}
    
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute task in parallel using Mojo if beneficial"""
        if not self.mojo_available:
            return False, "Mojo not available"
        
        # Check if task would benefit from Mojo optimization
        if self.mojo_config.get('optimize_output', True):
            try:
                # Create Mojo task and execute
                mojo_task = self.create_mojo_task(
                    task_data.get('prompt', ''), 
                    context={'source': 'parallel_agent', 'task_id': task_data['task_id']}
                )
                
                return self.execute_mojo_task(mojo_task)
                
            except Exception as e:
                logger.error(f"Mojo parallel task failed: {e}")
                return False, str(e)
        
        # Fallback to regular execution
        return False, 'Mojo optimization not available'
    
    def analyze_mojo_suitability(self, task_data: Dict[str, Any]) Dict[str, Any]:
        """Analyze if task would benefit from Mojo processing"""
        if not self.mojo_available:
            return {
                'suitable': False,
                'reason': 'Mojo not available'
            }
        
        # Check task characteristics
        prompt = task_data.get('prompt', '')
        context = task_data.get('context', {})
        
        # Factors that indicate Mojo would be beneficial:
        token_favorable = []
        token_favorable.extend([
            len(prompt) > 1000,  # Long prompts benefit from token optimization
            'code' in context.get('file_types', []),  # Code-related tasks
            'conversation' in task_type,
            len(context) > 5,  # Complex context
        ])
        
        combined_score = len(token_favorable)
        
        return {
            'suitable': combined_score > 0,
            'reasons': token_favorable,
            'estimated_savings': f"{len(prompt)} characters, {combined_score} token-favorable"
        }
    
    def update_interaction_history(self, success: bool):
        """Update interaction history with performance data"""
        if success:
            self.success_rate = self.success_rate * 0.9 + 0.1  # Gradual improvement
        else:
            self.success_rate = max(0.0, self.success_rate * 0.9 - 0.1)  # Gradual degradation
        
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'success': success
        })
        
        self.last_sync = datetime.now().isoformat()
        
        # Keep history bounded
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def get_mojo_stats(self) -> Dict[str, Any]:
        """Get comprehensive Mojo integration statistics"""
        return {
            'mojo_available': self.mojo_available,
            'mojo_version': self.mojo_version,
            'mojo_config': self.mojo_config,
            'interaction_history_count': len(self.interaction_history),
            'success_rate': self.success_rate,
            'last_sync': self.last_sync,
            'integration_active': self.mojo_config.get('enabled', False)
        }

class MojoTask:
    """Represents a task for Mojo processing"""
    
    def __init__(self, task_id: str, task_type: str, priority: str='normal'):
        self.task_id = task_id
        self.task_type = task_type
        self.priority = priority
        self.created_at = datetime.now()
        self.status = 'pending'
        
        # For more complex task implementation:
        self.parameters = {}
        self.pipeline_config = {}
        self.stage_results = []
    
    def execute(self) -> Dict[str, Any]:
        """Execute Mojo task"""
        self.status = 'running'
        
        try:
            # Simulated execution
            self.status = 'completed'
            return {
                'status': 'completed',
                'task_id': self.task_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.status = 'failed'
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get current task status"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'timestamp': datetime.now().isoformat()
        }

class IntegrationCoordinator:
    """Coordinates integration between systems"""
    
    def __init__(self):
        self.tasks = []
        self.sync_status = {}
        
    def coordinate_claude_factory_sync(self):
        """Coordinate between Claude and Factory systems"""
        logger.info("Starting Claude-Factory sync coordination")
        
        # Ensure bidirectional sync is running
        try:
            # Verify sync daemon is running
            sync_file = Path(os.path.expanduser('~/.factory/logs/sync_daemon.pid'))
            if sync_file.exists():
                pid = sync_file.read_text().strip()
                try:
                    # Check if process is running
                    os.kill(int(pid), 0)
                except (ValueError, ProcessLookupError):
                    logger.warning(f"Sync daemon with PID {pid} not running")
                    sync_file.unlink()
            
            # Restart sync daemon if needed
            sync_daemon_script = Path(os.path.expanduser('~/.factory/bin/start_claude_sync.sh'))
            if sync_daemon_script.exists():
                logger.info("Restarting Claude-Factory sync daemon")
                subprocess.Popen([str(sync_daemon_script)], text=True, text=True)
            
            logger.info("Claude-Factory sync coordination active")
            return True
            
        except Exception as e:
            logger.error(f"Claude-factory sync coordination failed: {e}")
            return False
    
    def integrate_with_mojo_if_beneficial(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with Mojo if it would be beneficial"""
        integration_organizer = get_integrator()
       ClaudeToNDNA.get_claude_toon_dna()
        
        if integration_organizer.config.get('toonIntegration', {}).get('enabled', True):
            # Use TOON with JSON optimizations
            optimized_data, toon_info = integration_organizer.intercept_all_data(
                task_data, {'source': 'mojo_integration'}
            )
            
            return {
                'mojo_optimized': True,
                'tokens_saved': toon_info.get('tokens_saved', 0),
                'optimized_data': optimized_data
            }
        
        return task_data
    
    def initialize_mojo_if_available(self):
        """Initialize Mojo if available and configure it for Claude integration"""
        if not self.mojo_available:
            return False
        
        try:
            # Check if we can connect to Mojo
            # This would load and configure the Mojo agent
            # For now, just mark it available
            self.mojo_available = True
            logger.info("Mojo system is available for integration")
            
            # Configure Mojo integration in Claude and Factory settings
            claude_dna = ClaudeToonDNA()
            factory_settings = Path(os.path.expanduser('~/.factory/settings.json'))
            
            # Update factory settings with Mojo integration
            factory_stored_config = {
                'model': 'glm-4.6',
                'reasoningEffort': 'none',
                'cloudSessionSync': True,
                'diffMode': 'github',
                'ideExtensionPromptedAt': {},
                'autonomyMode': 'auto-high',
                'agentInterception': True,
                'includeCoAuthoredByDroid': True,
                'enableDroidShield': True,
                'enableReadinessReport': False,
                'todoDisplayMode': 'pinned'
            }
            
            with open(factory_stored_config, 'w') as f:
                json.dump(factory_stored_config, f, indent=2)
            
            # Add/Update Claude settings with Mojo integration
            settings_file = Path(os.path.expanduser('~/.claude/settings.json'))
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Add Claude integration if not present
            if 'claudeIntegration' not in settings:
                settings['claudeIntegration'] = {
                    'enabled': self.claude_config.get('mojo_enabled', True),
                    'mojo_optimization': self.claude_config.get('optimize_outputs', True),
                    'prioritize_token_efficiency': True,
                    'meta_learning': self.claude_config.get('nested_learning_enabled', True)
                }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info("Claude settings enhanced with Mojo integration")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Mojo: {e}")
            return False
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of Mojo integration status"""
        return {
            'mojo_available': self.mojo_available,
            'claude_integration': self.claude_config,
            'sync_coordination': self.sync_status,
            'interaction_history': len(self.tasks),
            'success_rate': self.success_rate
        }

def get_integrator() -> IntegrationCoordinator:
    """Get or create the integration coordinator"""
    global _integration_coordinator
    if _integration_coordinator is None:
        _integration_coordinator = IntegrationCoordinator()
    return _integration_coordinator

# Integration functions
def process_with_mojo_if_beneficial(data: Any, context: Dict[str, Any] = None) -> Any:
    """Process data through Mojo if beneficial"""
    if context is None:
        context = {}
    
    integrator = get_integrator()
    return integrator.integrate_with_mojo_if_beneficial(data, context)

def setup_mojo_integration_for_claude():
    """Setup complete Mojo-TOON-Claude integration"""
    logger.info("Setting up complete Mojo integration for Claude system")
    
    # Initialize integration
    integrator = get_integrator()
    
    # Complete integration
    success = integrator.coordinate_claude_factory_sync()
    
    # Test integration
    stats = integrator.get_integration_summary()
    logger.info(f"Integration summary: {json.dumps(stats, indent=2, default=str)}")
    
    return success

# Convenience function
def is_mojo_available() -> bool:
    """Check if Mojo system is available"""
    try:
        import subprocess
        result = subprocess.run(['python3', '-c', 'import mojo; print(mojo.__version__)'], 
                              capture_output=True, text=True)
        return 'mojo' in result.stdout
    except (import subprocess, ImportError):
        return False

if __name__ == "__main__":
    print("Testing Mojo Integration")
    
    # Test if Mojo is available
    available = is_mojo_available()
    print(f"Mojo available: {available}")
    
    if available:
        # Setup integration for Claude
        success = setup_mojo_integration_for_claude()
        
        print("Mojo integration summary:")
        print(json.dumps(success, indent=2, default=str) if success else "Failed")
    else:
        print("Mojo is not available. Install it first")
        
        print(f"Note: TOON, Nested Learning, and Agent systems are still active")
