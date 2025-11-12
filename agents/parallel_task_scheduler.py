#!/usr/bin/env python3
"""
Parallel Task Scheduler for Droid CLI
Advanced parallelization for tasks and agents with resource management
"""

import os
import sys
import json
import logging
import threading
import queue
import time
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(threadName)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/parallel_scheduler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ParallelTask:
    """Represents a parallel task in the scheduler"""
    task_id: str
    task_type: str
    command: str
    args: tuple
    kwargs: dict
    priority: int  # Higher number = higher priority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = None
    max_wait_time: int = 604800  # Maximum wait time in seconds
    resource_requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        
        if self.resource_requirements is None:
            self.resource_requirements = {}

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class ParallelAgent:
    """Represents an agent that can process tasks in parallel"""
    agent_id: str
    agent_type: str
    status: AgentStatus
    current_task: Optional[str] = None
    supported_task_types: List[str]
    max_concurrent_tasks: int = 1
    performance_metrics: Dict[str, float] = None
    last_activity: datetime
    task_history: List[Dict[str, Any]]
    resource_usage: Dict[str, float] = None
    
    def __post_init__(self):
        if self.supported_task_types is None:
            self.supported_task_types = []
        
        if self.performance_metrics is None:
            self.performance_metrics = {
                'response_time': 1.0,
                'success_rate': 1.0,
                'efficiency': 1.0
            }
        
        if self.task_history is None:
            self.task_history = []
        
        if self.resource_usage is None:
            self.resource_usage = {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_io_percent': 0.0
            }

