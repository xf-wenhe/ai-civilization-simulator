"""测试生存系统"""

from survival_system import SurvivalSystem
from agent import Agent, PersonalityTrait
from world_state import WorldState, BiomeType

def test_hunger_decay():
    """测试饥饿值衰减"""
    world = WorldState(width=10, height=10)
    sys = SurvivalSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    assert agent.hunger == 100.0

    # 正常衰减
    sys.update_needs(agent, "rest")
    assert agent.hunger == 100.0 - 1.5

    # 高强度活动衰减
    sys.update_needs(agent, "gather")
    assert agent.hunger == 100.0 - 1.5 - 1.5 - 0.5

    print("✓ 饥饿值衰减测试通过")

def test_eat():
    """测试进食"""
    world = WorldState(width=10, height=10)
    sys = SurvivalSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    agent.hunger = 50
    agent.inventory["food"] = 5

    success = sys.eat(agent)
    assert success == True
    assert agent.hunger == 50 + 30
    assert agent.inventory["food"] == 4

    print("✓ 进食测试通过")

def test_death():
    """测试死亡"""
    world = WorldState(width=10, height=10)
    sys = SurvivalSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    agent.health = 0
    died = sys.check_death(agent, 100)

    assert died == True
    assert agent.is_alive == False
    assert agent.death_tick == 100

    print("✓ 死亡测试通过")

if __name__ == "__main__":
    test_hunger_decay()
    test_eat()
    test_death()
    print("\n✅ 所有生存系统测试通过")