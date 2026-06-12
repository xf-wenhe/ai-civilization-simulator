"""
Knowledge transfer and teaching system.
Agents can teach skills and share knowledge with each other.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class KnowledgeArtifact:
    """Knowledge that can be transferred"""
    name: str
    category: str  # skill, fact, technique, belief
    content: str
    mastery_level: float  # 0-1, how well the teacher knows it


@dataclass
class TeachingSession:
    """Record of a teaching session"""
    teacher_id: str
    student_id: str
    knowledge: KnowledgeArtifact
    success: bool
    improvement: float  # How much student improved
    timestamp: int


class KnowledgeSystem:
    """Manages knowledge transfer between agents"""

    def __init__(self):
        self.teaching_history: Dict[str, List[TeachingSession]] = {}  # student_id -> sessions
        self.shared_knowledge: Dict[str, KnowledgeArtifact] = {}  # Knowledge name -> artifact

        # Initialize with some base knowledge
        self._init_base_knowledge()

    def _init_base_knowledge(self):
        """Initialize base knowledge artifacts"""

        base_knowledge = [
            KnowledgeArtifact("basic_gathering", "skill", "How to gather food and resources efficiently", 1.0),
            KnowledgeArtifact("tool_crafting", "skill", "Creating simple tools from gathered materials", 0.8),
            KnowledgeArtifact("shelter_building", "skill", "Building basic shelters for protection", 0.7),
            KnowledgeArtifact("social_interaction", "skill", "Communicating effectively with others", 0.6),
            KnowledgeArtifact("exploration", "technique", "Methods for exploring new areas safely", 0.5),
        ]

        for knowledge in base_knowledge:
            self.shared_knowledge[knowledge.name] = knowledge

    def can_agent_teach(self, teacher_id: str, knowledge_name: str, agent_skills: Dict[str, float]) -> bool:
        """Check if agent can teach specific knowledge"""

        # Check if knowledge exists
        if knowledge_name not in self.shared_knowledge:
            return False

        knowledge = self.shared_knowledge[knowledge_name]

        # Check if agent has sufficient skill level
        skill_name = knowledge.category

        if skill_name in agent_skills:
            return agent_skills[skill_name] >= 0.5

        return False

    def teach_knowledge(self, teacher_id: str, student_id: str, knowledge_name: str,
                       teacher_skills: Dict[str, float], student_skills: Dict[str, float],
                       timestamp: int) -> TeachingSession:
        """Teach knowledge from one agent to another"""

        if knowledge_name not in self.shared_knowledge:
            return TeachingSession(
                teacher_id=teacher_id,
                student_id=student_id,
                knowledge=None,
                success=False,
                improvement=0.0,
                timestamp=timestamp
            )

        knowledge = self.shared_knowledge[knowledge_name]

        # Determine if teaching is successful based on teacher skill and student aptitude
        teacher_skill = teacher_skills.get(knowledge.category, 0.0)

        # Success probability based on teacher mastery
        success_prob = teacher_skill * 0.7 + random.uniform(0.1, 0.3)

        success = random.random() < success_prob

        # Calculate improvement if successful
        improvement = 0.0
        if success:
            # Student learns based on teacher skill and random factor
            improvement = teacher_skill * 0.2 + random.uniform(0.05, 0.15)
            improvement = min(improvement, 1.0 - student_skills.get(knowledge.category, 0.0))

        session = TeachingSession(
            teacher_id=teacher_id,
            student_id=student_id,
            knowledge=knowledge,
            success=success,
            improvement=improvement,
            timestamp=timestamp
        )

        # Record in teaching history
        if student_id not in self.teaching_history:
            self.teaching_history[student_id] = []

        self.teaching_history[student_id].append(session)

        return session

    def get_available_knowledge(self) -> List[str]:
        """Get list of available knowledge names"""
        return list(self.shared_knowledge.keys())

    def get_teaching_history(self, agent_id: str) -> List[TeachingSession]:
        """Get agent's teaching/learning history"""
        return self.teaching_history.get(agent_id, [])

    def create_new_knowledge(self, name: str, category: str, content: str, mastery: float):
        """Create new knowledge artifact"""
        artifact = KnowledgeArtifact(name, category, content, mastery)
        self.shared_knowledge[name] = artifact


# Helper function for integration
def process_teaching_interaction(teacher_id: str, student_id: str, knowledge_name: str,
                                teacher_skills: Dict[str, float], student_skills: Dict[str, float],
                                knowledge_system: KnowledgeSystem, timestamp: int) -> Dict:
    """Process a teaching interaction"""

    session = knowledge_system.teach_knowledge(
        teacher_id=teacher_id,
        student_id=student_id,
        knowledge_name=knowledge_name,
        teacher_skills=teacher_skills,
        student_skills=student_skills,
        timestamp=timestamp
    )

    result = {
        "success": session.success,
        "knowledge": knowledge_name if session.knowledge else None,
        "improvement": session.improvement,
        "message": ""
    }

    if session.success:
        result["message"] = f"Successfully taught {knowledge_name}. Student improved by {session.improvement:.2f}"
    else:
        result["message"] = f"Teaching {knowledge_name} failed. Student needs more practice."

    return result