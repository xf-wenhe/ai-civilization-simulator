"""测试建筑系统"""

from building_system import BuildingSystem, BUILDING_CONFIGS
from world_state import WorldState, BuildingType
from agent import Agent, PersonalityTrait

def test_can_build():
    """测试建造条件检查"""
    world = WorldState(width=10, height=10)
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    agent.inventory["wood"] = 10
    agent.inventory["stone"] = 5

    can, reason = sys.can_build(agent, BuildingType.HOUSE, 1)
    assert can == True
    print(f"✓ 建造条件检查通过: {reason}")

def test_build_house():
    """测试建造房屋"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    agent.inventory["wood"] = 15
    agent.inventory["stone"] = 10

    building = sys.build(agent, BuildingType.HOUSE, 1, current_tick=100)

    assert building is not None
    assert building.name == "茅屋"
    assert agent.home_location == (5, 5)
    assert agent.inventory["wood"] == 5

    print(f"✓ 建造房屋测试通过: {building.name}")

if __name__ == "__main__":
    test_can_build()
    test_build_house()
    print("\n✅ 所有建筑系统测试通过")
