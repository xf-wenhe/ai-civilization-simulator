"""
Agent orchestrator - manages agent lifecycle, scheduling, and Claude API integration.
"""

import asyncio
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import anthropic
try:
    from anthropic import Anthropic
except ImportError:
    print("Warning: anthropic package not installed. Agent decision-making will be simulated.")
    Anthropic = None

from agent import Agent, ActionType, PersonalityTrait, Goal
from world_state import WorldState, ResourceType


class AgentOrchestrator:
    """Manages all agents and coordinates their actions"""

    def __init__(self, world: WorldState, agent_count: int = 5):
        load_dotenv()

        self.world = world
        self.agents: Dict[str, Agent] = {}
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic else None
        self.running = False

        # Create initial agents
        for i in range(agent_count):
            agent = self._create_agent(i)
            self.agents[agent.id] = agent
            self.world.locations[agent.position].agents_present.append(agent.id)

    def _create_agent(self, index: int) -> Agent:
        """Create a new agent with randomized personality and starting position"""
        import random

        # Generate unique ID and name
        agent_id = f"agent_{index}"
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
        name = names[index % len(names)]

        # Random personality (Big Five traits)
        personality = {
            PersonalityTrait.OPENNESS: random.uniform(0.3, 0.9),
            PersonalityTrait.CONSCIENTIOUSNESS: random.uniform(0.3, 0.9),
            PersonalityTrait.EXTRAVERSION: random.uniform(0.3, 0.9),
            PersonalityTrait.AGREEABLENESS: random.uniform(0.3, 0.9),
            PersonalityTrait.NEUROTICISM: random.uniform(0.1, 0.7)
        }

        # Starting position near village center
        center = (self.world.width // 2, self.world.height // 2)
        start_pos = (
            center[0] + random.randint(-2, 2),
            center[1] + random.randint(-2, 2)
        )

        # Initial goals
        goals = [
            Goal("Find food to eat", priority=0.8),
            Goal("Explore the surrounding area", priority=0.6),
            Goal("Meet other agents", priority=0.5 if personality[PersonalityTrait.EXTRAVERSION] > 0.5 else 0.2)
        ]

        # Initial skills
        skills = {
            "gathering": random.uniform(0.2, 0.5),
            "crafting": random.uniform(0.1, 0.3),
            "communication": random.uniform(0.3, 0.6)
        }

        return Agent(
            id=agent_id,
            name=name,
            personality=personality,
            position=start_pos,
            goals=goals,
            skills=skills
        )

    def _build_agent_system_prompt(self, agent: Agent) -> str:
        """Build system prompt defining agent's personality and context"""
        personality_desc = ", ".join([f"{trait.value}: {value:.2f}" for trait, value in agent.personality.items()])
        goals_desc = ", ".join([f"{g.description} (priority: {g.priority:.2f})" for g in agent.goals if not g.completed])
        location = self.world.get_location(agent.position)

        return f"""You are {agent.name}, an autonomous agent in an emerging civilization.

Your personality traits: {personality_desc}
Your current goals: {goals_desc}

Current status:
- Position: {agent.position} ({location.biome.value if location else 'unknown'})
- Health: {agent.health:.1f}
- Energy: {agent.energy:.1f}
- Inventory: {agent.inventory}
- Skills: {agent.skills}

You can take these actions:
- MOVE: Move to adjacent location (north, south, east, west)
- GATHER: Gather resources from current location (food, wood, stone, water)
- CRAFT: Create tools or items from gathered materials
- COMMUNICATE: Talk to nearby agents (they will respond)
- REST: Recover energy
- BUILD: Construct buildings or shelters
- TEACH: Share knowledge with other agents
- TRADE: Exchange items with other agents

Choose ONE action to take next. Respond in this exact format:
ACTION: [action_type]
PARAMETERS: [details like direction for MOVE, resource type for GATHER, target agent for COMMUNICATE]
REASONING: [brief explanation of why you chose this action]

Your personality traits should influence your choices:
- High openness: more likely to explore, try new things
- High conscientiousness: more likely to plan carefully, complete goals
- High extraversion: more likely to communicate, form relationships
- High agreeableness: more likely to help others, cooperate
- High neuroticism: more cautious, risk-averse

Act autonomously based on your goals, personality, and current situation."""

    async def get_agent_decision(self, agent: Agent) -> Dict:
        """Get next action from agent using Claude API"""
        if not self.client:
            # Simulated decision if Claude not available
            return self._simulate_decision(agent)

        # Build context including nearby agents and recent memories
        location = self.world.get_location(agent.position)
        nearby_agents = location.agents_present if location else []
        recent_memories = agent.memories[-5:] if agent.memories else []

        context = f"""
Nearby agents: {nearby_agents}
Recent memories: {[m.content for m in recent_memories]}
Available resources at current location: {location.resources if location else {}}
"""

        user_message = f"{context}\nWhat action will you take?"

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=self._build_agent_system_prompt(agent),
                messages=[{"role": "user", "content": user_message}]
            )

            # Parse response
            text = response.content[0].text

            # Extract action from response (simple parsing)
            action_data = self._parse_action_response(text)
            return action_data

        except Exception as e:
            print(f"Error getting decision for {agent.name}: {e}")
            return self._simulate_decision(agent)

    def _parse_action_response(self, response_text: str) -> Dict:
        """Parse action from Claude response"""
        lines = response_text.strip().split('\n')
        action_data = {}

        for line in lines:
            if line.startswith("ACTION:"):
                action_str = line.split("ACTION:")[1].strip().upper()
                try:
                    action_data["action"] = ActionType(action_str.lower())
                except:
                    action_data["action"] = ActionType.REST
            elif line.startswith("PARAMETERS:"):
                action_data["parameters"] = line.split("PARAMETERS:")[1].strip()
            elif line.startswith("REASONING:"):
                action_data["reasoning"] = line.split("REASONING:")[1].strip()

        return action_data

    def _simulate_decision(self, agent: Agent) -> Dict:
        """Simulate agent decision when Claude unavailable"""
        import random

        # Simple heuristic-based decision
        if agent.energy < 30:
            return {"action": ActionType.REST, "parameters": "", "reasoning": "Low energy"}

        if not agent.inventory.get("food", 0):
            return {"action": ActionType.GATHER, "parameters": "food", "reasoning": "Need food"}

        location = self.world.get_location(agent.position)
        if location and location.agents_present and len(location.agents_present) > 1:
            other_agents = [a for a in location.agents_present if a != agent.id]
            if other_agents and agent.personality[PersonalityTrait.EXTRAVERSION] > 0.5:
                return {"action": ActionType.COMMUNICATE, "parameters": other_agents[0], "reasoning": "Social interaction"}

        # Random movement
        directions = ["north", "south", "east", "west"]
        return {"action": ActionType.MOVE, "parameters": random.choice(directions), "reasoning": "Exploring"}

    async def execute_agent_action(self, agent: Agent, action_data: Dict):
        """Execute agent's chosen action"""
        action = action_data.get("action", ActionType.REST)
        params = action_data.get("parameters", "")
        reasoning = action_data.get("reasoning", "")

        agent.current_action = action

        # Execute action
        if action == ActionType.MOVE:
            self._execute_move(agent, params)
        elif action == ActionType.GATHER:
            self._execute_gather(agent, params)
        elif action == ActionType.REST:
            self._execute_rest(agent)
        elif action == ActionType.COMMUNICATE:
            await self._execute_communicate(agent, params)

        # Record memory
        memory_content = f"Tick {self.world.tick}: Took action {action.value}. {reasoning}"
        agent.memories.append({
            "content": memory_content,
            "timestamp": self.world.tick,
            "importance": 0.5,
            "memory_type": "episodic"
        })

        # Decrease energy (except for rest)
        if action != ActionType.REST:
            agent.energy = max(0, agent.energy - 10)

    def _execute_move(self, agent: Agent, direction: str):
        """Move agent to adjacent location"""
        x, y = agent.position

        if direction == "north":
            new_pos = (x, y - 1)
        elif direction == "south":
            new_pos = (x, y + 1)
        elif direction == "east":
            new_pos = (x + 1, y)
        elif direction == "west":
            new_pos = (x - 1, y)
        else:
            return  # Invalid direction

        # Check bounds
        if 0 <= new_pos[0] < self.world.width and 0 <= new_pos[1] < self.world.height:
            self.world.update_agent_position(agent.id, agent.position, new_pos)
            agent.position = new_pos

    def _execute_gather(self, agent: Agent, resource_str: str):
        """Gather resource from current location"""
        try:
            resource_type = ResourceType(resource_str.lower())
        except:
            resource_type = ResourceType.FOOD  # Default

        # Gather based on skill level
        skill_level = agent.skills.get("gathering", 0.3)
        amount_to_gather = int(5 + skill_level * 10)

        gathered = self.world.gather_resource(agent.position, resource_type, amount_to_gather)

        if gathered > 0:
            agent.inventory[resource_type.value] = agent.inventory.get(resource_type.value, 0) + gathered

            # Small chance to improve skill
            if random.random() < 0.1:
                agent.skills["gathering"] = min(1.0, agent.skills.get("gathering", 0) + 0.05)

    def _execute_rest(self, agent: Agent):
        """Rest to recover energy"""
        agent.energy = min(100, agent.energy + 30)

    async def _execute_communicate(self, agent: Agent, target_agent_id: str):
        """Communicate with another agent"""
        if target_agent_id not in self.agents:
            return

        target = self.agents[target_agent_id]

        # Check if target is nearby
        location = self.world.get_location(agent.position)
        if target_agent_id not in (location.agents_present if location else []):
            return

        # Update relationship
        if target_agent_id not in agent.relationships:
            agent.relationships[target_agent_id] = {
                "agent_id": target_agent_id,
                "trust": 0.0,
                "friendship": 0.0,
                "interactions": 0
            }

        agent.relationships[target_agent_id]["interactions"] += 1

        # Increase friendship for agreeable agents
        if agent.personality[PersonalityTrait.AGREEABLENESS] > 0.5:
            agent.relationships[target_agent_id]["friendship"] = min(
                1.0,
                agent.relationships[target_agent_id]["friendship"] + 0.1
            )

    async def run_simulation_loop(self, tick_rate: int = 10):
        """Main simulation loop"""
        self.running = True

        while self.running:
            # Advance world time
            self.world.advance_time()

            # Get decisions from all agents concurrently
            decisions = await asyncio.gather(*[self.get_agent_decision(agent) for agent in self.agents.values()])

            # Execute all actions
            for agent, decision in zip(self.agents.values(), decisions):
                await self.execute_agent_action(agent, decision)

            # Save state periodically
            if self.world.tick % 10 == 0:
                self.save_state()

            # Wait for next tick
            await asyncio.sleep(tick_rate)

    def save_state(self):
        """Save world and agent states"""
        os.makedirs("data", exist_ok=True)

        # Save world state
        with open("data/world_state.json", 'w') as f:
            json.dump(self.world.to_dict(), f, indent=2)

        # Save each agent
        for agent in self.agents.values():
            agent.save_state("data")

    def stop(self):
        """Stop simulation"""
        self.running = False


async def main():
    """Start the civilization simulation"""
    world = WorldState(width=50, height=50)
    world.initialize_world()

    orchestrator = AgentOrchestrator(world, agent_count=5)

    print("Starting AI Civilization Simulator...")
    print(f"World size: {world.width}x{world.height}")
    print(f"Agents: {len(orchestrator.agents)}")
    print(f"Agent names: {[a.name for a in orchestrator.agents.values()]}")

    try:
        await orchestrator.run_simulation_loop(tick_rate=10)
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        orchestrator.stop()
        orchestrator.save_state()
        print("State saved. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())