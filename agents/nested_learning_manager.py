#!/usr/bin/env python3
"""
Claude Code Nested Learning Manager
Integrates nested learning capabilities into Claude Code for improved long-context processing
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import nested learning system from Factory
sys.path.append(str(Path(os.path.expanduser('~/.factory/agents')))
from nested_learning_system import NestedLearningSystem, LearningTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.claude/logs/nested_learning.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeNestedLearningManager:
    """Manages nested learning integration for Claude Code"""
    
    def __init__(self):
        self.factory_path = Path(os.path.expanduser('~/.factory'))
        self.claude_path = Path(os.path.expanduser('~/.claude'))
        self.learning_system = NestedLearningSystem()
        
        # Claude-specific optimizations
        self.claude_optimizations = {
            'conversation_retention': 10,  # Number of recent conversations to retain
            'code_pattern_memory': 20,      # Number of code patterns to remember
            'context_compression': True,    # Enable context compression for long conversations
            'knowledge_synthesis': True,   # Enable knowledge synthesis across tasks
        }
        
        # Initialize Claude-specific learning levels
        self.initialize_claude_levels()
    
    def initialize_claude_levels(self):
        """Initialize specialized learning levels for Claude Code"""
        try:
            # Claude conversation level
            self.learning_system.create_nested_level(
                level_id=10,
                parent_id=0,
                context_window_size=8192,  # Large context for conversations
                learning_rate=0.005
            )
            
            # Code pattern level
            self.learning_system.create_nested_level(
                level_id=11,
                parent_id=1,  # Child of code generation level
                context_window_size=4096,
                learning_rate=0.015
            )
            
            # Error resolution level
            self.learning_system.create_nested_level(
                level_id=12,
                parent_id=0,
                context_window_size=2048,
                learning_rate=0.025
            )
            
            logger.info("Claude-specific learning levels initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Claude levels: {e}")
    
    def process_claude_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a Claude Code interaction through nested learning"""
        try:
            # Create learning task for Claude interaction
            learning_task = self.create_claude_task(interaction_data)
            
            # Process through nested learning system
            result = self.learning_system.process_learning_task(learning_task.task_data)
            
            # Extract Claude-specific insights
            claude_insights = self.extract_claude_insights(interaction_data, result)
            
            # Apply Claude-specific optimizations
            optimized_result = self.apply_claude_optimizations(result, interaction_data)
            
            # Update conversation context
            self.update_conversation_context(interaction_data, result)
            
            return {
                'learning_result': optimized_result,
                'claude_insights': claude_insights,
                'context_updates': self.get_context_updates(),
                'recommendations': self.get_learning_recommendations(result)
            }
            
        except Exception as e:
            logger.error(f"Failed to process Claude interaction: {e}")
            return {'error': str(e)}
    
    def create_claude_task(self, interaction_data: Dict[str, Any]) -> LearningTask:
        """Create a learning task from Claude interaction data"""
        task_id = f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine interaction type
        interaction_type = self.determine_interaction_type(interaction_data)
        
        # Extract relevant features
        features = self.extract_interaction_features(interaction_data)
        
        task_data = {
            'interaction_type': interaction_type,
            'features': features,
            'raw_data': interaction_data,
            'context_size': self.estimate_claude_context_size(interaction_data),
            'claude_specific': True
        }
        
        return LearningTask(
            task_id=task_id,
            task_type=interaction_type,
            task_data=task_data,
            context_size=len(json.dumps(features)),
            priority=self.calculate_claude_task_priority(interaction_data),
            timestamp=datetime.now(),
            parent_task_ids=[],
            subtask_ids=[]
        )
    
    def determine_interaction_type(self, interaction_data: Dict[str, Any]) -> str:
        """Determine the type of Claude interaction"""
        content = json.dumps(interaction_data).lower()
        
        if 'code' in content or 'script' in content or 'programming' in content:
            return 'claude_code_generation'
        elif 'error' in content or 'debug' in content or 'fix' in content:
            return 'claude_error_resolution'
        elif 'explain' in content or 'understand' in content or 'clarify' in content:
            return 'claude_explanation'
        elif 'refactor' in content or 'optimize' in content or 'improve' in content:
            return 'claude_refactoring'
        elif 'conversation' in content or 'chat' in content or 'dialog' in content:
            return 'claude_conversation'
        else:
            return 'claude_general'
    
    def extract_interaction_features(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract salient features from Claude interaction"""
        features = {
            'timestamp': datetime.now().isoformat(),
            'interaction_length': len(json.dumps(interaction_data))
        }
        
        # Extract code features
        if any(key in interaction_data for key in ['code', 'script', 'function']):
            code_content = self.extract_code_content(interaction_data)
            features['code_features'] = self.analyze_code_features(code_content)
        
        # Extract conversation features
        if 'messages' in interaction_data:
            features['conversation_features'] = self.analyze_conversation_features(interaction_data['messages'])
        
        # Extract error features
        error_content = self.extract_error_content(interaction_data)
        if error_content:
            features['error_features'] = self.analyze_error_features(error_content)
        
        # Extract performance features
        features['performance_indicators'] = self.extract_performance_indicators(interaction_data)
        
        return features
    
    def extract_code_content(self, interaction_data: Dict[str, Any]) -> str:
        """Extract code content from interaction data"""
        code_keys = ['code', 'script', 'function', 'method', 'class', 'program']
        
        for key in code_keys:
            if key in interaction_data:
                return str(interaction_data[key])
        
        # Search in nested structures
        for value in interaction_data.values():
            if isinstance(value, dict):
                for key in code_keys:
                    if key in value:
                        return str(value[key])
            elif isinstance(value, str) and any(code_key in value.lower() for code_key in code_keys):
                return value
        
        return ""
    
    def analyze_code_features(self, code_content: str) -> Dict[str, Any]:
        """Analyze features of code content"""
        features = {
            'language': self.detect_programming_language(code_content),
            'complexity': self.calculate_code_complexity(code_content),
            'patterns': self.extract_code_patterns(code_content),
            'structures': self.identify_code_structures(code_content)
        }
        
        return features
    
    def detect_programming_language(self, code: str) -> str:
        """Detect programming language from code content"""
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code and 'var ' in code:
            return 'javascript'
        elif 'public class ' in code or 'private ' in code:
            return 'java'
        elif '#include' in code and '{' in code:
            return 'c/cpp'
        elif 'fn ' in code and 'let ' in code:
            return 'rust'
        else:
            return 'unknown'
    
    def calculate_code_complexity(self, code: str) -> float:
        """Calculate complexity score for code"""
        # Simple complexity metrics
        complexity_indicators = [
            code.count('if'), code.count('for'), code.count('while'),
            code.count('try'), code.count('catch'), code.count('def'),
            code.count('class'), code.count('function')
        ]
        
        total_indicators = sum(complexity_indicators)
        lines = len(code.split('\n'))
        
        if lines == 0:
            return 0.0
        
        return min(1.0, total_indicators / lines)
    
    def extract_code_patterns(self, code: str) -> List[str]:
        """Extract common programming patterns from code"""
        patterns = []
        
        # Common patterns to look for
        pattern_checks = [
            ('list_comprehension', [x in code for x in ['[x for x in', '[x if x for']]),
            ('error_handling', ['try:' in code, 'except' in code]),
            ('class_definition', ['class ' in code]),
            ('function_definition', ['def ' in code, 'function ' in code]),
            ('recursion', ['return ' + f.split('def ')[1].split('(')[0] for f in code.split('def ')[1:] if 'return ' + f.split('def ')[1].split('(')[0] in code]),
            ('lambda', ['lambda ' in code, '=> ' in code]),
        ]
        
        for pattern_name, checks in pattern_checks:
            if any(checks) if isinstance(checks, list) else checks:
                patterns.append(pattern_name)
        
        return patterns
    
    def identify_code_structures(self, code: str) -> List[str]:
        """Identify code structures"""
        structures = []
        
        if 'class ' in code:
            structures.append('class')
        if 'def ' in code or 'function ' in code:
            structures.append('function')
        if 'import ' in code or 'require ' in code:
            structures.append('imports')
        if 'for ' in code or 'while ' in code:
            structures.append('loops')
        if 'if ' in code:
            structures.append('conditionals')
        if 'try:' in code:
            structures.append('exception_handling')
        
        return structures
    
    def analyze_conversation_features(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation features from messages"""
        features = {
            'message_count': len(messages),
            'conversation_length': sum(len(msg.get('content', '')) for msg in messages),
            'turns': len([msg for msg in messages if msg.get('role') == 'user']),
            'topics': self.extract_conversation_topics(messages),
            'sentiment': self.analyze_conversation_sentiment(messages),
            'complexity': self.calculate_conversation_complexity(messages)
        }
        
        return features
    
    def extract_conversation_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract topics from conversation messages"""
        topics = set()
        
        topic_keywords = {
            'code': ['algorithm', 'function', 'variable', 'class', 'method'],
            'debugging': ['error', 'bug', 'fix', 'issue', 'problem'],
            'optimization': ['improve', 'optimize', 'better', 'performance'],
            'architecture': ['design', 'structure', 'pattern', 'architecture'],
            'data': ['data', 'dataset', 'database', 'storage'],
            'security': ['security', 'auth', 'encryption', 'secure']
        }
        
        all_content = ' '.join(msg.get('content', '') for msg in messages).lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_content for keyword in keywords):
                topics.add(topic)
        
        return list(topics)
    
    def analyze_conversation_sentiment(self, messages: List[Dict[str, Any]]) -> str:
        """Analyze sentiment of conversation"""
        positive_words = ['thanks', 'good', 'great', 'excellent', 'perfect', 'working']
        negative_words = ['error', 'problem', 'wrong', 'broken', 'issue', 'fail']
        
        all_content = ' '.join(msg.get('content', '') for msg in messages).lower()
        
        positive_count = sum(1 for word in positive_words if word in all_content)
        negative_count = sum(1 for word in negative_words if word in all_content)
        
        if positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_conversation_complexity(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate conversation complexity"""
        if not messages:
            return 0.0
        
        # Factors affecting complexity
        avg_message_length = sum(len(msg.get('content', '')) for msg in messages) / len(messages)
        topic_diversity = len(self.extract_conversation_topics(messages))
        technical_terms = sum(1 for msg in messages for word in 
                           ['function', 'algorithm', 'implementation', 'optimization'] 
                           if word in msg.get('content', '').lower())
        
        normalized_length = min(1.0, avg_message_length / 500)
        normalized_diversity = min(1.0, topic_diversity / 5)
        normalized_technical = min(1.0, technical_terms / (len(messages) * 2))
        
        return (normalized_length + normalized_diversity + normalized_technical) / 3
    
    def extract_error_content(self, interaction_data: Dict[str, Any]) -> str:
        """Extract error-related content"""
        error_keys = ['error', 'exception', 'traceback', 'failure', 'issue', 'problem']
        
        for key in error_keys:
            if key in interaction_data:
                return str(interaction_data[key])
        
        return ""
    
    def analyze_error_features(self, error_content: str) -> Dict[str, Any]:
        """Analyze error content features"""
        features = {
            'error_type': self.classify_error_type(error_content),
            'severity': self.estimate_error_severity(error_content),
            'category': self.categorize_error(error_content),
            'context': self.extract_error_context(error_content)
        }
        
        return features
    
    def classify_error_type(self, error: str) -> str:
        """Classify type of error"""
        error_lower = error.lower()
        
        if 'syntax' in error_lower or 'parse' in error_lower:
            return 'syntax'
        elif 'type' in error_lower or 'value' in error_lower:
            return 'data_type'
        elif 'name' in error_lower or 'attribute' in error_lower:
            return 'name'
        elif 'index' in error_lower or 'key' in error_lower:
            return 'index_key'
        elif 'null' in error_lower or 'none' in error_lower:
            return 'null_value'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission'
        elif 'import' in error_lower:
            return 'import_module'
        else:
            return 'unknown'
    
    def estimate_error_severity(self, error: str) -> str:
        """Estimate error severity"""
        severity_keywords = {
            'critical': ['critical', 'fatal', 'panic', 'segmentation fault'],
            'high': ['error', 'exception', 'traceback'],
            'medium': ['warning', 'deprecated'],
            'low': ['info', 'notice']
        }
        
        error_lower = error.lower()
        
        for severity, keywords in severity_keywords.items():
            if any(keyword in error_lower for keyword in keywords):
                return severity
        
        return 'medium'  # Default
    
    def categorize_error(self, error: str) -> str:
        """Categorize error by domain"""
        error_lower = error.lower()
        
        if 'file' in error_lower or 'path' in error_lower:
            return 'file_system'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network'
        elif 'memory' in error_lower or 'allocation' in error_lower:
            return 'memory'
        elif 'syntax' in error_lower:
            return 'syntax'
        elif 'type' in error_lower:
            return 'runtime'
        else:
            return 'general'
    
    def extract_error_context(self, error: str) -> str:
        """Extract context around error"""
        lines = error.split('\n')
        
        # Find line with "error", "exception", etc.
        error_lines = [i for i, line in enumerate(lines) 
                      if any(keyword in line.lower() 
                            for keyword in ['error', 'exception', 'traceback'])]
        
        if error_lines:
            error_line = error_lines[0]
            # Get 3 lines before and after
            start = max(0, error_line - 3)
            end = min(len(lines), error_line + 4)
            return '\n'.join(lines[start:end])
        
        return error[:500]  # Return first 500 chars if no specific context
    
    def extract_performance_indicators(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance indicators from interaction"""
        indicators = {}
        
        # Response time (if available)
        if 'response_time' in interaction_data:
            indicators['response_time'] = interaction_data['response_time']
        
        # Token usage (if available)
        if 'tokens' in interaction_data:
            indicators['token_usage'] = interaction_data['tokens']
        
        # Success/failure indicators
        success_keywords = ['success', 'completed', 'done', 'finished', 'working']
        failure_keywords = ['error', 'fail', 'broken', 'problem', 'issue']
        
        content = json.dumps(interaction_data).lower()
        success_score = sum(1 for word in success_keywords if word in content)
        failure_score = sum(1 for word in failure_keywords if word in content)
        
        indicators['success_indicator'] = success_score / (success_score + failure_score + 1)
        indicators['complexity_score'] = self.calculate_interaction_complexity(interaction_data)
        
        return indicators
    
    def calculate_interaction_complexity(self, interaction_data: Dict[str, Any]) -> float:
        """Calculate overall interaction complexity"""
        factors = []
        
        # Size factor
        size_score = min(1.0, len(json.dumps(interaction_data)) / 10000)
        factors.append(size_score)
        
        # Structure complexity
        structure_score = self.calculate_structure_complexity(interaction_data)
        factors.append(structure_score)
        
        # Content complexity
        content_score = self.calculate_content_complexity(interaction_data)
        factors.append(content_score)
        
        return sum(factors) / len(factors)
    
    def calculate_structure_complexity(self, data: Any, current_depth: int = 0) -> float:
        """Calculate structural complexity of nested data"""
        if current_depth > 5:  # Prevent infinite recursion
            return 1.0
        
        if isinstance(data, dict):
            if not data:
                return 0.0
            child_complexities = [self.calculate_structure_complexity(v, current_depth + 1) 
                                 for v in data.values()]
            return min(1.0, (len(data) + sum(child_complexities)) / 20)
        elif isinstance(data, list):
            if not data:
                return 0.0
            child_complexities = [self.calculate_structure_complexity(item, current_depth + 1) 
                                 for item in data]
            return min(1.0, (len(data) + sum(child_complexities)) / 15)
        else:
            return 0.1  # Small complexity for primitive types
    
    def calculate_content_complexity(self, interaction_data: Dict[str, Any]) -> float:
        """Calculate content complexity based on keywords and patterns"""
        content = json.dumps(interaction_data).lower()
        
        complexity_indicators = [
            'algorithm', 'implementation', 'optimization', 'refactor',
            'architecture', 'design', 'pattern', 'framework'
        ]
        
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in content)
        return min(1.0, indicator_count / len(complexity_indicators))
    
    def estimate_claude_context_size(self, interaction_data: Dict[str, Any]) -> int:
        """Estimate required context size for Claude interaction"""
        base_size = len(json.dumps(interaction_data))
        
        # Multiply by factor based on content type
        if any(key in str(interaction_data).lower() for key in ['code', 'script']):
            return min(8192, base_size * 3)  # Code needs more context
        elif 'conversation' in str(interaction_data).lower():
            return min(4096, base_size * 2)  # Conversation needs moderate context
        else:
            return min(2048, base_size * 1.5)  # Default context
    
    def calculate_claude_task_priority(self, interaction_data: Dict[str, Any]) -> float:
        """Calculate priority for Claude task"""
        base_priority = 0.5
        
        # Adjust based on interaction type
        interaction_type = self.determine_interaction_type(interaction_data)
        type_priorities = {
            'claude_error_resolution': 0.9,
            'claude_code_generation': 0.8,
            'claude_explanation': 0.6,
            'claude_refactoring': 0.7,
            'claude_conversation': 0.5,
            'claude_general': 0.4
        }
        
        base_priority = type_priorities.get(interaction_type, 0.5)
        
        # Adjust based on complexity
        complexity = self.calculate_interaction_complexity(interaction_data)
        base_priority += complexity * 0.2
        
        # Adjust based on error content
        if self.extract_error_content(interaction_data):
            base_priority += 0.2
        
        return min(1.0, base_priority)
    
    def extract_claude_insights(self, interaction_data: Dict[str, Any], 
                              learning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Claude-specific insights from learning result"""
        insights = {
            'interaction_patterns': self.analyze_interaction_patterns(interaction_data),
            'learning_progress': self.analyze_learning_progress(learning_result),
            'optimization_opportunities': self.identify_optimization_opportunities(learning_result),
            'context_recommendations': self.get_context_recommendations(interaction_data, learning_result)
        }
        
        return insights
    
    def analyze_interaction_patterns(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze recurring patterns in interactions"""
        patterns = {
            'common_topics': self.get_common_topics(interaction_data),
            'preferred_formats': self.get_preferred_formats(interaction_data),
            'complexity_trends': self.analyze_complexity_trends(interaction_data)
        }
        
        return patterns
    
    def get_common_topics(self, interaction_data: Dict[str, Any]) -> List[str]:
        """Get commonly discussed topics"""
        # This would typically look at historical data
        # For now, return basic analysis
        topics = []
        
        if 'code' in str(interaction_data).lower():
            topics.append('programming')
        if 'error' in str(interaction_data).lower():
            topics.append('debugging')
        if 'design' in str(interaction_data).lower():
            topics.append('architecture')
        
        return topics
    
    def get_preferred_formats(self, interaction_data: Dict[str, Any]) -> List[str]:
        """Get preferred response formats"""
        preferred = []
        
        if 'example' in str(interaction_data).lower():
            preferred.append('code_examples')
        if 'explain' in str(interaction_data).lower():
            preferred.append('explanations')
        if 'step' in str(interaction_data).lower():
            preferred.append('step_by_step')
        
        return preferred
    
    def analyze_complexity_trends(self, interaction_data: Dict[str, Any]) -> str:
        """Analyze complexity trends"""
        complexity = self.calculate_interaction_complexity(interaction_data)
        
        if complexity > 0.7:
            return 'increasing_complexity'
        elif complexity < 0.3:
            return 'decreasing_complexity'
        else:
            return 'stable_complexity'
    
    def analyze_learning_progress(self, learning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning progress from result"""
        progress = {
            'task_completion': learning_result.get('final_performance', {}).get('overall', 0.0),
            'pathway_efficiency': self.calculate_pathway_efficiency(learning_result),
            'knowledge_retention': self.assess_knowledge_retention(learning_result)
        }
        
        return progress
    
    def calculate_pathway_efficiency(self, learning_result: Dict[str, Any]) -> float:
        """Calculate efficiency of learning pathway"""
        pathway = learning_result.get('pathway', [])
        results = learning_result.get('results', [])
        
        if not pathway or not results:
            return 0.0
        
        # Check if specialized levels were used appropriately
        efficiency = 0.0
        
        # Base efficiency from pathway length (shorter is often better)
        if len(pathway) <= 3:
            efficiency += 0.4
        elif len(pathway) <= 5:
            efficiency += 0.3
        else:
            efficiency += 0.2
        
        # Efficiency from performance at each level
        level_performances = []
        for result in results:
            if 'performance' in result and isinstance(result['performance'], dict):
                avg_performance = sum(result['performance'].values()) / len(result['performance'])
                level_performances.append(avg_performance)
        
        if level_performances:
            efficiency += sum(level_performances) / len(level_performances) * 0.6
        
        return min(1.0, efficiency)
    
    def assess_knowledge_retention(self, learning_result: Dict[str, Any]) -> float:
        """Assess knowledge retention"""
        retention_scores = []
        
        for result in learning_result.get('results', []):
            if 'performance' in result and isinstance(result['performance'], dict):
                retention = result['performance'].get('retention', 0.0)
                retention_scores.append(retention)
        
        if retention_scores:
            return sum(retention_scores) / len(retention_scores)
        
        return 0.0
    
    def identify_optimization_opportunities(self, learning_result: Dict[str, Any]) -> List[str]:
        """Identify opportunities for optimization"""
        opportunities = []
        
        final_performance = learning_result.get('final_performance', {})
        
        # Check for low efficiency
        if final_performance.get('efficiency', 0.0) < 0.7:
            opportunities.append('improve_processing_efficiency')
        
        # Check for low accuracy
        if final_performance.get('accuracy', 0.0) < 0.8:
            opportunities.append('enhance_knowledge_accuracy')
        
        # Check for low retention
        if final_performance.get('retention', 0.0) < 0.6:
            opportunities.append('strengthen_knowledge_retention')
        
        # Check pathway complexity
        pathway = learning_result.get('pathway', [])
        if len(pathway) > 5:
            opportunities.append('optimize_learning_pathway')
        
        return opportunities
    
    def get_context_recommendations(self, interaction_data: Dict[str, Any], 
                                  learning_result: Dict[str, Any]) -> List[str]:
        """Get context management recommendations"""
        recommendations = []
        
        context_size = self.estimate_claude_context_size(interaction_data)
        
        if context_size > 6000:
            recommendations.append('consider_context_compression')
        
        if interaction_data.get('conversation_context'):
            recommendations.append('maintain_conversation_continuity')
        
        if self.extract_code_content(interaction_data):
            recommendations.append('preserve_code_patterns')
        
        # Based on pathway usage
        pathway = learning_result.get('pathway', [])
        if 10 in pathway:  # Conversation level
            recommendations.append('enhance_conversation_memory')
        if 11 in pathway:  # Code pattern level
            recommendations.append('strengthen_code_pattern_recognition')
        
        return recommendations
    
    def apply_claude_optimizations(self, learning_result: Dict[str, Any], 
                                  interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Claude-specific optimizations to learning result"""
        optimized_result = learning_result.copy()
        
        # Apply conversation context optimization
        if self.claude_optimizations['context_compression']:
            optimized_result = self.apply_context_compression(optimized_result)
        
        # Apply knowledge synthesis
        if self.claude_optimizations['knowledge_synthesis']:
            optimized_result = self.apply_knowledge_synthesis(optimized_result)
        
        # Apply Claude-specific learning rate adjustments
        optimized_result = self.apply_claude_learning_adjustments(optimized_result)
        
        return optimized_result
    
    def apply_context_compression(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply context compression for long conversations"""
        # This would implement intelligent context compression
        # For now, just mark that it was applied
        result['applied_optimizations'] = result.get('applied_optimizations', [])
        result['applied_optimizations'].append('context_compression')
        
        return result
    
    def apply_knowledge_synthesis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply knowledge synthesis across learning levels"""
        result['applied_optimizations'] = result.get('applied_optimizations', [])
        result['applied_optimizations'].append('knowledge_synthesis')
        
        return result
    
    def apply_claude_learning_adjustments(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Claude-specific learning adjustments"""
        # Adjust learning rates for Claude-specific levels
        for level_id in [10, 11, 12]:  # Claude-specific levels
            if level_id in self.learning_system.nested_levels:
                level = self.learning_system.nested_levels[level_id]
                
                # Slightly increase learning rate for Claude levels
                if level.learning_rate < 0.02:
                    level.learning_rate *= 1.1
                    level.learning_rate = min(0.02, level.learning_rate)
        
        result['applied_optimizations'] = result.get('applied_optimizations', [])
        result['applied_optimizations'].append('claude_learning_adjustments')
        
        return result
    
    def update_conversation_context(self, interaction_data: Dict[str, Any], 
                                  learning_result: Dict[str, Any]):
        """Update conversation context based on learning"""
        conversation_context_file = self.claude_path / 'state' / 'conversation_context.json'
        
        try:
            # Load existing context
            if conversation_context_file.exists():
                with open(conversation_context_file, 'r') as f:
                    context = json.load(f)
            else:
                context = {'recent_interactions': [], 'learned_patterns': [], 'preferences': {}}
            
            # Add current interaction
            context['recent_interactions'].append({
                'timestamp': datetime.now().isoformat(),
                'interaction_type': self.determine_interaction_type(interaction_data),
                'performance': learning_result.get('final_performance', {}),
                'key_insights': learning_result.get('results', [])
            })
            
            # Keep only recent interactions
            max_interactions = self.claude_optimizations['conversation_retention']
            if len(context['recent_interactions']) > max_interactions:
                context['recent_interactions'] = context['recent_interactions'][-max_interactions:]
            
            # Extract and add learned patterns
            new_patterns = self.extract_learned_patterns(learning_result)
            for pattern in new_patterns:
                if pattern not in context['learned_patterns']:
                    context['learned_patterns'].append(pattern)
            
            # Keep learned patterns bounded
            if len(context['learned_patterns']) > self.claude_optimizations['code_pattern_memory']:
                context['learned_patterns'] = context['learned_patterns'][-self.claude_optimizations['code_pattern_memory']:]
            
            # Save updated context
            conversation_context_file.parent.mkdir(parents=True, exist_ok=True)
            with open(conversation_context_file, 'w') as f:
                json.dump(context, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update conversation context: {e}")
    
    def extract_learned_patterns(self, learning_result: Dict[str, Any]) -> List[str]:
        """Extract patterns learned from the learning result"""
        patterns = []
        
        for result in learning_result.get('results', []):
            if 'knowledge_updates' in result:
                for key, value in result['knowledge_updates'].items():
                    if 'pattern' in key.lower():
                        patterns.append(key)
        
        return patterns
    
    def get_context_updates(self) -> Dict[str, Any]:
        """Get recent context updates"""
        context_file = self.claude_path / 'state' / 'conversation_context.json'
        
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load context updates: {e}")
        
        return {}
    
    def get_learning_recommendations(self, learning_result: Dict[str, Any]) -> List[str]:
        """Get learning recommendations based on results"""
        recommendations = []
        
        final_performance = learning_result.get('final_performance', {})
        
        # Performance-based recommendations
        if final_performance.get('overall', 0.0) < 0.7:
            recommendations.append('focus_on_fundamentals')
        
        if final_performance.get('efficiency', 0.0) < 0.6:
            recommendations.append('context_optimization')
        
        if final_performance.get('retention', 0.0) < 0.5:
            recommendations.append('knowledge_consolidation')
        
        # Pathway-based recommendations
        pathway = learning_result.get('pathway', [])
        
        if 10 in pathway:  # Used conversation level
            recommendations.append('enhance_conversation_continuity')
        
        if 11 in pathway:  # Used code pattern level
            recommendations.append('develop_code_pattern_memory')
        
        if 12 in pathway:  # Used error resolution level
            recommendations.append('improve_error_recognition_capability')
        
        return recommendations

# Integration functions for Claude Code
def process_claude_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a Claude Code interaction through nested learning"""
    manager = ClaudeNestedLearningManager()
    return manager.process_claude_interaction(interaction_data)

def get_claude_learning_status() -> Dict[str, Any]:
    """Get current Claude learning system status"""
    manager = ClaudeNestedLearningManager()
    return manager.learning_system.get_system_status()

if __name__ == "__main__":
    # Test the Claude nested learning manager
    test_interaction = {
        'messages': [
            {'role': 'user', 'content': 'Can you help me debug this Python function?'},
            {'role': 'assistant', 'content': 'I need to see the function code first.'},
            {'role': 'user', 'content': 'Here is the error: ValueError: invalid literal for int() with base 10'}
        ],
        'code': 'def parse_data(data_str):\n    return int(data_str)\n\nresult = parse_data("abc123")',
        'error': 'ValueError: invalid literal for int() with base 10: "abc123"'
    }
    
    manager = ClaudeNestedLearningManager()
    result = manager.process_claude_interaction(test_interaction)
    
    print("Claude Nested Learning Test Results:")
    print(json.dumps(result, indent=2, default=str))
