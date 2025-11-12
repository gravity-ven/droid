#!/usr/bin/env python3
"""
Claude Negotiation Skill
Extracted from Claude repositories patterns

Advanced negotiation and conflict resolution capabilities for agent coordination,
resource allocation, and decision making in multi-agent environments.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

class NegotiationStrategy(Enum):
    """Negotiation strategy types"""
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    COMPROMISE = "compromise"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"

class NegotiationStatus(Enum):
    """Negotiation status states"""
    INITIALIZING = "initializing"
    PROPOSING = "proposing"
    COUNTERPROPOSING = "counterproposing"
    CONSENSUS = "consensus"
    DEADLOCK = "deadlock"
    FAILED = "failed"

@dataclass
class NegotiationItem:
    """Individual item in a negotiation"""
    item_id: str
    description: str
    value: float
    priority: float = 1.0
    negotiable: bool = True
    min_acceptable: float = 0.0
    max_acceptable: float = float('inf')

@dataclass
class AgentPosition:
    """Agent's position in negotiation"""
    agent_id: str
    agent_name: str
    items: List[NegotiationItem]
    strategy: NegotiationStrategy = NegotiationStrategy.COLLABORATIVE
    confidence: float = 0.5
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NegotiationProposal:
    """Negotiation proposal"""
    proposal_id: str
    proposing_agent: str
    timestamp: datetime
    items: List[NegotiationItem]
    total_value: float
    reasoning: str
    accept_deadline: Optional[datetime] = None

