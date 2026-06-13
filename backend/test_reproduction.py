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

    print("✓ 婚姻测试通过")

if __name__ == "__main__":
    test_relationship_update()
    test_marriage()
    print("\n✅ 所有繁衍系统测试通过")
