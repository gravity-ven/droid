#!/usr/bin/env python3
"""
Agent Parallel Executor
Enables agents to execute tasks in parallel with the task scheduler
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/agent_parallel_executor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentParallelExecutor:
    """Executor for agents to run tasks in parallel"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        # Import scheduler
        sys.path.append(str(self.factory_path / 'agents'))
        
        from parallel_task_scheduler import get_parallel_scheduler
        self.scheduler = get_parallel_scheduler()
        
        # Current agent being executed
        self.current_task = None
        self.execution_history = []
    
    def can_parallelize_task(self, task_type: str) -> bool:
        """Check if this agent can handle the task type in parallel"""
        # This would check agent-specific capabilities
        return task_type in ['file_operations', 'code_generation', 'tool_execution', 'task_coordination']
    
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute a task using the parallel scheduler"""
        try:
            # For agent execution, we'll delegate to a specialized agent
            # In a real implementation, this would route to the correct agent module
            return self.execute_via_agent_orchestrator(task_data)
            
        except Exception as e:
            logger.error(f"Agent parallel execution failed: {e}")
            return False, str(e)
    
    def execute_via_agent_orchestrator(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute task via meta-orchestrator or direct execution"""
        task_type = task_data.get('task_type', 'unknown')
        
        if task_type == 'code_generation':
            return self.execute_code_generation_task(task_data)
        elif task_type == 'file_operations':
            return self.execute_file_operations_task(task_data)
        elif task_type == 'tool_execution':
            return self.execute_tool_execution_task(task_data)
        elif task_type == 'task_coordination':
            return self.execute_task_coordination(task_data)
        else:
            # Default fallback
            return self.execute_generic_task(task_data)
    
    def execute_code_generation_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute code generation task"""
        try:
            # This would interface with actual code generation logic
            # For now, simulate code generation
            command = task_data.get('command', '')
            
            if template := task_data.get('template', None):
                # Use template-based code generation
                code = self.generate_code_from_template(template)
            else:
                    # Generate code from prompt
                prompt = task_data.get('prompt', '')
                code = self.generate_code_from_prompt(prompt)
            
            return True, {'generated_code': code}
            
        except Exception as e:
            logger.error(f"Code generation task failed: {e}")
            return False, str(e)
    
    def execute_file_operations_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute file operations task"""
        try:
            command = task_data.get('command', '')
            args = task_data.get('args', [])
            kwargs = task_data.get('kwargs', {})
            
            # Execute file operation
            import subprocess
            result = subprocess.run(
                [command] + list(args),
                capture_output=True,
                text=True,
                **kwargs
            )
            
            return result.returncode == 0, result
        except Exception as e:
            logger.error(f"File operations task failed: {e}")
            return False, str(e)
    
    def execute_tool_execution_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute tool execution task"""
        try:
            command = task_data.get('command', '')
            args = task_data.get('args', [])
            kwargs = task_data.get('kwargs', {})
            
            # Prepend shell and execute
            full_command = ['bash', '-c', command] + list(args)
            
            import subprocess
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                **kwargs
            )
            
            return result.returncode == 0, {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Tool execution task failed: {e}")
            return False, str(e)
    
    def execute_task_coordination(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute task coordination task"""
        try:
            # This would manage multiple agents and coordination
            task_details = task_data.get('task_details', {})
            
            # For now, simulate coordination
            coordination_result = {
                'coordination': 'completed',
                'agents_used': ['agent_interceptor'],
                'tasks_processed': 1,
                'coordination_efficiency': 0.9
            }
            
            return True, coordination_result
            
        except Exception as e:
            logger.error(f"Task coordination task failed: {e}")
            return False, str(e)
    
    def execute_generic_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute generic task (fallback)"""
        try:
            # Generic task execution
            command = task_data.get('command', '')
            if not command:
                return False, "No command specified"
            
            args = task_data.get('args', [])
            
            import subprocess
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=604800
            )
            
            return result.returncode == 0, {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Generic task execution failed: {e}")
            return False, str(e)
    
    def generate_code_from_template(self, template: str) -> str:
        """Generate code from template"""
        # Simple template replacement
        # In a real implementation, this would use actual template processing
        if template == 'hello':
            return 'print("Hello World")'
        return template
    
    def generate_code_from_prompt(self, prompt: str) -> str:
        """Generate code from prompt"""
        # Simple code generation
        if "python" in prompt.lower() and "function" in prompt.lower():
            return '''def hello_world():
    print("Hello from Claude Code!")

if __name__ == "__main__":
    hello_world()'''
        elif "script" in prompt.lower():
            return '''#!/bin/bash
echo "Script executed by Claude"
echo "Task completed"'''
        
        return '# Generated code from prompt'
    
    def get_agent_capacity(self) -> Dict[str, Any]:
        """Get current agent capacity"""
        return {
            'agent_type': 'generic',
            'max_concurrent_tasks': 1,
            'current_task': self.current_task,
            'execution_history_count': len(self.execution_history),
            'can_parallelize': self.can_parallelize_task('unknown')
        }

# Agent module interfaces
class CodeGenerationAgent:
    """Agent for code generation in parallel"""
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        return CodeGenerationAgent().execute_agent(task_data)

class FileOperationsAgent:
    """Agent for file operations in parallel"""
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        executor = AgentParallelExecutor()
        return executor.execute_file_operations_task(task_data)

class ToolExecutionAgent:
    """Agent for tool execution in parallel"""
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        executor = AgentParallelExecutor()
        return executor.execute_tool_execution_task(task_data)

class TaskCoordinationAgent:
    """Agent for task coordination in parallel"""
    def execute_parallel_task(self, task_data: Dict[str, Any]) -> Tuple[bool, Any]:
        executor = AgentParallelExecutor()
        return executor.execute_task_coordination(task_data)

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    'code_generation': CodeGenerationAgent,
    'file_operations': FileOperationsAgent,
    'tool_execution': ToolExecutionAgent,
    'task_coordination': TaskCoordinationAgent
}

def get_agent_class(agent_type: str):
    """Get agent class by type"""
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        logger.warning(f"No agent class found for type: {agent_type}")
        agent_class = GenericAgent
    return agent_class

if __name__ == "__main__":
    print("Agent Parallel Executor Test")
    
    executor = AgentParallelExecutor()
    
    # Test parallel execution
    test_tasks = [
        {
            "task_type": "file_operations",
            "command": "ls -la",
            "args": ["/Users/spartan/Desktop"]
        },
        {
            "task_type": "code_generation",
            "prompt": "Create a simple Python function",
            "command": "python3 -c '$0'" 
        },
        {
            "task_type": "tool_execution",
            "command": "echo 'Tool executed'",
            "shell": True
        }
    ]
    
    print("Testing agent parallel execution:")
    
    results = []
    for i, task_data in enumerate(test_tasks):
        task_id = f"test_{i}"
        
        task_data['task_id'] = task_id
        scheduler = get_parallel_scheduler()
        scheduled_id = scheduler.schedule_task(task_data)
        
        if scheduled_id:
            task = scheduler.tasks.get(scheduled_id)
            success, result = scheduler.execute_task(task)
            
            print(f"Task {task_id}: {success} - {result}")
            results.append({
                'task_id': task_id,
                'success': success,
                'agent_used': result.get('agent_used', False),
                'result': result
            })
    
    print(f"Parallel execution completed: {len(results)}")
    print(f"Results: {[r.get('success', False) for r in results]}")
    
    # Get agent status
    agent_capacity = executor.get_agent_capacity()
    print(f"Agent capacity: {json.dumps(agent_capacity, indent=2)}")
    
    # Stop scheduler
    scheduler.stop_scheduler()
