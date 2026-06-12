"""
Test to verify the priority inversion bug fix in orchestrator._simulate_decision()
Bug: Critical survival checks must come before proactive maintenance checks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import Agent, ActionType, PersonalityTrait, Goal
from world_state import WorldState, BiomeType
from orchestrator import EnhancedAgentOrchestrator


def test_critical_thirst_priority():
    """
    Test scenario: hunger=40 (proactive), thirst=25 (critical), at river with food
    Expected: Agent should DRINK (critical thirst) not EAT (proactive hunger)
    """
    print("\n=== Test: Critical Thirst Priority ===")

    # Create world and orchestrator
    world = WorldState(width=10, height=10)
    world.initialize_world()  # Initialize the world to create locations
    orchestrator = EnhancedAgentOrchestrator(world, agent_count=0)

    # Create agent with the bug scenario
    agent = Agent(
        id="test_agent",
        name="TestAgent",
        personality={trait: 0.5 for trait in PersonalityTrait},
        position=(5, 5),  # Center of map
        goals=[Goal("Survive", priority=1.0)]
    )

    # Set up the scenario
    agent.hunger = 40  # Moderate - should trigger proactive EAT
    agent.thirst = 25  # Critical - should override proactive EAT
    agent.health = 100
    agent.energy = 80
    agent.inventory = {"food": 3, "water": 0}  # Has food

    # Set position to river biome
    location = world.get_location((5, 5))
    location.biome = BiomeType.RIVER

    # Get decision
    decision = orchestrator._simulate_decision(agent)

    print(f"Agent state: hunger={agent.hunger}, thirst={agent.thirst}")
    print(f"Agent at river: {location.biome == BiomeType.RIVER}")
    print(f"Agent has food: {agent.inventory.get('food', 0) > 0}")
    print(f"\nDecision: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")

    # Verify correct behavior
    assert decision['action'] == ActionType.DRINK, \
        f"FAILED: Expected DRINK for critical thirst, got {decision['action']}"

    print("\n✓ PASSED: Agent correctly prioritized critical thirst over proactive hunger")


def test_critical_hunger_priority():
    """
    Test scenario: hunger=25 (critical), thirst=40 (proactive)
    Expected: Agent should GATHER food (critical hunger) not DRINK (proactive thirst)
    """
    print("\n=== Test: Critical Hunger Priority ===")

    world = WorldState(width=10, height=10)
    world.initialize_world()
    orchestrator = EnhancedAgentOrchestrator(world, agent_count=0)

    agent = Agent(
        id="test_agent",
        name="TestAgent",
        personality={trait: 0.5 for trait in PersonalityTrait},
        position=(5, 5),
        goals=[Goal("Survive", priority=1.0)]
    )

    # Set up the scenario
    agent.hunger = 25  # Critical
    agent.thirst = 40  # Moderate
    agent.health = 100
    agent.energy = 80
    agent.inventory = {"food": 0, "water": 2}  # Has water but no food

    location = world.get_location((5, 5))
    location.biome = BiomeType.RIVER

    decision = orchestrator._simulate_decision(agent)

    print(f"Agent state: hunger={agent.hunger}, thirst={agent.thirst}")
    print(f"Agent has water: {agent.inventory.get('water', 0) > 0}")
    print(f"\nDecision: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")

    # Verify correct behavior
    assert decision['action'] == ActionType.GATHER, \
        f"FAILED: Expected GATHER for critical hunger, got {decision['action']}"
    assert decision['parameters'] == "food", \
        f"FAILED: Expected to gather food, got {decision['parameters']}"

    print("\n✓ PASSED: Agent correctly prioritized critical hunger over proactive thirst")


def test_proactive_maintenance_when_no_critical():
    """
    Test scenario: hunger=40 (proactive), thirst=45 (proactive), at river with food
    Expected: Agent can perform proactive actions (EAT or DRINK)
    """
    print("\n=== Test: Proactive Maintenance (No Critical) ===")

    world = WorldState(width=10, height=10)
    world.initialize_world()
    orchestrator = EnhancedAgentOrchestrator(world, agent_count=0)

    agent = Agent(
        id="test_agent",
        name="TestAgent",
        personality={trait: 0.5 for trait in PersonalityTrait},
        position=(5, 5),
        goals=[Goal("Survive", priority=1.0)]
    )

    # Set up the scenario
    agent.hunger = 40  # Proactive level
    agent.thirst = 45  # Proactive level
    agent.health = 100
    agent.energy = 80
    agent.inventory = {"food": 2, "water": 0}

    location = world.get_location((5, 5))
    location.biome = BiomeType.RIVER

    decision = orchestrator._simulate_decision(agent)

    print(f"Agent state: hunger={agent.hunger}, thirst={agent.thirst}")
    print(f"Agent has food: {agent.inventory.get('food', 0) > 0}")
    print(f"Agent at river: {location.biome == BiomeType.RIVER}")
    print(f"\nDecision: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")

    # Either EAT or DRINK is acceptable for proactive maintenance
    assert decision['action'] in [ActionType.EAT, ActionType.DRINK], \
        f"FAILED: Expected EAT or DRINK for proactive maintenance, got {decision['action']}"

    print(f"\n✓ PASSED: Agent performed proactive maintenance (no critical needs)")


def test_both_critical_thirst_wins():
    """
    Test scenario: hunger=25 (critical), thirst=20 (more critical)
    Expected: Agent should GATHER water (more critical thirst)
    """
    print("\n=== Test: Both Critical - Thirst Wins ===")

    world = WorldState(width=10, height=10)
    world.initialize_world()
    orchestrator = EnhancedAgentOrchestrator(world, agent_count=0)

    agent = Agent(
        id="test_agent",
        name="TestAgent",
        personality={trait: 0.5 for trait in PersonalityTrait},
        position=(5, 5),
        goals=[Goal("Survive", priority=1.0)]
    )

    # Both critical, thirst more urgent
    agent.hunger = 25  # Critical
    agent.thirst = 20  # More critical
    agent.health = 100
    agent.energy = 80
    agent.inventory = {"food": 0, "water": 0}

    decision = orchestrator._simulate_decision(agent)

    print(f"Agent state: hunger={agent.hunger}, thirst={agent.thirst}")
    print(f"\nDecision: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")

    # Should prioritize thirst (lower value = more critical)
    assert decision['action'] == ActionType.GATHER, \
        f"FAILED: Expected GATHER, got {decision['action']}"
    assert decision['parameters'] == "water", \
        f"FAILED: Expected to gather water for more critical thirst, got {decision['parameters']}"

    print("\n✓ PASSED: Agent correctly prioritized more critical need (thirst)")


def main():
    print("\n" + "="*70)
    print("Testing Priority Fix in orchestrator._simulate_decision()")
    print("="*70)

    try:
        test_critical_thirst_priority()
        test_critical_hunger_priority()
        test_proactive_maintenance_when_no_critical()
        test_both_critical_thirst_wins()

        print("\n" + "="*70)
        print("✓ All tests passed! Priority inversion bug is fixed.")
        print("="*70 + "\n")

    except AssertionError as e:
        print("\n" + "="*70)
        print(f"✗ Test failed: {e}")
        print("="*70 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()