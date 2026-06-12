"""
Enhanced agent orchestrator with memory system integration.
"""

import asyncio
import os
import json
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from agent import Agent, ActionType, PersonalityTrait, Goal, Memory, Relationship
from world_state import WorldState, ResourceType, BiomeType
from memory_system import AgentMemorySystem
from survival_system import SurvivalSystem


class EnhancedAgentOrchestrator:
    """Orchestrator with semantic memory system"""

    def __init__(self, world: WorldState, agent_count: int = 5):
        load_dotenv()

        self.world = world
        self.agents: Dict[str, Agent] = {}

        # Check if using simulation mode
        self.use_simulation = os.getenv("USE_SIMULATION", "false").lower() == "true"

        # Initialize Anthropic client with custom base_url if provided
        if Anthropic and not self.use_simulation:
            client_kwargs = {"api_key": os.getenv("ANTHROPIC_API_KEY")}
            base_url = os.getenv("ANTHROPIC_BASE_URL")
            if base_url:
                client_kwargs["base_url"] = base_url
            self.client = Anthropic(**client_kwargs)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            print(f"✓ API Client initialized (model: {self.model})")
        else:
            self.client = None
            if self.use_simulation:
                print("✓ Running in SIMULATION mode (no API calls)")
            else:
                print("⚠️  No API client available, using simulation mode")

        self.running = False

        # Initialize memory system
        self.memory_system = AgentMemorySystem(persist_directory="./data/chroma")

        # === 新增：初始化生存系统 ===
        self.survival_system = SurvivalSystem(world)

        # Create initial agents
        for i in range(agent_count):
            agent = self._create_agent(i)
            self.agents[agent.id] = agent
            self.world.locations[agent.position].agents_present.append(agent.id)

    def _create_agent(self, index: int) -> Agent:
        """Create agent with personality and goals"""
        agent_id = f"agent_{index}"
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
        name = names[index % len(names)]

        personality = {
            PersonalityTrait.OPENNESS: random.uniform(0.3, 0.9),
            PersonalityTrait.CONSCIENTIOUSNESS: random.uniform(0.3, 0.9),
            PersonalityTrait.EXTRAVERSION: random.uniform(0.3, 0.9),
            PersonalityTrait.AGREEABLENESS: random.uniform(0.3, 0.9),
            PersonalityTrait.NEUROTICISM: random.uniform(0.1, 0.7)
        }

        center = (self.world.width // 2, self.world.height // 2)
        start_pos = (center[0] + random.randint(-2, 2), center[1] + random.randint(-2, 2))

        goals = [
            Goal("Find food to survive", priority=0.8),
            Goal("Explore the world", priority=0.6),
            Goal("Meet other agents", priority=0.5 if personality[PersonalityTrait.EXTRAVERSION] > 0.5 else 0.2)
        ]

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

    def _build_enhanced_system_prompt(self, agent: Agent) -> str:
        """Build system prompt with memory context"""

        # Retrieve relevant memories
        recent_memories = self.memory_system.get_recent_memories(agent.id, limit=5)
        relevant_goals = [g for g in agent.goals if not g.completed][:3]

        location = self.world.get_location(agent.position)
        nearby_agents = location.agents_present if location else []

        personality_desc = ", ".join([f"{t.value}: {v:.2f}" for t, v in agent.personality.items()])

        memory_context = "\n".join([f"- {m['content']}" for m in recent_memories]) if recent_memories else "No significant memories yet."

        return f"""You are {agent.name}, an autonomous agent in an emerging civilization.

PERSONALITY: {personality_desc}

CURRENT STATUS:
- Position: {agent.position} ({location.biome.value if location else 'unknown'})
- Health: {agent.health:.1f}/100 | Energy: {agent.energy:.1f}/100
- Inventory: {agent.inventory}
- Skills: {agent.skills}

RECENT MEMORIES:
{memory_context}

CURRENT GOALS:
{chr(10).join([f"- {g.description} (priority: {g.priority:.2f})" for g in relevant_goals])}

NEARBY AGENTS: {nearby_agents}

AVAILABLE ACTIONS:
- MOVE [north/south/east/west] - Move to adjacent location
- GATHER [food/wood/stone/water] - Gather resources
- CRAFT [tool/shelter] - Create items from materials
- COMMUNICATE [agent_name] - Talk to nearby agent
- REST - Recover energy
- BUILD [structure] - Construct buildings

Choose your next action autonomously based on your personality, goals, and situation.

Respond EXACTLY in this format:
ACTION: [action_type]
PARAMETERS: [details]
REASONING: [why you chose this]

Your decisions should reflect your personality traits and current needs."""

    async def get_agent_decision_with_memory(self, agent: Agent) -> Dict:
        """Get decision using Claude with memory context"""

        # Always use simulation if USE_SIMULATION=true
        if self.use_simulation or not self.client:
            return self._simulate_decision(agent)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                system=self._build_enhanced_system_prompt(agent),
                messages=[{"role": "user", "content": "What will you do next?"}]
            )

            return self._parse_action_response(response.content[0].text)

        except Exception as e:
            print(f"Error for {agent.name}: {e}")
            return self._simulate_decision(agent)

    def _parse_action_response(self, response_text: str) -> Dict:
        """Parse Claude response"""
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
        """Heuristic-based decision with personality influence"""
        import random

        # === 新增：死亡检查 ===
        if not agent.is_alive:
            return {"action": ActionType.REST, "parameters": "", "reasoning": "Agent is dead"}

        # === 新增：主动进食/喝水 ===
        if agent.hunger < 50 and agent.inventory.get("food", 0) > 0:
            return {"action": ActionType.EAT, "parameters": "", "reasoning": "Eating food from inventory"}

        if agent.thirst < 50:
            # 检查是否有水或靠近河流
            location = self.world.get_location(agent.position)
            if agent.inventory.get("water", 0) > 0 or (location and location.biome == BiomeType.RIVER):
                return {"action": ActionType.DRINK, "parameters": "", "reasoning": "Drinking water"}

        # === 新增：生存优先 ===
        if agent.hunger < 30 or agent.thirst < 30:
            if agent.thirst < agent.hunger and agent.thirst < 30:
                # 优先解决口渴
                return {"action": ActionType.GATHER, "parameters": "water", "reasoning": f"Thirst critical ({agent.thirst:.0f})"}
            elif agent.hunger < 30:
                # 解决饥饿
                return {"action": ActionType.GATHER, "parameters": "food", "reasoning": f"Hunger critical ({agent.hunger:.0f})"}

        # Priority-based decision making with energy check first
        # 能量低于30强制休息
        if agent.energy < 30:
            return {"action": ActionType.REST, "parameters": "", "reasoning": "Low energy, need to rest"}

        # 能量恢复后才能继续其他行动
        if agent.energy < 50:
            # 能量低于50也倾向于休息
            return {"action": ActionType.REST, "parameters": "", "reasoning": "Low energy, need to rest"}

        # Check inventory and gather if needed
        food_count = agent.inventory.get("food", 0)
        if food_count < 3:
            # Personality affects gathering behavior
            if agent.personality[PersonalityTrait.OPENNESS] > 0.7:
                # High openness - try different resources
                resources = ["food", "wood", "water"]
                resource = random.choice(resources)
            else:
                resource = "food"
            return {"action": ActionType.GATHER, "parameters": resource, "reasoning": f"Need {resource} (current: {food_count})"}

        # Social interaction for extraverted agents
        location = self.world.get_location(agent.position)
        if location and len(location.agents_present) > 1:
            others = [a for a in location.agents_present if a != agent.id]
            extraversion = agent.personality[PersonalityTrait.EXTRAVERSION]

            if others and extraversion > 0.6:
                # High extraversion - actively communicate
                target = random.choice(others)
                return {"action": ActionType.COMMUNICATE, "parameters": target, "reasoning": f"Social interaction (extraversion: {extraversion:.2f})"}
            elif others and extraversion > 0.4 and random.random() < 0.5:
                # Medium extraversion - sometimes communicate
                target = random.choice(others)
                return {"action": ActionType.COMMUNICATE, "parameters": target, "reasoning": "Opportunistic socializing"}

        # Exploration vs crafting based on personality
        openness = agent.personality[PersonalityTrait.OPENNESS]
        conscientiousness = agent.personality[PersonalityTrait.CONSCIENTIOUSNESS]

        if openness > 0.7 and random.random() < 0.6:
            # High openness - explore
            directions = ["north", "south", "east", "west"]
            return {"action": ActionType.MOVE, "parameters": random.choice(directions), "reasoning": f"Exploring (openness: {openness:.2f})"}

        if conscientiousness > 0.6 and agent.inventory.get("wood", 0) >= 3:
            # High conscientiousness - craft/build
            return {"action": ActionType.CRAFT, "parameters": "tool", "reasoning": f"Crafting (conscientiousness: {conscientiousness:.2f})"}

        # Default: explore or gather based on personality
        if random.random() < 0.5:
            directions = ["north", "south", "east", "west"]
            return {"action": ActionType.MOVE, "parameters": random.choice(directions), "reasoning": "Random exploration"}
        else:
            return {"action": ActionType.GATHER, "parameters": "food", "reasoning": "Gathering food"}

    async def execute_action_and_learn(self, agent: Agent, action_data: Dict):
        """Execute action and store in memory"""

        action = action_data.get("action", ActionType.REST)
        params = action_data.get("parameters", "")
        reasoning = action_data.get("reasoning", "")

        agent.current_action = action

        # Execute action
        result = await self._execute_action(agent, action, params)

        # === 新增：更新生存需求 ===
        self.survival_system.update_needs(agent, action.value if hasattr(action, 'value') else str(action))

        # === 新增：检查死亡 ===
        if self.survival_system.check_death(agent, self.world.tick):
            print(f"💀 {agent.name} 死亡了！原因：健康值归零")
            return

        # Store as episodic memory
        memory_content = f"{action.value.capitalize()} - {reasoning}. Result: {result}"
        self.memory_system.store_memory(
            agent_id=agent.id,
            memory_type="episodic",
            content=memory_content,
            timestamp=self.world.tick,
            importance=self._calculate_importance(action, result)
        )

        # Store semantic knowledge if learned something
        if action == ActionType.GATHER and "success" in result:
            self.memory_system.store_memory(
                agent_id=agent.id,
                memory_type="semantic",
                content=f"Location {agent.position} has {params}",
                timestamp=self.world.tick,
                importance=0.4
            )

        # Decrease energy
        if action != ActionType.REST:
            agent.energy = max(0, agent.energy - 10)

    async def _execute_action(self, agent: Agent, action: ActionType, params: str) -> str:
        """Execute specific action and return result"""

        if action == ActionType.MOVE:
            return self._execute_move(agent, params)
        elif action == ActionType.GATHER:
            return self._execute_gather(agent, params)
        elif action == ActionType.REST:
            return self._execute_rest(agent)
        elif action == ActionType.COMMUNICATE:
            return await self._execute_communicate(agent, params)
        # === 新增 ===
        elif action == ActionType.EAT:
            return self._execute_eat(agent)
        elif action == ActionType.DRINK:
            return self._execute_drink(agent)
        else:
            return "Action not implemented"

    def _execute_move(self, agent: Agent, direction: str) -> str:
        x, y = agent.position

        moves = {"north": (x, y-1), "south": (x, y+1), "east": (x+1, y), "west": (x-1, y)}
        new_pos = moves.get(direction.lower(), agent.position)

        if 0 <= new_pos[0] < self.world.width and 0 <= new_pos[1] < self.world.height:
            self.world.update_agent_position(agent.id, agent.position, new_pos)
            agent.position = new_pos
            return f"Moved {direction} to {new_pos}"
        return "Cannot move in that direction"

    def _execute_gather(self, agent: Agent, resource_str: str) -> str:
        try:
            resource_type = ResourceType(resource_str.lower())
        except:
            return f"Unknown resource: {resource_str}"

        skill_level = agent.skills.get("gathering", 0.3)
        amount = int(5 + skill_level * 10)

        gathered = self.world.gather_resource(agent.position, resource_type, amount)

        if gathered > 0:
            agent.inventory[resource_type.value] = agent.inventory.get(resource_type.value, 0) + gathered

            if random.random() < 0.1:
                agent.skills["gathering"] = min(1.0, agent.skills.get("gathering", 0) + 0.05)

            return f"success - gathered {gathered} {resource_type.value}"
        return f"No {resource_str} available at this location"

    def _execute_rest(self, agent: Agent) -> str:
        agent.energy = min(100, agent.energy + 30)
        return f"Rested, energy now {agent.energy:.1f}"

    def _execute_eat(self, agent: Agent) -> str:
        """执行进食"""
        success = self.survival_system.eat(agent)
        if success:
            return f"Ate food, hunger now {agent.hunger:.0f}"
        return "No food available"

    def _execute_drink(self, agent: Agent) -> str:
        """执行喝水"""
        success = self.survival_system.drink(agent)
        if success:
            return f"Drank water, thirst now {agent.thirst:.0f}"
        return "No water available"

    async def _execute_communicate(self, agent: Agent, target_id: str) -> str:
        if target_id not in self.agents:
            return f"Agent {target_id} not found"

        target = self.agents[target_id]
        location = self.world.get_location(agent.position)

        if target_id not in (location.agents_present if location else []):
            return f"{target.name} is not nearby"

        if target_id not in agent.relationships:
            agent.relationships[target_id] = {
                "agent_id": target_id,
                "trust": 0.0,
                "friendship": 0.0,
                "interactions": 0
            }

        agent.relationships[target_id]["interactions"] += 1

        if agent.personality[PersonalityTrait.AGREEABLENESS] > 0.5:
            agent.relationships[target_id]["friendship"] = min(
                1.0,
                agent.relationships[target_id]["friendship"] + 0.1
            )

        return f"Communicated with {target.name}"

    def _calculate_importance(self, action: ActionType, result: str) -> float:
        """Calculate memory importance"""
        if "success" in result:
            return 0.7
        elif "fail" in result or "cannot" in result.lower():
            return 0.5
        return 0.3

    async def run_simulation_loop(self, tick_rate: int = 10):
        """Main simulation loop"""
        self.running = True

        while self.running:
            self.world.advance_time()

            decisions = await asyncio.gather(
                *[self.get_agent_decision_with_memory(agent) for agent in self.agents.values()]
            )

            for agent, decision in zip(self.agents.values(), decisions):
                await self.execute_action_and_learn(agent, decision)

            if self.world.tick % 10 == 0:
                self.save_state()

            await asyncio.sleep(tick_rate)

    def save_state(self):
        """Save world and agent states"""
        os.makedirs("data", exist_ok=True)

        with open("data/world_state.json", 'w') as f:
            json.dump(self.world.to_dict(), f, indent=2)

        for agent in self.agents.values():
            agent.save_state("data")

    def stop(self):
        self.running = False