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
    world.initialize_world()
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

    # 设置怀孕状态（到达分娩期）
    agent1.pregnancy_start_tick = 80  # 20 ticks before current_tick=100

    # 创建孩子
    child = sys.create_child(agent1, agent2, current_tick=100)

    assert child is not None, "应该能够创建孩子"
    assert child.id == "agent_child_test1_test2_100", f"孩子ID应该是唯一的，实际为: {child.id}"
    assert child.position == (5, 5), f"孩子位置应该在家，实际为: {child.position}"
    assert child.hunger == 100
    assert child.thirst == 100
    assert child.id in agent1.children
    assert child.id in agent2.children
    assert agent1.pregnancy_start_tick is None

    print("✓ 生育测试通过")


def test_unique_child_ids():
    """测试多个孩子在同一tick的唯一ID"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = ReproductionSystem(world)

    # 第一对父母
    agent1 = Agent(id="parent1", name="Alice", personality={t: 0.5 for t in PersonalityTrait})
    agent1.home_location = (3, 3)
    agent1.inventory = {"food": 30, "water": 20}

    agent2 = Agent(id="parent2", name="Bob", personality={t: 0.5 for t in PersonalityTrait})
    agent2.home_location = (3, 3)

    # 第二对父母
    agent3 = Agent(id="parent3", name="Carol", personality={t: 0.5 for t in PersonalityTrait})
    agent3.home_location = (7, 7)
    agent3.inventory = {"food": 30, "water": 20}

    agent4 = Agent(id="parent4", name="Dave", personality={t: 0.5 for t in PersonalityTrait})
    agent4.home_location = (7, 7)

    # 结婚
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")
        sys.update_relationship(agent3, agent4.id, "friendly")
        sys.update_relationship(agent4, agent3.id, "friendly")

    sys.marry(agent1, agent2)
    sys.marry(agent3, agent4)

    # 设置怀孕
    agent1.pregnancy_start_tick = 80
    agent3.pregnancy_start_tick = 80

    # 在同一tick创建孩子
    child1 = sys.create_child(agent1, agent2, current_tick=100)
    child2 = sys.create_child(agent3, agent4, current_tick=100)

    assert child1 is not None and child2 is not None, "应该能够创建两个孩子"
    assert child1.id != child2.id, f"两个孩子ID应该不同: {child1.id} vs {child2.id}"
    assert "parent1_parent2_100" in child1.id
    assert "parent3_parent4_100" in child2.id

    print("✓ 唯一ID测试通过")


def test_pregnancy_validation():
    """测试怀孕验证"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = ReproductionSystem(world)

    agent1 = Agent(id="test1", name="Alice", personality={t: 0.5 for t in PersonalityTrait})
    agent1.home_location = (5, 5)
    agent1.inventory = {"food": 30, "water": 20}

    agent2 = Agent(id="test2", name="Bob", personality={t: 0.5 for t in PersonalityTrait})

    # 建立关系并结婚
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")

    sys.marry(agent1, agent2)

    # 尝试在没有怀孕的情况下创建孩子
    child = sys.create_child(agent1, agent2, current_tick=100)
    assert child is None, "未怀孕时不应该创建孩子"

    # 设置怀孕但未到分娩期
    agent1.pregnancy_start_tick = 95  # 只有5 ticks，不够20
    child = sys.create_child(agent1, agent2, current_tick=100)
    assert child is None, "怀孕未足月时不应该创建孩子"

    # 设置足月怀孕
    agent1.pregnancy_start_tick = 80
    child = sys.create_child(agent1, agent2, current_tick=100)
    assert child is not None, "怀孕足月时应该能够创建孩子"

    print("✓ 怀孕验证测试通过")


def test_safe_spawn_position():
    """测试安全的生成位置"""
    world = WorldState(width=10, height=10)
    world.initialize_world()
    sys = ReproductionSystem(world)

    agent1 = Agent(id="test1", name="Alice", personality={t: 0.5 for t in PersonalityTrait})
    agent1.home_location = (5, 5)
    agent1.inventory = {"food": 30, "water": 20}

    agent2 = Agent(id="test2", name="Bob", personality={t: 0.5 for t in PersonalityTrait})

    # 建立关系并结婚
    for _ in range(15):
        sys.update_relationship(agent1, agent2.id, "friendly")
        sys.update_relationship(agent2, agent1.id, "friendly")

    sys.marry(agent1, agent2)

    # 测试正常位置
    agent1.pregnancy_start_tick = 80
    child = sys.create_child(agent1, agent2, current_tick=100)
    assert child is not None
    x, y = child.position
    assert 0 <= x < 10 and 0 <= y < 10, "位置应该在世界边界内"

    # 测试无效位置的回退（假设(0,0)可能无效）
    agent1.home_location = None
    agent2.home_location = None
    agent1.pregnancy_start_tick = 80
    child2 = sys.create_child(agent1, agent2, current_tick=100)
    assert child2 is not None
    x2, y2 = child2.position
    assert 0 <= x2 < 10 and 0 <= y2 < 10, "回退位置应该在世界边界内"

    print("✓ 安全位置测试通过")

if __name__ == "__main__":
    test_relationship_update()
    test_marriage()
    test_pregnancy()
    test_child_creation()
    test_unique_child_ids()
    test_pregnancy_validation()
    test_safe_spawn_position()
    print("\n✅ 所有繁衍系统测试通过")
