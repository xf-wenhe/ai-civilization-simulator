"""
Communication system for agent-to-agent dialogue.
Agents can have natural language conversations stored in conversation logs.
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
import os
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from agent import Agent


@dataclass
class DialogueMessage:
    """Single message in a dialogue"""
    speaker_id: str
    speaker_name: str
    content: str
    timestamp: int
    emotion: str = "neutral"


@dataclass
class Conversation:
    """Full conversation between agents"""
    participants: List[str]
    messages: List[DialogueMessage] = field(default_factory=list)
    topic: str = "general"
    start_tick: int = 0
    end_tick: Optional[int] = None


class CommunicationSystem:
    """Manages agent communications and dialogue generation"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}  # conversation_id -> Conversation
        if Anthropic:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            client_kwargs = {"api_key": os.getenv("ANTHROPIC_API_KEY")}
            base_url = os.getenv("ANTHROPIC_BASE_URL")
            if base_url:
                client_kwargs["base_url"] = base_url
            self.client = Anthropic(**client_kwargs)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        else:
            self.client = None

    def generate_conversation_id(self, agent_ids: List[str]) -> str:
        """Generate unique conversation ID"""
        sorted_ids = sorted(agent_ids)
        return f"conv_{sorted_ids[0]}_{sorted_ids[1]}"

    async def initiate_dialogue(self, agent1: Agent, agent2: Agent, topic: str = "general") -> Conversation:
        """Start a dialogue between two agents"""

        conv_id = self.generate_conversation_id([agent1.id, agent2.id])

        # Check if conversation already exists
        if conv_id in self.conversations:
            conversation = self.conversations[conv_id]
        else:
            conversation = Conversation(
                participants=[agent1.id, agent2.id],
                topic=topic,
                start_tick=0
            )
            self.conversations[conv_id] = conversation

        # Generate initial dialogue
        if self.client:
            dialogue_messages = await self._generate_ai_dialogue(agent1, agent2, conversation)
            conversation.messages.extend(dialogue_messages)
        else:
            # Simulated dialogue
            simulated = self._simulate_dialogue(agent1, agent2)
            conversation.messages.extend(simulated)

        return conversation

    async def _generate_ai_dialogue(self, agent1: Agent, agent2: Agent, conversation: Conversation) -> List[DialogueMessage]:
        """Generate dialogue using Claude"""

        # Build context
        context = f"""
Agents {agent1.name} and {agent2.name} are having a conversation about: {conversation.topic}

{agent1.name}'s personality: {self._personality_summary(agent1)}
{agent1.name}'s recent experiences: {self._recent_experiences(agent1)}

{agent2.name}'s personality: {self._personality_summary(agent2)}
{agent2.name}'s recent experiences: {self._recent_experiences(agent2)}

Previous messages in this conversation:
{self._format_previous_messages(conversation.messages)}

Generate a natural dialogue exchange (2-3 messages each) between these agents that reflects their personalities.
Format each message as:
AGENT_NAME: [message content]

Make the conversation interesting and reflect their unique personalities and current situations.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                messages=[{"role": "user", "content": context}]
            )

            dialogue_text = response.content[0].text
            return self._parse_dialogue(dialogue_text, agent1, agent2)

        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return self._simulate_dialogue(agent1, agent2)

    def _parse_dialogue(self, dialogue_text: str, agent1: Agent, agent2: Agent) -> List[DialogueMessage]:
        """Parse dialogue from Claude response"""
        messages = []
        lines = dialogue_text.strip().split('\n')

        agent_map = {agent1.name: agent1, agent2.name: agent2}

        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                name = parts[0].strip()
                content = parts[1].strip() if len(parts) > 1 else ""

                agent = agent_map.get(name)
                if agent and content:
                    messages.append(DialogueMessage(
                        speaker_id=agent.id,
                        speaker_name=agent.name,
                        content=content,
                        timestamp=0,  # Will be set by caller
                        emotion=self._detect_emotion(content)
                    ))

        return messages

    def _detect_emotion(self, content: str) -> str:
        """Simple emotion detection from content"""
        positive_words = ["happy", "glad", "excited", "wonderful", "great", "pleased", "thank"]
        negative_words = ["sad", "angry", "frustrated", "worried", "afraid", "unhappy"]
        curious_words = ["what", "how", "why", "curious", "wonder", "interesting"]

        content_lower = content.lower()

        if any(word in content_lower for word in positive_words):
            return "positive"
        elif any(word in content_lower for word in negative_words):
            return "negative"
        elif any(word in content_lower for word in curious_words):
            return "curious"

        return "neutral"

    def _simulate_dialogue(self, agent1: Agent, agent2: Agent) -> List[DialogueMessage]:
        """Simulate dialogue without AI"""

        templates = [
            f"{agent1.name}: Hello {agent2.name}, how are you today?",
            f"{agent2.name}: I'm doing well, {agent1.name}. What brings you here?",
            f"{agent1.name}: I was exploring this area. Have you found anything interesting?",
            f"{agent2.name}: Yes, I found some resources nearby. We could work together!",
            f"{agent1.name}: That sounds like a great idea. Let's collaborate."
        ]

        messages = []
        agent_map = {agent1.name: agent1, agent2.name: agent2}

        for template in templates:
            if ':' in template:
                parts = template.split(':', 1)
                name = parts[0].strip()
                content = parts[1].strip()

                agent = agent_map.get(name)
                if agent:
                    messages.append(DialogueMessage(
                        speaker_id=agent.id,
                        speaker_name=agent.name,
                        content=content,
                        timestamp=0,
                        emotion="neutral"
                    ))

        return messages

    def _personality_summary(self, agent: Agent) -> str:
        """Summarize agent personality for context"""
        traits = []
        for trait, value in agent.personality.items():
            if value > 0.7:
                traits.append(f"very {trait.value}")
            elif value < 0.3:
                traits.append(f"not very {trait.value}")

        return ", ".join(traits) if traits else "balanced"

    def _recent_experiences(self, agent: Agent) -> str:
        """Summarize recent experiences"""
        if agent.memories:
            recent = agent.memories[-3:]
            return "; ".join([m["content"] if isinstance(m, dict) else m.content for m in recent])
        return "No significant experiences yet"

    def _format_previous_messages(self, messages: List[DialogueMessage]) -> str:
        """Format previous messages for context"""
        if not messages:
            return "No previous messages"

        return "\n".join([f"{m.speaker_name}: {m.content}" for m in messages[-6:]])

    def save_conversation(self, conversation_id: str, directory: str = "data/conversations"):
        """Save conversation to file"""
        os.makedirs(directory, exist_ok=True)

        if conversation_id not in self.conversations:
            return

        conversation = self.conversations[conversation_id]

        filepath = os.path.join(directory, f"{conversation_id}.json")

        data = {
            "participants": conversation.participants,
            "topic": conversation.topic,
            "start_tick": conversation.start_tick,
            "end_tick": conversation.end_tick,
            "messages": [
                {
                    "speaker_id": m.speaker_id,
                    "speaker_name": m.speaker_name,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "emotion": m.emotion
                }
                for m in conversation.messages
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_conversations(self, directory: str = "data/conversations"):
        """Load all saved conversations"""
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)

                with open(filepath, 'r') as f:
                    data = json.load(f)

                messages = [
                    DialogueMessage(**m) for m in data["messages"]
                ]

                conversation = Conversation(
                    participants=data["participants"],
                    messages=messages,
                    topic=data["topic"],
                    start_tick=data["start_tick"],
                    end_tick=data.get("end_tick")
                )

                conv_id = filename.replace('.json', '')
                self.conversations[conv_id] = conversation


# Export for use in orchestrator
async def generate_agent_dialogue(agent1: Agent, agent2: Agent, comm_system: CommunicationSystem) -> Conversation:
    """Generate dialogue between agents"""
    return await comm_system.initiate_dialogue(agent1, agent2)