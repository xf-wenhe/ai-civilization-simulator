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

def test_build_insufficient_resources():
    """测试资源不足时无法建造"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    # 只给部分资源
    agent.inventory["wood"] = 5
    agent.inventory["stone"] = 2

    building = sys.build(agent, BuildingType.HOUSE, 1, current_tick=100)

    assert building is None
    assert agent.inventory["wood"] == 5  # 资源未消耗
    assert agent.inventory["stone"] == 2

    print("✓ 资源不足测试通过")

def test_build_resource_not_in_inventory():
    """测试资源不在库存中（KeyError场景）"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    # 只给木石，不给知识（测试豪宅建造）
    agent.inventory["wood"] = 50
    agent.inventory["stone"] = 50
    # 注意：没有给knowledge资源

    can_build, reason = sys.can_build(agent, BuildingType.HOUSE, 4)
    assert can_build == False
    assert "资源不足" in reason

    print("✓ 资源不存在于库存测试通过")

def test_build_already_has_house():
    """测试已有房屋时无法再建"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    agent.inventory["wood"] = 50
    agent.inventory["stone"] = 50
    agent.home_location = (3, 3)  # 已有房屋

    can_build, reason = sys.can_build(agent, BuildingType.HOUSE, 1)
    assert can_build == False
    assert "已有房屋" in reason

    print("✓ 已有房屋检查测试通过")

def test_build_unknown_type():
    """测试未知建筑类型"""
    world = WorldState(width=10, height=10)
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    # 使用不存在的建筑类型（通过字符串模拟）
    can_build, reason = sys.can_build(agent, "unknown_type", 1)
    assert can_build == False
    assert "未知建筑类型" in reason

    print("✓ 未知建筑类型测试通过")

def test_build_unknown_level():
    """测试未知建筑等级"""
    world = WorldState(width=10, height=10)
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    can_build, reason = sys.can_build(agent, BuildingType.HOUSE, 99)
    assert can_build == False
    assert "未知建筑等级" in reason

    print("✓ 未知建筑等级测试通过")

def test_build_well():
    """测试建造水井"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    agent.inventory["stone"] = 20
    agent.inventory["wood"] = 10

    building = sys.build(agent, BuildingType.WELL, 2, current_tick=100)

    assert building is not None
    assert building.name == "深井"
    assert agent.inventory["stone"] == 0

    print(f"✓ 建造水井测试通过: {building.name}")

def test_build_warehouse():
    """测试建造仓库"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    agent.inventory["wood"] = 50
    agent.inventory["stone"] = 30

    building = sys.build(agent, BuildingType.WAREHOUSE, 3, current_tick=100)

    assert building is not None
    assert building.name == "大仓库"
    assert agent.inventory["wood"] == 0

    print(f"✓ 建造仓库测试通过: {building.name}")

def test_get_nearby_buildings():
    """测试获取附近建筑"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    # 建造水井
    agent.inventory["stone"] = 10
    agent.inventory["wood"] = 5
    well = sys.build(agent, BuildingType.WELL, 1, current_tick=100)

    # 在范围内的位置应该能找到水井
    nearby = sys.get_nearby_buildings((5, 5), BuildingType.WELL)
    assert len(nearby) == 1
    assert nearby[0].id == well.id

    # 3格范围内也应该找到
    nearby = sys.get_nearby_buildings((7, 5), BuildingType.WELL)
    assert len(nearby) == 1

    # 超出范围应该找不到
    nearby = sys.get_nearby_buildings((10, 10), BuildingType.WELL)
    assert len(nearby) == 0

    print("✓ 获取附近建筑测试通过")

def test_get_nearby_buildings_no_type_filter():
    """测试获取附近建筑（无类型过滤）"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = BuildingSystem(world)

    agent = Agent(
        id="test",
        name="Test",
        personality={t: 0.5 for t in PersonalityTrait},
        position=(5, 5)
    )

    # 建造多种建筑
    agent.inventory["stone"] = 20
    agent.inventory["wood"] = 20
    sys.build(agent, BuildingType.WELL, 1, current_tick=100)

    agent.position = (6, 6)
    sys.build(agent, BuildingType.WAREHOUSE, 1, current_tick=101)

    # 在(5,5)应该找到水井（范围内）和仓库（当前位置）
    nearby = sys.get_nearby_buildings((5, 5))
    assert len(nearby) >= 1  # 至少有水井

    print("✓ 无类型过滤测试通过")

if __name__ == "__main__":
    test_can_build()
    test_build_house()
    test_build_insufficient_resources()
    test_build_resource_not_in_inventory()
    test_build_already_has_house()
    test_build_unknown_type()
    test_build_unknown_level()
    test_build_well()
    test_build_warehouse()
    test_get_nearby_buildings()
    test_get_nearby_buildings_no_type_filter()
    print("\n✅ 所有建筑系统测试通过")
