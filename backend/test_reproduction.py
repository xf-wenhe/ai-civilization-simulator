"""测试繁衍系统"""

from reproduction_system import ReproductionSystem
from agent import Agent, PersonalityTrait
from world_state import WorldState

def test_relationship_update():
    """测试关系更新"""
    world = WorldState(width=10, height=10)
    sys = ReproductionSystem(world)

    agent1 = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    agent2 = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    stage = sys.update_relationship(agent1, agent2.id, "friendly")
    print(f"关系阶段: {stage}")
    assert agent1.relationships[agent2.id].friendship > 0

    print("✓ 关系更新测试通过")

def test_marriage():
    """测试婚姻"""
    world = WorldState(width=10, height=10)
    sys = ReproductionSystem(world)

    agent1 = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )
    agent1.home_location = (5, 5)

    agent2 = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    # 建立关系
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")

    # 结婚
    success = sys.marry(agent1, agent2)
    assert success == True
    assert agent1.spouse_id == agent2.id
    assert agent2.spouse_id == agent1.id
    assert agent1.relationship_status == "married"
    assert agent2.relationship_status == "married"

    print("✓ 婚姻测试通过")

def test_pregnancy():
    """测试怀孕"""
    world = WorldState(width=10, height=10)
    sys = ReproductionSystem(world)

    agent1 = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )
    agent1.home_location = (5, 5)
    agent1.inventory = {"food": 30, "water": 20}

    agent2 = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )
    agent2.home_location = (5, 5)

    # 建立关系并结婚
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")

    sys.marry(agent1, agent2)

    # 尝试怀孕（可能需要多次尝试，因为只有5%概率）
    pregnant = False
    for _ in range(100):
        if sys.start_pregnancy(agent1, 0):
            pregnant = True
            break

    assert pregnant, "应该能够怀孕"
    assert agent1.pregnancy_start_tick is not None
    print("✓ 怀孕测试通过")

def test_child_creation():
    """测试生育"""
    world = WorldState(width=10, height=10)
    sys = ReproductionSystem(world)

    agent1 = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )
    agent1.home_location = (5, 5)
    agent1.inventory = {"food": 30, "water": 20}

    agent2 = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    # 建立关系并结婚
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")

    sys.marry(agent1, agent2)

    # 创建孩子
    child = sys.create_child(agent1, agent2, current_tick=100)

    assert child is not None, "应该能够创建孩子"
    assert child.id == "agent_child_100"
    assert child.position == (5, 5)
    assert child.hunger == 100
    assert child.thirst == 100
    assert "agent_child_100" in agent1.children
    assert "agent_child_100" in agent2.children
    assert agent1.pregnancy_start_tick is None

    print("✓ 生育测试通过")

if __name__ == "__main__":
    test_relationship_update()
    test_marriage()
    test_pregnancy()
    test_child_creation()
    print("\n✅ 所有繁衍系统测试通过")