class ResourcePool:
    """Manages system resources for parallel execution"""
    
    def __init__(self, max_workers=None, max_memory_percent=80):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) * 2)
        self.max_memory_percent = max_memory_percent
        self.available_workers = self.max_workers
        self.allocated_memory = 0.0
        self.memory_stats = self.get_memory_stats()
        
    def get_memory_stats(self) -> Dict[str, float]:
        """Get current memory statistics"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
        except ImportError:
            return {'total': 0, 'available': 0, 'used': 0, 'percent': 0}
    
    def can_allocate_task(self, resource_requirements: Dict[str, Any]) -> bool:
        """Check if resources are available for task"""
        memory_required = resource_requirements.get('memory_mb', 10)
        
        # Check available workers
        if self.available_workers <= 0:
            return False
        
        # Check available memory
        memory_usage = (self.memory_stats['used'] / self.memory_stats['total']) * 100
        projected_usage = memory_usage + (memory_required * 1024 * 1024 / self.memory_stats['total'] * 100)  # Convert MB to percentage
        
        return projected_usage <= self.max_memory_percent
    
    def allocate_resources(self, task: ParallelTask):
        """Allocate resources for a task"""
        # Allocate one worker
        if self.available_workers > 0:
            self.available_workers -= 1
            task.status = TaskStatus.RUNNING
            return True
        
        return False
    
    def release_resources(self, task: ParallelTask):
        """Release resources used by a task"""
        self.available_workers += 1
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.COMPLETED

class ParallelTaskScheduler:
    """Main parallel task scheduler for Droid CLI"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.task_queue = queue.PriorityQueue()
        self.agent_pool = {}
        self.resource_pool = ResourcePool()
        self.executor = ThreadPoolExecutor(max_workers=self.resource_pool.max_workers)
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Task and agent tracking
        self.tasks = {}
        self.task_status_stats = {}
        self.agent_status_stats = {}
        
        # Performance tracking
        self.schedule_stats = {
            "total_scheduled": 0,
            "total_completed": 0,
            "total_failed": 0,
            "average_execution_time": 0.0,
            "parallelism_efficiency": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load saved agents if available
        self.load_registered_agents()
        
    def start_scheduler(self):
        """Start the parallel scheduler daemon"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Parallel task scheduler started")
    
    def stop_scheduler(self):
        """Stop the parallel scheduler daemon"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Shut down executor
        self.executor.shutdown(wait=True)
        logger.info("Parallel task scheduler stopped")
    
    def register_agent(self, agent_config: Dict[str, Any]) -> str:
        """Register an agent for parallel processing"""
        agent_id = agent_config['agent_id']
        
        agent = ParallelAgent(
            agent_id=agent_id,
            agent_type=agent_config.get('agent_type', 'unknown'),
            status=AgentStatus.IDLE,
            supported_task_types=agent_config.get('supported_tasks', []),
            max_concurrent_tasks=agent_config.get('max_concurrent', 1),
            performance_metrics=agent_config.get('performance_metrics', {}),
            last_activity=datetime.now()
        )
        
        self.agent_pool[agent_id] = agent
        logger.info(f"Registered parallel agent: {agent_id} ({agent.agent_type})")
        
        return agent_id
    
    def schedule_task(self, task_data: Dict[str, Any]) -> str:
        """Schedule a task for parallel execution"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"
        
        task = ParallelTask(
            task_id=task_id,
            task_type=task_data.get('task_type', 'unknown'),
            command=task_data.get('command', ""),
            args=tuple(task_data.get('args', [])),
            kwargs=task_data.get('kwargs', {}),
            priority=task_data.get('priority', 0),
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            dependencies=task_data.get('dependencies', []),
            max_wait_time=task_data.get('max_wait_time', 604800),
            resource_requirements=task_data.get('resource_requirements', {})
        )
        
        self.tasks[task_id] = task
        self.task_status_stats[task_id] = task.status
        self.schedule_stats['total_scheduled'] += 1
        
        # Add to priority queue
        priority = -task.priority  # Negative for max-heap behavior
        self.task_queue.put((priority, task))
        
        logger.info(f"Scheduled task: {task_id} ({task.task_type}) with priority {task.priority}")
        return task_id
    
    def execute_task(self, task: ParallelTask) -> Tuple[bool, Any]:
        """Execute a single task and return (success, result)"""
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.task_status_stats[task_id] = task.status
            
            # Choose execution method
            if self.has_available_agent_for_task(task):
                success, result = self.execute_with_agent(task)
            else:
                success, result = self.execute_with_threadpool(task)
            
            # Update status upon completion
            task.completed_at = datetime.now()
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            
            if success:
                self.schedule_stats['total_completed'] += 1
                if task.started_at and task.completed_at:
                    execution_time = (task.completed_at - task.started_at).total_seconds()
                    self.update_average_execution_time(execution_time)
            else:
                self.schedule_stats['total_failed'] += 1
            
            task.result = result
            return success, result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Task {task_id} failed: {e}")
            
            self.task_status_stats[task_id] = task.status
            self.schedule_stats['total_failed'] += 1
            
            return False, str(e)
    
    def has_available_agent_for_task(self, task: ParallelTask) -> bool:
        """Check if any agent is available for the task type"""
        for agent_id, agent in self.agent_pool.items():
            if (agent.status == AgentStatus.IDLE and 
                task.task_type in agent.supported_task_types and
                len(agent.current_task) < agent.max_concurrent_tasks):
                return True
        return False
    
    def execute_with_agent(self, task: ParallelTask) -> Tuple[bool, Any]:
        """Execute task using a specialized agent"""
        # Find suitable agent
        suitable_agent = self.find_suitable_agent(task)
        if not suitable_agent:
            return False, "No suitable agent available"
        
        # Allocate agent
        suitable_agent.current_task = task.task_id
        suitable_agent.status = AgentStatus.BUSY
        suitable_agent.last_activity = datetime.now()
        logger.info(f"Executing task {task_id} with agent {suitable_agent.agent_id}")
        
        try:
            # Get agent execution function
            agent_module = self.get_agent_module(suitable_agent.agent_type)
            if not hasattr(agent_module, 'execute_parallel_task'):
                return False, f"Agent {suitable_agent.agent_type} doesn't support parallel execution"
            
            # Execute task through agent
            result = agent_module.execute_parallel_task(
                task_id=task.task_id,
                task_type=task.task_type,
                command=task.command,
                args=task.args,
                kwargs=task.kwargs,
                data=task_data
            )
            
            # Update agent metrics
            start_time = task.started_at
            end_time = task.completed_at
            if start_time and end_time:
                execution_time = (end_time - start_time).total_seconds()
                self.update_agent_metrics(suitable_agent, execution_time, True)
            
            return True, result
            
        except Exception as e:
            logger.error(f"Agent {suitable_agent.agent_id} failed to execute task: {e}")
            return False, str(e)
    
    def execute_with_threadpool(self, task: ParallelTask) -> Tuple[bool, Any]:
        """Execute task using the thread pool"""
        logger.info(f"Executing task {task.task_id} with thread pool")
        
        try:
            # Execute with timeout handling
            future = self.executor.submit(
                self.execute_task_in_thread,
                task
            )
            
            # Wait for completion with timeout
            try:
                result = future.result(timeout=task.max_wait_time)
                return True, result
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                return False, str(e)
            
        except Exception as e:
            logger.error(f"ThreadPool execution for task {task.id} failed: {e}")
            task.status = TaskStatus.FAILED
            return False, str(e)
    
    def execute_task_in_thread(self, task: ParallelTask) -> Any:
        """Execute a task in a thread (actual implementation)"""
        # This would call the actual task execution logic
        # For now, we'll implement a simple execution
        
        try:
            import subprocess
            if task.command:
                # Execute shell command
                result = subprocess.run(
                    task.command,
                    capture_output=True,
                    text=True,
                    timeout=task.max_wait_time,
                    check=True
                )
                
                return {
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                # For non-command tasks, just return success
                return {'success': True, 'message': 'Task completed'}
                
        except subprocess.TimeoutExpired:
            task.status = TaskStatus.FAILED
            task.error = "Task timed out"
            
            raise
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            raise
    
    def find_suitable_agent(self, task: ParallelTask) -> Optional[ParallelAgent]:
        """Find the most suitable agent for a task"""
        suitable_agents = []
        
        for agent_id, agent in self.agent_pool.items():
            if (agent.status == AgentStatus.IDLE and
                task.task_type in agent.supported_task_types and
                len(agent.current_task) < agent.max_concurrent_tasks):
                
                # Calculate suitability score
                score = self.calculate_agent_suitability_score(agent, task)
                suitable_agents.append((score, agent))
        
        if suitable_agents:
            # Return agent with highest score
            suitable_agents.sort(key=lambda x: x[0], reverse=True)
            return suitable_agents[0][1]
        
        return None
    
    def calculate_agent_suitability_score(self, agent: ParallelAgent, task: ParallelTask) -> float:
        """Calculate suitability score for agent-task pairing"""
        score = 0.0
        
        # Task type match score
        if task.task_type in agent.supported_task_types:
            score += 0.4
        
        # Agent performance score
        if agent.performance_metrics:
            avg_performance = list(agent.performance_metrics.values())[0] if agent.performance_metrics else 1.0
            score += avg_performance * 0.3
        
        # Load balancing score
        current_load = len(agent.current_task) / max(agent.max_concurrent_tasks, 1.0)
        availability_score = 1.0 - current_load
        score += availability_score * 0.2
        
        # Recent performance score
        if agent.task_history:
            recent_tasks = agent.task_history[-5:]
            success_rate = sum(1 for task in recent_tasks 
                               if task.get('success', False)) / len(recent_tasks)
            score += success_rate * 0.1
        
        return score
    
    def update_agent_metrics(self, agent: ParallelAgent, execution_time: float, success: bool):
        """Update agent performance metrics"""
        if not agent.performance_metrics:
            agent.performance_metrics = {
                'response_time': 1.0,
                'success_rate': 1.0,
                'efficiency': 1.0
            }
        
        # Update response time
        old_response_time = agent.performance_metrics['response_time']
        if old_response_time > 0:
            agent.performance_metrics['response_time'] = (
                old_response_time * 0.8 + execution_time * 0.2
            )
        
        # Update success rate
        old_success_rate = agent.performance_metrics['success_rate']
        if old_success_rate > 0:
            agent.performance_metrics['success_rate'] = (
                old_success_rate * 0.9 + (1.0 if success else 0.0) * 0.1
            )
        
        # Update efficiency
        efficiency = execution_time / (response_time / 1.0) if old_response_time > 0 else 1.0
        old_efficiency = agent.performance_metrics['efficiency']
        agent.performance_metrics['efficiency'] = (
            old_efficiency * 0.8 + efficiency * 0.2
        )
        
        # Update task history
        agent.task_history.append({
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'success': success,
            'task_type': agent.current_task and agent.current_task[0]  # Simplified
        })
        
        # Keep only recent history
        if len(agent.task_history) > 50:
            agent.task_history = agent.task_history[-50:]
    
    def update_average_execution_time(self, execution_time: float):
        """Update average execution time metric"""
        current_avg = self.schedule_stats["average_execution_time"]
        completed_count = self.schedule_stats["total_completed"]
        
        if completed_count > 0:
            avg_time = (current_avg * completed_count + execution_time) / (completed_count + 1)
            self.schedule_stats["average_execution_time"] = avg_time
    
    def scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Starting parallel scheduler loop")
        
        while self.scheduler_running:
            try:
                # Process any ready tasks
                self.process_ready_tasks()
                
                # Check for completed tasks
                self.completed_tasks()
                
                # Optimize scheduling
                self.optimize_scheduling()
                
                # Clean up completed tasks
                self.cleanup_completed_tasks()
                
                # Sleep to prevent busy waiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(5)  # Error recovery wait
    
    def process_ready_tasks(self):
        """Process tasks that are ready to execute"""
        ready_tasks = []
        
        # Check resource availability and get ready tasks
        while not self.task_queue.empty():
            priority, task = self.task_queue.get()
            
            if self.resource_pool.can_allocate_task(task.resource_requirements):
                ready_tasks.append(task)
            else:
                # Put back in queue and wait for resources
                self.task_queue.put((priority, task))
                break
        
        # Execute ready tasks in parallel
        if ready_tasks:
            logger.info(f"Executing {len(ready_tasks)} tasks in parallel")
            
            futures = []
            for task in ready_tasks:
                if self.resource_pool.allocate_resources(task):
                    future = self.executor.submit(self.execute_task, task)
                    futures.append(future)
            
            # Wait for completion
            try:
                for future in as_completed(futures):
                    task_id = None
                    for task in ready_tasks:
                        if hasattr(future, '_task_id'):
                            task_id = task_id or task.task_id
                        break
                    if task_id:
                        task = self.tasks.get(task_id)
                        if task:
                            success, result = future.result()
                            self.handle_task_completion(task, success, result)
            except Exception as e:
                logger.error(f"Error processing task completion: {e}")
            
            # Release resources
            for task in ready_tasks:
                self.resource_pool.release_resources(task)
                
                # Update agent status if agent was used
                self.update_agent_status_after_task(task)
    
    def completed_tasks(self):
        """Handle completed tasks"""
        # Task completion is handled in process_ready_tasks
        pass
    
    def optimize_scheduling(self):
        """Optimize task scheduling based on performance"""
        # Analyze task completion patterns
        # Implement adaptive priority adjustments
        pass
    
    def cleanup_completed_tasks(self):
        """Clean up completed tasks to prevent memory leaks"""
        current_time = datetime.now()
        max_age_hours = 24  # Keep tasks for 24 hours
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.completed_at and 
                (current_time - task.completed_at).total_seconds() > max_age_hours * 3600 and
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            if task_id in self.task_status_stats:
                del self.task_status_stats[task_id]
        
        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} completed tasks")
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get current status of a specific agent"""
        agent = self.agent_pool.get(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "performance_metrics": agent.performance_metrics,
            "resource_usage": agent.resource_usage,
            "last_activity": agent.last_activity.isoformat(),
            "task_history_count": len(agent.task_history)
        }
    
    def update_agent_status_after_task(self, task: ParallelTask):
        """Update agent status after task completion"""
        # Determine which agent was used (this would be tracked during execution)
        # For now, we'll mark all idle agents
        for agent in self.agent_pool.values():
            if agent.current_task == task.task_id:
                agent.current_task = None
                agent.status = AgentStatus.IDLE
                
                # Update agent metrics
                if task.started_at and task.completed_at:
                    execution_time = (task.completed_at - task.started_at).total_seconds()
                    self.update_agent_metrics(agent, execution_time, task.status == TaskStatus.COMPLETED)
    
    def get_agent_pool_status(self) -> Dict[str, Any]:
        """Get status of all agents in the pool"""
        return {
            "total_agents": len(self.agent_pool),
            "active_agents": len([a for a in self.agent_pool.values() if a.status == AgentStatus.BUSY]),
            "idle_agents": len([a for a in self.agent_pool.values() if a.status == AgentStatus.IDLE]),
            "total_capacity": sum(a.max_concurrent_tasks for a in self.agent_pool.values()),
            "resource_pool": {
                "max_workers": self.resource_pool.max_workers,
                "available_workers": self.resource_pool.available_workers
            }
        }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status"""
        return {
            "running": self.scheduler_running,
            "scheduler_thread": self.scheduler_thread.is_alive() if self.scheduler_thread else None,
            "task_queue_size": self.task_queue.qsize(),
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.status_stats["total_failed"]]),
            "schedule_stats": self.schedule_stats,
            "resource_status": {
                "available_workers": self.resource_pool.available_workers,
                "memory_usage": self.memory_stats['percent'],
                "memory_available": self.memory_stats['available']
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_parallel_tasks(self, task_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel"""
        task_ids = []
        
        # Schedule all tasks
        for task_data in task_list:
            task_id = self.schedule_task(task_data)
            task_ids.append(task_id)
        
        # Process tasks in parallel with dependency resolution
        task_results = []
        completed_tasks = 0
        
        # Resolve dependencies and execute
        while completed_tasks < len(task_ids):
            for task_id in task_ids[:]:
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    # Check if dependencies are met
                    if self.are_dependencies_met(task):
                        success, result = self.execute_task(task)
                    elif task.dependencies:
                        # Wait for dependencies to complete
                        success, result = self.wait_for_dependencies(task)
                
                    if success:
                        task_results.append({
                            'task_id': task_id,
                            'result': result,
                            'agent_used': False
                        })
                        completed_tasks += 1
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = "Failed to execute in thread pool"
                        task_completed_at = datetime.now()
                        
                        task_results.append({
                            'task_id': task_id,
                            'result': 'Failed to execute task',
                            'agent_used': False
                        })
                        completed_tasks += 1
                    else:
                    # Skip for now, will be retried in next iteration
                    pass
                else:
                    # Task is no longer pending
                    completed_tasks += 1
                    continue
                    
            if completed_tasks >= len(task_ids):
                break
            
            if completed_tasks < len(task_ids):
                time.sleep(1)
        
        return {
            'total_tasks': len(task_list),
            'completed_tasks': completed_tasks,
            'failed_tasks': len([t['result'] == 'Failed to execute task' for t in task_results]),
            'task_results': task_results
        }
    
    def are_dependencies_met(self, task: ParallelTask) -> bool:
        """Check if all dependencies for a task are met"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.SUCCESS]:
                return False
        return True
    
    def wait_for_dependencies(self, task: ParallelTask, timeout: int = 60) -> bool:
        """Wait for task dependencies to complete"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task:
                if dep_task.status == TaskStatus.PENDING:
                    # Start the dependency task
                    success, _ = self.execute_task(dep_task)
                    if not success:
                        return False
                    
                    # Poll for completion
                    wait_time = 0
                    while (dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                           wait_time < timeout):
                        time.sleep(1)
                        wait_time += 1
                    
                    if dep_task.status == TaskStatus.FAILED:
                        return False
                    
                    # Check if dependencies are now met
                    if not self.are_dependencies_met(task):
                        return False
                else:
                    # Dependency not found, assume completed
                    pass
            else:
                # Dependency not found, assume completed
                pass
        
        return True
    
    def register_predefined_agents(self):
        """Register commonly used agents"""
        predefined_agents = [
            {
                "agent_id": "file_operations",
                "agent_type": "file_system",
                "supported_tasks": ["file_operations", "directory_management", "path_operations"],
                "max_concurrent": 3,
                "performance_metrics": {
                    "response_time": 0.5,
                    "success_rate": 0.9,
                    "efficiency": 0.85
                }
            },
            {
                "agent_id": "code_generator",
                "agent_type": "code_generation",
                "supported_tasks": ["code_generation", "code_analysis", "code_optimization"],
                "max_concurrent": 2,
                "performance_metrics": {
                    "response_time": 2.0,
                    "success_rate": 0.8,
                    "efficiency": 0.75
                }
            },
            {
                "agent_id": "tool_executor",
                "agent_type": "tool_execution",
                "supported_tasks": ["tool_execute", "command_execution", "process_management"],
                "max_concurrent": 3,
                "performance_metrics": {
                    "response_time": 1.5,
                    "success_rate": 0.85,
                    "efficiency": 0.8
                } 
            },
            {
                "agent_id": "agent_interceptor",
                "agent_type": "task_orchestration",
                "supported_tasks": ["task_filtering", "task_routing", "parallel_coordination"],
                "max_concurrent": 5,
                "performance_metrics": {
                    "response_time": 0.8,
                    "success_rate": 0.9,
                    "efficiency": 0.9
                }
            }
        ]
        
        for agent_config in predefined_agents:
            self.register_agent(agent_config)
    
    def load_registered_agents(self):
        """Load registered agents from configuration"""
        # This would load agents from a config file
        # For now, register predefined agents
        self.register_predefined_agents()

# Global scheduler instance
_parallel_scheduler = None

def get_parallel_scheduler() -> ParallelTaskScheduler:
    """Get or create global parallel scheduler instance"""
    global _parallel_scheduler
    if _parallel_scheduler is None:
        _parallel_scheduler = ParallelTaskScheduler()
    return _parallel_scheduler

# Convenience functions
def schedule_parallel_tasks(task_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Schedule multiple tasks for parallel execution"""
    scheduler = get_parallel_scheduler()
    return scheduler.execute_parallel_tasks(task_list)

def execute_parallel_task(task_data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Execute a single task in parallel"""
    scheduler = get_parallel_scheduler()
    task_id = scheduler.schedule_task(task_data)
    
    if task_id:
        task = scheduler.tasks.get(task_id)
        if task:
            return scheduler.execute_task(task)
    
    return False, "Task scheduling failed"

if __name__ == "__main__":
    # Test the parallel scheduler
    scheduler = ParallelTaskScheduler()
    scheduler.start_scheduler()
    
    # Register some predefined agents
    scheduler.register_predefined_agents()
    
    # Test parallel task execution
    test_tasks = [
        {
            "task_type": "file_operations",
            "command": "ls -la",
            "priority": 1,
            "args": ("/tmp",)
        },
        {
            "task_type": "code_generation",
            "command": "echo 'Hello World'",
            "priority": 2, 
            "args": [],
            "kwargs": {"shell": True}
        },
        {
            "task_type": "tool_execution",
            "command": "python3 -c 'print(\"Task completed\")'",
            "priority": 3,
            "args": [],
            "kwargs": {}
        }
    ]
    
    print("Testing parallel task execution...")
    results = scheduler.execute_parallel_tasks(test_tasks)
    
    print(f"Total tasks: {results['total_tasks']}")
    print(f"Completed: {results['completed_tasks']}")
    print(f"Failed: {results['failed_tasks']}")
    print(f"Task results: {len(results['task_results'])}")
    
    # Get status
    status = scheduler.get_scheduler_status()
    print("\nScheduler status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Get agent pool status
    agent_status = scheduler.get_agent_pool_status()
    print("\nAgent pool status:")
    print(json.dumps(agent_status, indent=2, default=str))
    
    # Stop scheduler
    scheduler.stop_scheduler()
    print("\nScheduler stopped")
