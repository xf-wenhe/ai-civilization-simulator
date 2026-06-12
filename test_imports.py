#!/usr/bin/env python3
"""
Test script to check all imports and basic functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("Testing imports...")

try:
    print("✓ Testing agent module...")
    from agent import Agent, ActionType, PersonalityTrait, Goal
    print("  Agent module OK")
except Exception as e:
    print(f"✗ Agent module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing world_state module...")
    from world_state import WorldState, ResourceType, BiomeType
    print("  World state module OK")
except Exception as e:
    print(f"✗ World state module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing memory_system module...")
    from memory_system import AgentMemorySystem
    print("  Memory system module OK")
except Exception as e:
    print(f"✗ Memory system module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing communication module...")
    from communication import CommunicationSystem
    print("  Communication module OK")
except Exception as e:
    print(f"✗ Communication module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing knowledge_system module...")
    from knowledge_system import KnowledgeSystem
    print("  Knowledge system module OK")
except Exception as e:
    print(f"✗ Knowledge system module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing crafting module...")
    from crafting import CraftingSystem
    print("  Crafting module OK")
except Exception as e:
    print(f"✗ Crafting module error: {e}")
    sys.exit(1)

try:
    print("✓ Testing orchestrator module...")
    from orchestrator import EnhancedAgentOrchestrator
    print("  Orchestrator module OK")
except Exception as e:
    print(f"✗ Orchestrator module error: {e}")
    sys.exit(1)

print("\n✅ All modules import successfully!")
print("\nTesting basic functionality...")

# Test world creation
try:
    world = WorldState(width=10, height=10)
    world.initialize_world()
    print("✓ World creation OK")
except Exception as e:
    print(f"✗ World creation error: {e}")
    sys.exit(1)

# Test agent creation
try:
    from agent import PersonalityTrait
    agent = Agent(
        id="test_agent",
        name="TestAgent",
        personality={
            PersonalityTrait.OPENNESS: 0.5,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
            PersonalityTrait.EXTRAVERSION: 0.5,
            PersonalityTrait.AGREEABLENESS: 0.5,
            PersonalityTrait.NEUROTICISM: 0.5
        },
        position=(0, 0)
    )
    print("✓ Agent creation OK")
except Exception as e:
    print(f"✗ Agent creation error: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! Project is ready to run.")