class ClaudeNegotiationSkill:
    """
    Advanced negotiation skill for Claude agents
    Features:
    - Multi-agent negotiation coordination
    - Strategy selection and adaptation
    - Issue identification and prioritization
    - Consensus building mechanisms
    - Conflict resolution patterns
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.active_negotiations = {}
        self.completed_negotiations = []
        self.agent_profiles = {}
        
        # Negotiation parameters
        self.max_negotiation_rounds = self.config.get("max_rounds", 10)
        self.consensus_threshold = self.config.get("consensus_threshold", 0.8)
        self.deadlock_timeout = self.config.get("deadlock_timeout", 300)  # seconds
        
    def initialize_negotiation(self, 
                               negotiation_id: str,
                               participants: List[str],
                               items: List[NegotiationItem],
                               context: Optional[Dict] = None) -> Dict:
        """Initialize a new negotiation between agents"""
        
        negotiation = {
            "negotiation_id": negotiation_id,
            "status": NegotiationStatus.INITIALIZING.value,
            "participants": participants,
            "items": [item.__dict__ for item in items],
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "rounds": [],
            "proposals": [],
            "decisions": {},
            "current_round": 0
        }
        
        self.active_negotiations[negotiation_id] = negotiation
        
        # Initialize participant positions
        for participant in participants:
            self._initialize_participant_position(negotiation_id, participant, items)
        
        negotiation["status"] = NegotiationStatus.PROPOSING.value
        
        logging.info(f"Initialized negotiation {negotiation_id} with {len(participants)} participants")
        
        return {
            "negotiation_id": negotiation_id,
            "status": "initialized",
            "participants": len(participants),
            "items": len(items)
        }
    
    def _initialize_participant_position(self, negotiation_id: str, agent_id: str, items: List[NegotiationItem]):
        """Initialize agent's starting position in negotiation"""
        
        # Get agent profile or create default
        profile = self.agent_profiles.get(agent_id, {
            "preferred_strategy": "collaborative",
            "risk_tolerance": 0.5,
            "communication_style": "formal",
            "decision_speed": "moderate"
        })
        
        # Create initial position based on items and agent profile
        position_items = []
        for item in items:
            # Adjust item value based on agent preferences
            adjusted_value = self._adjust_item_value(item, profile)
            
            position_item = NegotiationItem(
                item_id=item.item_id,
                description=item.description,
                value=adjusted_value,
                priority=item.priority,
                negotiable=item.negotiable,
                min_acceptable=item.min_acceptable,
                max_acceptable=item.max_acceptable
            )
            position_items.append(position_item)
        
        position = AgentPosition(
            agent_id=agent_id,
            agent_name=agent_id,  # In real implementation, would map to actual name
            items=position_items,
            strategy=NegotiationStrategy(profile.get("preferred_strategy", "collaborative")),
            confidence=profile.get("risk_tolerance", 0.5)
        )
        
        if "participants" not in self.active_negotiations[negotiation_id]:
            self.active_negotiations[negotiation_id]["participants"] = {}
        
        self.active_negotiations[negotiation_id]["participants"][agent_id] = position
        
        return position
    
    def _adjust_item_value(self, item: NegotiationItem, profile: Dict) -> float:
        """Adjust item value based on agent profile"""
        base_value = item.value
        
        # Adjust based on priority weighting
        if profile.get("priority_focus", "balanced") == "high":
            return base_value * (1 + item.priority * 0.2)
        elif profile.get("priority_focus", "balanced") == "low":
            return base_value * (1 - item.priority * 0.1)
        
        return base_value
    
    def submit_proposal(self, negotiation_id: str, agent_id: str, 
                       proposal_items: List[NegotiationItem], 
                       reasoning: str) -> Dict:
        """Submit a proposal from an agent"""
        
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Validate proposal
        validation_result = self._validate_proposal(negotiation_id, agent_id, proposal_items)
        if not validation_result["valid"]:
            return {"error": "Invalid proposal", "reason": validation_result["reason"]}
        
        # Create proposal
        proposal = NegotiationProposal(
            proposal_id=f"{agent_id}_round_{negotiation['current_round']}",
            proposing_agent=agent_id,
            timestamp=datetime.now(),
            items=proposal_items,
            total_value=sum(item.value for item in proposal_items),
            reasoning=reasoning
        )
        
        negotiation["proposals"].append(proposal.__dict__)
        
        # Record round activity
        round_data = {
            "round": negotiation["current_round"],
            "agent": agent_id,
            "action": "proposal",
            "proposal_id": proposal.proposal_id,
            "timestamp": datetime.now().isoformat()
        }
        negotiation["rounds"].append(round_data)
        
        logging.info(f"Agent {agent_id} submitted proposal {proposal.proposal_id} in {negotiation_id}")
        
        return {
            "proposal_id": proposal.proposal_id,
            "status": "submitted",
            "total_value": proposal.total_value
        }
    
    def _validate_proposal(self, negotiation_id: str, agent_id: str, 
                          proposal_items: List[NegotiationItem]) -> Dict:
        """Validate proposal against constraints"""
        
        # Get agent's original position
        negotiation = self.active_negotiations[negotiation_id]
        positions = negotiation.get("positions", {})
        
        if agent_id not in positions:
            return {"valid": False, "reason": "Agent not in negotiation"}
        
        # Check if proposer is part of negotiation
        if agent_id not in negotiation["participants"]:
            return {"valid": False, "reason": "Agent not authorized"}
        
        # Check minimum acceptable values
        for item in proposal_items:
            if not item.negotiable:
                continue
                
            if item.value < item.min_acceptable:
                return {
                    "valid": False,
                    "reason": f"Item {item.item_id} value below minimum acceptable"
                }
        
        return {"valid": True}
    
    def evaluate_proposals(self, negotiation_id: str) -> Dict:
        """Evaluate current proposals and determine next steps"""
        
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}
        
        negotiation = self.active_negotiations[negotiation_id]
        proposals = negotiation["proposals"]
        
        if len(proposals) < len(negotiation["participants"]):
            return {"status": "waiting_for_proposals", "received": len(proposals)}
        
        # Analyze proposals for consensus
        consensus_analysis = self._analyze_consensus(proposals)
        
        if consensus_analysis["consensus_score"] >= self.consensus_threshold:
            # Successful negotiation
            return self._finalize_negotiation(negotiation_id, consensus_analysis)
        else:
            # Continue negotiation
            return self._continue_negotiation(negotiation_id, consensus_analysis)
    
    def _analyze_consensus(self, proposals: List[Dict]) -> Dict:
        """Analyze proposals to determine level of consensus"""
        
        if len(proposals) < 2:
            return {"consensus_score": 0.0, "reason": "insufficient_proposals"}
        
        # Calculate value variance
        values = [p["total_value"] for p in proposals]
        value_variance = self._calculate_variance(values)
        value_mean = sum(values) / len(values)
        
        # Check for clustering around similar values
        if value_variance < (value_mean * 0.1):  # Within 10% of mean
            consensus_score = 0.9
        elif value_variance < (value_mean * 0.2):  # Within 20% of mean
            consensus_score = 0.7
        elif value_variance < (value_mean * 0.3):  # Within 30% of mean
            consensus_score = 0.5
        else:
            consensus_score = 0.2
        
        # Check for deadlock (no movement proposals)
        movement_analysis = self._analyze_proposal_movement(proposals)
        
        return {
            "consensus_score": consensus_score,
            "value_variance": value_variance,
            "value_mean": value_mean,
            "movement_detected": movement_analysis["movement_detected"],
            "stall_detected": movement_analysis["stall_detected"],
            "recommendation": self._get_consensus_recommendation(consensus_score, movement_analysis)
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) == 0:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _analyze_proposal_movement(self, proposals: List[Dict]) -> Dict:
        """Analyze if proposals are making constructive progress"""
        movement_detected = False
        stall_detected = False
        
        # In a real implementation, this would compare with previous proposals
        # For now, check if all proposals are identical (stall)
        if len(proposals) > 1:
            first_total = proposals[0]["total_value"]
            all_identical = all(p["total_value"] == first_total for p in proposals)
            
            if all_identical:
                stall_detected = True
            else:
                movement_detected = True
        
        return {
            "movement_detected": movement_detected,
            "stall_detected": stall_detected
        }
    
    def _get_consensus_recommendation(self, consensus_score: float, movement_analysis: Dict) -> str:
        """Get recommendation based on consensus analysis"""
        if consensus_score >= self.consensus_threshold:
            return "finalize"
        elif movement_analysis["stall_detected"]:
            return "intervention_needed"
        elif consensus_score >= 0.5:
            return "continue_negotiation"
        else:
            return "mediation_needed"
    
    def _finalize_negotiation(self, negotiation_id: str, consensus_analysis: Dict) -> Dict:
        """Finalize successful negotiation"""
        
        negotiation = self.active_negotiations[negotiation_id]
        negotiation["status"] = NegotiationStatus.CONSENSUS.value
        negotiation["consensus_score"] = consensus_analysis["consensus_score"]
        negotiation["completed_at"] = datetime.now().isoformat()
        
        # Move to completed negotiations
        self.completed_negotiations.append(negotiation)
        del self.active_negotiations[negotiation_id]
        
        return {
            "negotiation_id": negotiation_id,
            "status": "completed",
            "consensus_score": consensus_analysis["consensus_score"],
            "outcome": "success"
        }
    
    def _continue_negotiation(self, negotiation_id: str, consensus_analysis: Dict) -> Dict:
        """Continue negotiation with next round"""
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Increment round
        negotiation["current_round"] += 1
        
        # Check for deadlock
        if negotiation["current_round"] >= self.max_negotiation_rounds:
            return self._handle_deadlock(negotiation_id)
        
        negotiation["status"] = NegotiationStatus.COUNTERPROPOSING.value
        
        return {
            "negotiation_id": negotiation_id,
            "status": "continuing",
            "current_round": negotiation["current_round"],
            "recommendation": consensus_analysis["recommendation"]
        }
    
    def _handle_deadlock(self, negotiation_id: str) -> Dict:
        """Handle negotiation deadlock"""
        
        negotiation = self.active_negotiations[negotiation_id]
        negotiation["status"] = NegotiationStatus.DEADLOCK.value
        negotiation["deadlock_at"] = datetime.now().isoformat()
        
        return {
            "negotiation_id": negotiation_id,
            "status": "deadlock",
            "reason": f"Max rounds ({self.max_negotiation_rounds}) reached",
            "recommendation": "mediation_or_abandon"
        }
    
    def mediate_negotiation(self, negotiation_id: str, 
                           mediator_id: str,
                           mediation_strategy: str = "compromise") -> Dict:
        """Mediate a stuck negotiation"""
        
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Analyze current positions
        positions = self._extract_current_positions(negotiation_id)
        
        # Generate mediation proposal
        mediation_proposal = self._generate_mediation_proposal(
            positions, 
            mediation_strategy
        )
        
        # Record mediation
        mediation_record = {
            "mediator_id": mediator_id,
            "strategy": mediation_strategy,
            "timestamp": datetime.now().isoformat(),
            "proposal": mediation_proposal
        }
        
        if "mediations" not in negotiation:
            negotiation["mediations"] = []
        
        negotiation["mediations"].append(mediation_record)
        
        return {
            "negotiation_id": negotiation_id,
            "mediation_initiated": True,
            "mediation_proposal": mediation_proposal
        }
    
    def _extract_current_positions(self, negotiation_id: str) -> List[Dict]:
        """Extract current positions from negotiation"""
        
        negotiation = self.active_negotiations[negotiation_id]
        positions = []
        
        # Get latest proposal from each participant
        latest_proposals = {}
        for proposal in negotiation["proposals"]:
            agent = proposal["proposing_agent"]
            if agent not in latest_proposals or proposal["timestamp"] > latest_proposals[agent]["timestamp"]:
                latest_proposals[agent] = proposal
        
        for agent_id, proposal in latest_proposals.items():
            positions.append({
                "agent": agent_id,
                "items": proposal["items"],
                "total_value": proposal["total_value"],
                "reasoning": proposal.get("reasoning", "")
            })
        
        return positions
    
    def _generate_mediation_proposal(self, positions: List[Dict], strategy: str) -> Dict:
        """Generate mediation proposal based on strategy"""
        
        if strategy == "compromise":
            return self._compromise_mediates(positions)
        elif strategy == "split_difference":
            return self._split_difference_mediates(positions)
        elif strategy == "priority_based":
            return self._priority_based_mediates(positions)
        else:
            return self._fair_distribution_mediates(positions)
    
    def _compromise_mediates(self, positions: List[Dict]) -> Dict:
        """Generate compromise mediation proposal"""
        
        # Calculate average of all positions
        total_values = [p["total_value"] for p in positions]
        compromise_value = sum(total_values) / len(total_values)
        
        # Adjust items proportionally
        if positions:
            base_items = positions[0]["items"]
            mediation_items = []
            
            for item in base_items:
                # Find corresponding item in each position and average the values
                values = []
                for pos in positions:
                    for pos_item in pos["items"]:
                        if pos_item["item_id"] == item["item_id"]:
                            values.append(pos_item["value"])
                            break
                
                if values:
                    avg_value = sum(values) / len(values)
                    mediation_item = {
                        "item_id": item["item_id"],
                        "description": item["description"],
                        "value": avg_value,
                        "priority": item["priority"],
                        "negotiable": item["negotiable"]
                    }
                    mediation_items.append(mediation_item)
            
            return {
                "items": mediation_items,
                "total_value": sum(item["value"] for item in mediation_items),
                "strategy": "compromise",
                "reasoning": "Compromise: Average of all positions"
            }
        
        return {"items": [], "total_value": 0, "strategy": "compromise"}
    
    def _split_difference_mediates(self, positions: List[Dict]) -> Dict:
        """Split the difference mediation"""
        
        # Find min and max total values and take midpoint
        total_values = [p["total_value"] for p in positions]
        min_value = min(total_values)
        max_value = max(total_values)
        midpoint_value = (min_value + max_value) / 2
        
        return {
            "items": [],  # Would need more complex item-level logic
            "total_value": midpoint_value,
            "strategy": "split_difference",
            "reasoning": "Split difference: Midpoint between min and max positions"
        }
    
    def _priority_based_mediates(self, positions: List[Dict]) -> Dict:
        """Priority-based mediation"""
        
        # Give more weight to higher priority items
        if not positions:
            return {"items": [], "total_value": 0, "strategy": "priority_based"}
        
        # Combine items with priority weighting
        all_items = {}
        
        for position in positions:
            for item in position["items"]:
                item_id = item["item_id"]
                item_priority = item["priority"]
                item_value = item["value"]
                
                if item_id not in all_items:
                    all_items[item_id] = {
                        "description": item["description"],
                        "values": [],
                        "priorities": [],
                        "negotiable": item["negotiable"]
                    }
                
                all_items[item_id]["values"].append(item_value)
                all_items[item_id]["priorities"].append(item_priority)
        
        # Calculate weighted average for each item
        mediation_items = []
        for item_id, item_data in all_items.items():
            # Weight by priority
            weighted_sum = sum(v * p for v, p in zip(item_data["values"], item_data["priorities"]))
            priority_sum = sum(item_data["priorities"])
            weighted_value = weighted_sum / priority_sum if priority_sum > 0 else 0
            
            mediation_item = {
                "item_id": item_id,
                "description": item_data["description"],
                "value": weighted_value,
                "priority": sum(item_data["priorities"]) / len(item_data["priorities"]),
                "negotiable": item_data["negotiable"]
            }
            mediation_items.append(mediation_item)
        
        return {
            "items": mediation_items,
            "total_value": sum(item["value"] for item in mediation_items),
            "strategy": "priority_based",
            "reasoning": "Priority-based: Higher priority items given more weight"
        }
    
    def _fair_distribution_mediates(self, positions: List[Dict]) -> Dict:
        """Fair distribution mediation"""
        
        # Ensure each agent gets a fair share
        if not positions:
            return {"items": [], "total_value": 0, "strategy": "fair_distribution"}
        
        # Calculate total value and divide equally
        total_values = [p["total_value"] for p in positions]
        total_sum = sum(total_values)
        fair_share = total_sum / len(positions)
        
        return {
            "items": [],  # Would need complex item distribution logic
            "total_value": fair_share,
            "strategy": "fair_distribution",
            "reasoning": "Fair distribution: Equal share for all participants"
        }
    
    def get_negotiation_status(self, negotiation_id: str) -> Dict:
        """Get current status of a negotiation"""
        
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            return {
                "negotiation_id": negotiation_id,
                "status": negotiation["status"],
                "current_round": negotiation["current_round"],
                "participants": len(negotiation.get("participants", [])),
                "proposals_count": len(negotiation.get("proposals", [])),
                "created_at": negotiation["created_at"]
            }
        else:
            # Check completed negotiations
            for completed in self.completed_negotiations:
                if completed["negotiation_id"] == negotiation_id:
                    return {
                        "negotiation_id": negotiation_id,
                        "status": "completed",
                        "completed_at": completed.get("completed_at"),
                        "consensus_score": completed.get("consensus_score")
                    }
        
        return {"error": "Negotiation not found"}
    
    def get_skill_status(self) -> Dict:
        """Get overall skill status"""
        
        return {
            "active_negotiations": len(self.active_negotiations),
            "completed_negotiations": len(self.completed_negotiations),
            "strategies_available": [s.value for s in NegotiationStrategy],
            "status_states": [s.value for s in NegotiationStatus],
            "max_negotiation_rounds": self.max_negotiation_rounds,
            "consensus_threshold": self.consensus_threshold
        }

# Export for Factory Droid integration
def create_claude_negotiation_skill(config_path: Optional[str] = None):
    """Factory function to create Claude Negotiation Skill"""
    config = None
    if config_path:
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    return ClaudeNegotiationSkill(config)

if __name__ == "__main__":
    # Demo usage
    skill = ClaudeNegotiationSkill()
    
    # Create test items
    items = [
        NegotiationItem("cpu", "Compute resources", 100.0, 1.0, True, 50.0, 150.0),
        NegotiationItem("memory", "Memory allocation", 50.0, 0.8, True, 25.0, 100.0),
        NegotiationItem("storage", "Storage space", 30.0, 0.6, True, 20.0, 60.0)
    ]
    
    # Initialize negotiation
    result = skill.initialize_negotiation(
        "demo_negotiation_1",
        ["agent_a", "agent_b", "agent_c"],
        items,
        {"context": "resource_allocation"}
    )
    
    print("Negotiation Started:", json.dumps(result, indent=2))
    print("\nSkill Status:", json.dumps(skill.get_skill_status(), indent=2))
