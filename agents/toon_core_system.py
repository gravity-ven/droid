#!/usr/bin/env python3
"""
TOON Core System Integration
Deep integration of Token-Oriented Object Notation into Droid DNA
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import threading
import queue
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.factory/logs/toon_core.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TOONCoreSystem:
    """Core TOON integration system embedded in Droid DNA"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.claude_path = Path(os.path.expanduser('~/.claude'))
        
        # TOON configuration
        self.config = self.load_toon_config()
        
        # Core components
        self.toon_interceptor = TOONInterceptor(self)
        self.toon_optimizer = TOONOptimizer(self)
        self.toon_cache = TOONCache(self)
        
        # Runtime state
        self.conversion_stats = {
            'total_conversions': 0,
            'total_tokens_saved': 0,
            'conversion_rate': 0.0,
            'last_conversion': None
        }
        
        # Start background processing
        self.background_thread = threading.Thread(target=self.background_processor, daemon=True)
        self.background_thread.start()
        
        self.conversion_queue = queue.Queue()
        self.optimization_queue = queue.Queue()
        
        logger.info("TOON Core System initialized and embedded in Droid DNA")
    
    def load_toon_config(self) -> Dict[str, Any]:
        """Load TOON configuration from settings"""
        settings_file = self.factory_path / 'settings.json'
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                return settings.get('toonIntegration', {
                    'enabled': True,
                    'coreSystem': True,
                    'autoConvert': True,
                    'minSavingsPercent': 15,
                    'optimizePrompts': True,
                    'optimizeResponses': True,
                    'optimizeConfigs': True,
                    'optimizeLogs': True,
                    'tokenAware': True,
                    'intelligentTruncation': True,
                    'contextOptimization': True,
                    'agentInterception': True,
                    'nestedLearning': True
                })
            except Exception as e:
                logger.error(f"Failed to load TOON config: {e}")
        
        return {'enabled': False}
    
    def intercept_all_data(self, data: Any, context: Dict[str, Any] = None) -> Tuple[Any, Dict[str, Any]]:
        """Intercept and process all data through TOON system"""
        context = context or {}
        
        if not self.config.get('enabled', False):
            return data, {'intercepted': False, 'reason': 'TOON disabled'}
        
        interception_result = {
            'intercepted': True,
            'original_type': type(data).__name__,
            'toon_applied': False,
            'tokens_saved': 0,
            'compression_ratio': 0.0,
            'optimizations_applied': []
        }
        
        try:
            # Determine if TOON conversion is beneficial
            should_convert, analysis = self.should_convert_to_toon(data, context)
            interception_result['analysis'] = analysis
            
            if should_convert:
                # Convert to TOON
                toon_data, conversion_info = self.convert_to_toon(data, context)
                interception_result['toon_applied'] = True
                interception_result['tokens_saved'] = conversion_info['tokens_saved']
                interception_result['compression_ratio'] = conversion_info['compression_ratio']
                interception_result['optimizations_applied'] = conversion_info['optimizations']
                
                # Update statistics
                self.update_conversion_stats(conversion_info)
                
                result_data = toon_data
            else:
                result_data = data
            
            # Apply intelligent context optimization if enabled
            if self.config.get('contextOptimization', True):
                context_opt = self.toon_optimizer.optimize_context(result_data, context)
                if context_opt['optimized']:
                    result_data = context_opt['data']
                    interception_result['optimizations_applied'].extend(context_opt['optimizations'])
            
            return result_data, interception_result
            
        except Exception as e:
            logger.error(f"TOON interception failed: {e}")
            interception_result['error'] = str(e)
            return data, interception_result
    
    def should_convert_to_toon(self, data: Any, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Determine if data should be converted to TOON format"""
        analysis = {
            'data_type': type(data).__name__,
            'data_size': 0,
            'complexity': 'simple',
            'conversion_potential': 0.0,
            'recommendation': 'no_conversion'
        }
        
        if not isinstance(data, (dict, list)):
            analysis['recommendation'] = 'not_convertible'
            return False, analysis
        
        try:
            # Calculate data size and complexity
            data_str = json.dumps(data, separators=(',', ':'))
            analysis['data_size'] = len(data_str)
            
            # Analyze structure for TOON suitability
            structure_analysis = self.analyze_structure_for_toon(data)
            analysis.update(structure_analysis)
            
            # Calculate conversion potential
            if structure_analysis['suitability_score'] > 0.3:
                # Perform actual conversion analysis
                from toon_format import analyze_tokens
                
                token_analysis = analyze_tokens(data)
                analysis['token_analysis'] = token_analysis
                
                if token_analysis['recommended'] and token_analysis['savings_percent'] >= self.config.get('minSavingsPercent', 15):
                    analysis['recommendation'] = 'convert_to_toon'
                    return True, analysis
            
            analysis['recommendation'] = 'no_conversion'
            return False, analysis
            
        except Exception as e:
            logger.warning(f"TOON analysis failed: {e}")
            analysis['error'] = str(e)
            return False, analysis
    
    def analyze_structure_for_toon(self, data: Any) -> Dict[str, Any]:
        """Analyze data structure for TOON suitability"""
        analysis = {
            'suitability_score': 0.0,
            'structure_type': 'unknown',
            'nesting_depth': 0,
            'uniqueness_score': 0.0,
            'table_suitability': 0.0,
            'reasons': []
        }
        
        def analyze_structure(data, depth=0, parent_path=''):
            nonlocal analysis
            
            if depth > analysis['nesting_depth']:
                analysis['nesting_depth'] = depth
            
            if isinstance(data, dict):
                if not data:
                    return
                
                # Check for table-like structure
                if all(isinstance(v, (str, int, float, bool)) for v in data.values()):
                    analysis['table_suitability'] += 0.3 * len(data)
                    analysis['reasons'].append(f'Dict with {len(data)} simple values')
                
                # Check for mixed types
                value_types = set(type(v).__name__ for v in data.values())
                if len(value_types) == 1 and 'str' in value_types:
                    analysis['uniqueness_score'] += 0.2
                    analysis['reasons'].append('Uniform string values')
                
                # Recursively analyze nested structures
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        analyze_structure(value, depth + 1, f"{parent_path}.{key}")
                
            elif isinstance(data, list):
                if not data:
                    return
                
                # Check for array of similar objects (ideal for TOON)
                if all(isinstance(item, dict) for item in data):
                    if data:
                        # Check if all dicts have similar structure
                        first_keys = set(data[0].keys())
                        similar_structure = all(set(item.keys()) == first_keys for item in data[1:max(1, len(data)//2)])
                        
                        if similar_structure:
                            analysis['suitability_score'] += 0.5 * min(1.0, len(data) / 10)
                            analysis['reasons'].append(f'Array of {len(data)} similar dicts')
                            analysis['structure_type'] = 'table_like'
                
                # Check for simple arrays
                if all(isinstance(item, (str, int, float, bool)) for item in data):
                    analysis['suitability_score'] += 0.2
                    analysis['reasons'].append(f'Array of {len(data)} simple values')
                
                # Recursively analyze nested structures
                for item in data[:5]:  # Sample first 5 items
                    if isinstance(item, (dict, list)):
                        analyze_structure(item, depth + 1, f"{parent_path}[item]")
        
        analyze_structure(data)
        
        # Calculate overall suitability
        if analysis['nesting_depth'] <= 2:
            analysis['suitability_score'] += 0.3
            analysis['reasons'].append('Shallow nesting depth')
        
        # Adjust score based on size
        if analysis['data_size'] > 500:
            analysis['suitability_score'] += 0.2
            analysis['reasons'].append('Large data size')
        elif analysis['data_size'] < 100:
            analysis['suitability_score'] -= 0.1
        
        analysis['suitability_score'] = min(1.0, analysis['suitability_score'])
        
        if analysis['suitability_score'] < 0.1 and analysis['nesting_depth'] > 3:
            analysis['structure_type'] = 'deeply_nested'
            analysis['reasons'].append('Deep nesting reduces TOON efficiency')
        
        return analysis
    
    def convert_to_toon(self, data: Any, context: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        """Convert data to TOON format with full analysis"""
        conversion_info = {
            'original_size': len(json.dumps(data)),
            'toon_size': 0,
            'tokens_saved': 0,
            'compression_ratio': 0.0,
            'optimizations': [],
            'conversion_time': 0.0,
            'success': False
        }
        
        try:
            start_time = time.time()
            
            # Convert using TOON format
            from toon_format import encode_toon, analyze_tokens
            
            toon_data = encode_toon(data)
            
            # Analyze conversion
            token_analysis = analyze_tokens(data)
            
            end_time = time.time()
            
            conversion_info['toon_size'] = len(toon_data)
            conversion_info['tokens_saved'] = token_analysis['tokens_saved']
            conversion_info['compression_ratio'] = token_analysis['savings_percent'] / 100
            conversion_info['conversion_time'] = end_time - start_time
            conversion_info['success'] = True
            
            # Add optimizations applied
            if self.config.get('intelligentTruncation', True):
                conversion_info['optimizations'].append('intelligent_truncation')
            
            if self.config.get('contextOptimization', True):
                conversion_info['optimizations'].append('context_optimization')
            
            # Cache the conversion
            if self.config.get('tokenAware', True):
                self.toon_cache.cache_conversion(data, toon_data, conversion_info)
            
            result_data = toon_data
            
        except Exception as e:
            logger.error(f"TOON conversion failed: {e}")
            conversion_info['error'] = str(e)
            result_data = data
        
        return result_data, conversion_info
    
    def update_conversion_stats(self, conversion_info: Dict[str, Any]):
        """Update conversion statistics"""
        self.conversion_stats['total_conversions'] += 1
        self.conversion_stats['tokens_saved'] += conversion_info.get('tokens_saved', 0)
        self.conversion_stats['last_conversion'] = datetime.now().isoformat()
        
        if self.conversion_stats['total_conversions'] > 0:
            avg_savings = self.conversion_stats['tokens_saved'] / self.conversion_stats['total_conversions']
            self.conversion_stats['conversion_rate'] = avg_savings
    
    def background_processor(self):
        """Background processing for TOON operations"""
        while True:
            try:
                # Process conversion queue
                if not self.conversion_queue.empty():
                    for _ in range(min(5, self.conversion_queue.qsize())):
                        task = self.conversion_queue.get_nowait()
                        self.process_background_conversion(task)
                
                # Process optimization queue
                if not self.optimization_queue.empty():
                    for _ in range(min(3, self.optimization_queue.qsize())):
                        task = self.optimization_queue.get_nowait()
                        self.process_background_optimization(task)
                
                # Periodic maintenance
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Background processing error: {e}")
                time.sleep(30)
    
    def process_background_conversion(self, task: Dict[str, Any]):
        """Process background conversion task"""
        try:
            data = task['data']
            context = task.get('context', {})
            
            # Perform conversion
            result_data, result_info = self.intercept_all_data(data, context)
            
            # Store result if a callback is provided
            if 'callback' in task:
                task['callback'](result_data, result_info)
                
        except Exception as e:
            logger.error(f"Background conversion task failed: {e}")
    
    def process_background_optimization(self, task: Dict[str, Any]):
        """Process background optimization task"""
        try:
            optimization_type = task.get('type', 'general')
            
            if optimization_type == 'cache_cleanup':
                self.toon_cache.cleanup()
            elif optimization_type == 'stats_update':
                self.update_statistics()
            elif optimization_type == 'file_scan':
                self.scan_and_optimize_files(task.get('directory', ''))
                
        except Exception as e:
            logger.error(f"Background optimization task failed: {e}")
    
    def scan_and_optimize_files(self, directory: str):
        """Scan directory and optimize eligible files"""
        if not directory:
            directory = str(self.factory_path)
        
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return
        
        # Find JSON files eligible for TOON conversion
        json_files = list(dir_path.rglob('*.json'))
        
        for json_file in json_files:
            try:
                self.optimize_file_if_beneficial(json_file)
            except Exception as e:
                logger.warning(f"Failed to optimize {json_file}: {e}")
    
    def optimize_file_if_beneficial(self, file_path: Path):
        """Optimize file if TOON conversion is beneficial"""
        try:
            # Skip system files and already processed files
            if any(pattern in str(file_path) for pattern in ['settings.json', 'auth.json', '.toon']):
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if conversion is beneficial
            context = {'file_path': str(file_path), 'source': 'file_scan'}
            
            should_convert, analysis = self.should_convert_to_toon(data, context)
            
            if should_convert:
                # Convert and save TOON version
                toon_data, conversion_info = self.convert_to_toon(data, context)
                
                # Save optimized file
                toon_path = file_path.with_suffix('.toon')
                toon_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(toon_path, 'w') as f:
                    f.write(toon_data)
                
                logger.info(f"Optimized {file_path} -> {toon_path} (saved {conversion_info['tokens_saved']} tokens)")
        
        except Exception as e:
            logger.warning(f"File optimization failed for {file_path}: {e}")
    
    def update_statistics(self):
        """Update system statistics"""
        stats = self.get_system_statistics()
        
        # Store statistics for monitoring
        stats_file = self.factory_path / 'logs' / 'toon_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'conversion_stats': self.conversion_stats,
            'cache_stats': self.toon_cache.get_statistics(),
            'config': self.config,
            'system_timestamp': datetime.now().isoformat(),
            'active_conversions': self.conversion_queue.qsize()
        }
    
    def intercept_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Intercept and optimize prompts with TOON"""
        if not self.config.get('optimizePrompts', True):
            return prompt
        
        try:
            # Analyze prompt for TOON opportunities
            prompt_data = {'prompt': prompt, 'context': context}
            
            optimized_prompt, interception_info = self.intercept_all_data(prompt_data, context)
            
            if interception_info['toon_applied']:
                # Convert back to string for prompt
                if isinstance(optimized_prompt, str):
                    result = optimized_prompt
                else:
                    result = prompt  # Fallback
                
                logger.debug(f"Prompt optimized: saved {interception_info['tokens_saved']} tokens")
                return result
            
            return prompt
            
        except Exception as e:
            logger.error(f"Prompt interception failed: {e}")
            return prompt
    
    def intercept_response(self, response: str, context: Dict[str, Any]) -> str:
        """Intercept and optimize responses with TOON"""
        if not self.config.get('optimizeResponses', True):
            return response
        
        try:
            # For responses, TOON is less applicable, but we can optimize internal representation
            response_data = {'response': response, 'context': context, 'optimization': True}
            
            # Just analyze and track, don't convert strings
            analysis = self.should_convert_to_toon(response_data, context)
            
            # For large responses, consider compression
            if len(response) > 10000:
                # Could apply intelligent response summarization
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"Response interception failed: {e}")
            return response
    
    def queue_background_conversion(self, data: Any, context: Dict[str, Any], callback=None):
        """Queue data for background TOON conversion"""
        task = {
            'data': data,
            'context': context,
            'callback': callback,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.conversion_queue.put_nowait(task)
        except queue.Full:
            logger.warning("TOON conversion queue full, dropping task")
    
    def queue_background_optimization(self, optimization_type: str, **kwargs):
        """Queue background optimization task"""
        task = {
            'type': optimization_type,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        try:
            self.optimization_queue.put_nowait(task)
        except queue.Full:
            logger.warning("TOON optimization queue full, dropping task")

class TOONInterceptor:
    """Handles TOON interception for all data flows"""
    
    def __init__(self, core_system):
        self.core = core_system
        self.interception_stats = {
            'total_interceptions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0
        }
    
    def intercept_agent_execution(self, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        """Intercept agent execution data"""
        self.interception_stats['total_interceptions'] += 1
        
        try:
            # Check if agent data should be processed through TOON
            should_intercept = self.should_intercept_agent(agent_input)
            
            if should_intercept:
                # Process key data through TOON
                processed_input, interception_info = self.core.intercept_all_data(
                    agent_input, {'source': 'agent_execution'}
                )
                
                self.interception_stats['successful_conversions'] += 1
                return processed_input
            
            return agent_input
            
        except Exception as e:
            logger.error(f"Agent interception failed: {e}")
            self.interception_stats['failed_conversions'] += 1
            return agent_input
    
    def should_intercept_agent(self, agent_input: Dict[str, Any]) -> bool:
        """Determine if agent input should be intercepted"""
        # Check for TOON-aware agents
        agent_name = agent_input.get('agent_type', '')
        
        toon_aware_agents = [
            'toon_integration', 'nested_learning', 'claude_factory_sync',
            'claude_sync', 'auto_sync_daemon'
        ]
        
        if agent_name in toon_aware_agents:
            return True
        
        # Check for large data payloads
        prompt = agent_input.get('prompt', '')
        if len(prompt) > 1000:
            return True
        
        # Check for rich context
        context = agent_input.get('context', {})
        if len(json.dumps(context)) > 500:
            return True
        
        return False

class TOONOptimizer:
    """Handles intelligent optimization of TOON-processed data"""
    
    def __init__(self, core_system):
        self.core = core_system
        self.optimization_strategies = {
            'context_compression': self.optimize_context_compression,
            'cache_optimization': self.optimize_cache_access,
            'memory_efficiency': self.optimize_memory_usage
        }
    
    def optimize_context(self, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize data for specific context"""
        result = {
            'data': data,
            'optimized': False,
            'optimizations': []
        }
        
        # Apply context-specific optimizations
        for strategy_name, strategy_func in self.optimization_strategies.items():
            try:
                optimized_data = strategy_func(data, context)
                if optimized_data is not None:
                    result['data'] = optimized_data
                    result['optimized'] = True
                    result['optimizations'].append(strategy_name)
            except Exception as e:
                logger.warning(f"Optimization {strategy_name} failed: {e}")
        
        return result
    
    def optimize_context_compression(self, data: Any, context: Dict[str, Any]) -> Any:
        """Apply intelligent context compression"""
        if isinstance(data, str) and len(data) > 1000:
            # Intelligent truncation for long strings
            return data[:800] + '...' if len(data) > 900 else data
        
        return data
    
    def optimize_cache_access(self, data: Any, context: Dict[str, Any]) -> Any:
        """Optimize for cache access patterns"""
        # This would implement cache-aware optimizations
        return data
    
    def optimize_memory_usage(self, data: Any, context: Dict[str, Any]) -> Any:
        """Optimize for memory efficiency"""
        # This would implement memory-efficient representations
        return data

class TOONCache:
    """Intelligent caching system for TOON conversions"""
    
    def __init__(self, core_system):
        self.core = core_system
        self.conversion_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'size': 0,
            'max_size': 1000
        }
    
    def cache_conversion(self, original_data: Any, toon_data: Any, conversion_info: Dict[str, Any]):
        """Cache a successful conversion"""
        # Generate cache key from original data
        cache_key = str(hash(json.dumps(original_data, sort_keys=True)))
        
        # Check cache size limits
        if len(self.conversion_cache) >= self.cache_stats['max_size']:
            # Remove oldest entries
            oldest_keys = list(self.conversion_cache.keys())[:100]
            for key in oldest_keys:
                del self.conversion_cache[key]
        
        # Store cached conversion
        self.conversion_cache[cache_key] = {
            'toon_data': toon_data,
            'conversion_info': conversion_info,
            'timestamp': datetime.now().isoformat()
        }
        
        self.cache_stats['size'] = len(self.conversion_cache)
    
    def get_cached_conversion(self, original_data: Any) -> Optional[Dict[str, Any]]:
        """Get cached conversion if available"""
        cache_key = str(hash(json.dumps(original_data, sort_keys=True)))
        
        if cache_key in self.conversion_cache:
            self.cache_stats['hits'] += 1
            return self.conversion_cache[cache_key]
        
        self.cache_stats['misses'] += 1
        return None
    
    def cleanup(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        
        expired_keys = []
        for key, value in self.conversion_cache.items():
            try:
                timestamp = datetime.fromisoformat(value['timestamp'])
                if (current_time - timestamp).total_seconds() > 3600:  # 1 hour
                    expired_keys.append(key)
            except Exception:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.conversion_cache[key]
        
        self.cache_stats['size'] = len(self.conversion_cache)
        logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate
        }

# Global TOON core instance
_toon_core_system = None

def get_toon_core_system() -> TOONCoreSystem:
    """Get or create global TOON core system"""
    global _toon_core_system
    if _toon_core_system is None:
        _toon_core_system = TOONCoreSystem()
    return _toon_core_system

# Integration functions
def intercept_data_flow(data: Any, context: Dict[str, Any] = None) -> Tuple[Any, Dict[str, Any]]:
    """Intercept and process any data through TOON core system"""
    core = get_toon_core_system()
    return core.intercept_all_data(data, context)

def optimize_prompt(prompt: str, context: Dict[str, Any] = None) -> str:
    """Optimize prompt through TOON system"""
    core = get_toon_core_system()
    return core.intercept_prompt(prompt, context or {})

def optimize_response(response: str, context: Dict[str, Any] = None) -> str:
    """Optimize response through TOON system"""
    core = get_toon_core_system()
    return core.intercept_response(response, context or {})

def get_toon_statistics() -> Dict[str, Any]:
    """Get TOON system statistics"""
    core = get_toon_core_system()
    return core.get_system_statistics()

if __name__ == "__main__":
    # Test the TOON core system
    core = TOONCoreSystem()
    
    # Test data interception
    test_data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "editor"}
        ]
    }
    
    print("TOON Core System Test:")
    print("Original data:", json.dumps(test_data, indent=2))
    
    # Process through TOON
    optimized_data, info = core.intercept_all_data(test_data, {'test': True'})
    
    print("\nOptimized data:", optimized_data)
    print("\nInterception info:", json.dumps(info, indent=2))
    
    # Get statistics
    stats = core.get_system_statistics()
    print("\nSystem stats:", json.dumps(stats, indent=2, default=str))
