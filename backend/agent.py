"""
Agent class for AI civilization simulator.
Each agent has personality, goals, memory, and can take autonomous actions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class PersonalityTrait(Enum):
    """Big Five personality traits"""
    OPENNESS = "openness"          # Curiosity, creativity
    CONSCIENTIOUSNESS = "conscientiousness"  # Organization, discipline
    EXTRAVERSION = "extraversion"   # Social engagement
    AGREEABLENESS = "agreeableness"  # Cooperation, trust
    NEUROTICISM = "neuroticism"     # Emotional sensitivity


class ActionType(Enum):
    """Available actions agents can take"""
    MOVE = "move"
    GATHER = "gather"
    CRAFT = "craft"
    COMMUNICATE = "communicate"
    REST = "rest"
    BUILD = "build"
    TEACH = "teach"
    TRADE = "trade"


@dataclass
class Goal:
    """Agent goal with priority and status"""
    description: str
    priority: float  # 0-1, higher = more urgent
    completed: bool = False


@dataclass
class Memory:
    """Agent memory entry"""
    content: str
    timestamp: int  # World tick
    importance: float  # 0-1
    memory_type: str  # episodic, semantic, procedural


@dataclass
class Relationship:
    """Relationship with another agent"""
    agent_id: str
    trust: float = 0.0  # -1 to 1
    friendship: float = 0.0  # 0 to 1
    interactions: int = 0


@dataclass
class Agent:
    """Autonomous agent with personality and memory"""

    # Identity
    id: str
    name: str
    personality: Dict[PersonalityTrait, float]  # Trait -> value (0-1)

    # State
    position: tuple[int, int] = (0, 0)
    health: float = 100.0
    energy: float = 100.0
    inventory: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, float] = field(default_factory=dict)  # skill -> level (0-1)

    # Mental state
    goals: List[Goal] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)

    # Current state
    current_action: Optional[ActionType] = None
    conversation_history: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize agent state to dict"""
        return {
            "id": self.id,
            "name": self.name,
            "personality": {t.value: v for t, v in self.personality.items()},
            "position": self.position,
            "health": self.health,
            "energy": self.energy,
            "inventory": self.inventory,
            "skills": self.skills,
            "goals": [{"description": g.description, "priority": g.priority, "completed": g.completed} for g in self.goals],
            "memories": [{"content": m.content, "timestamp": m.timestamp, "importance": m.importance, "memory_type": m.memory_type} for m in self.memories],
            "relationships": {k: {"trust": v.trust, "friendship": v.friendship, "interactions": v.interactions} for k, v in self.relationships.items()},
            "current_action": self.current_action.value if self.current_action else None,
            "conversation_history": self.conversation_history
        }

    def save_state(self, directory: str):
        """Save agent state to JSON file"""
        filepath = os.path.join(directory, f"agent_{self.id}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_state(cls, filepath: str) -> Agent:
        """Load agent state from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        personality = {PersonalityTrait(k): v for k, v in data["personality"].items()}
        goals = [Goal(**g) for g in data["goals"]]
        memories = [Memory(**m) for m in data["memories"]]
        relationships = {k: Relationship(agent_id=k, **v) for k, v in data["relationships"].items()}
        current_action = ActionType(data["current_action"]) if data["current_action"] else None

        return cls(
            id=data["id"],
            name=data["name"],
            personality=personality,
            position=tuple(data["position"]),
            health=data["health"],
            energy=data["energy"],
            inventory=data["inventory"],
            skills=data["skills"],
            goals=goals,
            memories=memories,
            relationships=relationships,
            current_action=current_action,
            conversation_history=data["conversation_history"]
        )