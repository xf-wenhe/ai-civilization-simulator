"""
繁衍系统 - 管理关系发展、婚姻、怀孕和生育
"""

from typing import Dict, List, Optional, Tuple
import random

from agent import Agent, PersonalityTrait, ActionType, Relationship
from world_state import WorldState, BiomeType


class ReproductionSystem:
    """管理智能体繁衍"""

    # 繁衍相关常量
    PREGNANCY_PROBABILITY = 0.05  # 怀孕概率 5%
    PREGNANCY_DURATION = 20  # 怀孕持续tick数

    def __init__(self, world: WorldState):
        self.world = world

    def _is_valid_spawn_position(self, position: Tuple[int, int]) -> bool:
        """检查位置是否有效（在边界内且不是水域）"""
        x, y = position

        # 检查边界
        if x < 0 or x >= self.world.width or y < 0 or y >= self.world.height:
            return False

        # 检查地形
        location = self.world.get_location(position)
        if location and location.biome == BiomeType.RIVER:
            return False

        return True

    def _find_safe_spawn_position(self, preferred_position: Tuple[int, int]) -> Tuple[int, int]:
        """找到一个安全的生成位置"""
        # 如果首选位置有效，使用它
        if self._is_valid_spawn_position(preferred_position):
            return preferred_position

        # 否则在附近寻找有效位置
        x, y = preferred_position
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                test_pos = (x + dx, y + dy)
                if self._is_valid_spawn_position(test_pos):
                    return test_pos

        # 最后回退到世界中心
        center = (self.world.width // 2, self.world.height // 2)
        return center

    def update_relationship(
        self,
        agent: Agent,
        target_id: str,
        interaction_type: str = "friendly"
    ) -> str:
        """更新关系"""

        if target_id not in agent.relationships:
            agent.relationships[target_id] = Relationship(
                agent_id=target_id,
                trust=0.0,
                friendship=0.0,
                interactions=0
            )

        relationship = agent.relationships[target_id]

        # 增加互动次数
        relationship.interactions += 1

        # 根据互动类型更新关系值
        if interaction_type == "friendly":
            trust_gain = 0.05
            friendship_gain = 0.1
        elif interaction_type == "conflict":
            trust_gain = -0.1
            friendship_gain = -0.15
        else:
            trust_gain = 0.05
            friendship_gain = 0.05

        # 性格影响
        if agent.personality[PersonalityTrait.AGREEABLENESS] > 0.7:
            friendship_gain *= 1.3
        if agent.personality[PersonalityTrait.NEUROTICISM] > 0.7:
            if friendship_gain < 0:
                friendship_gain *= 1.2

        relationship.trust = max(-1, min(1, relationship.trust + trust_gain))
        relationship.friendship = max(0, min(1, relationship.friendship + friendship_gain))

        # 返回关系阶段
        return self.get_relationship_stage(agent, target_id)

    def get_relationship_stage(self, agent: Agent, target_id: str) -> str:
        """获取关系阶段"""

        if target_id not in agent.relationships:
            return "陌生人"

        rel = agent.relationships[target_id]
        trust = rel.trust
        friendship = rel.friendship
        interactions = rel.interactions

        if agent.relationship_status == "married" and agent.spouse_id == target_id:
            return "配偶"

        if friendship >= 0.8 and trust >= 0.7:
            return "恋爱"
        elif friendship >= 0.7 and trust >= 0.5:
            return "好友"
        elif friendship >= 0.5:
            return "朋友"
        elif friendship >= 0.2 or interactions >= 3:
            return "熟人"
        else:
            return "陌生人"

    def can_propose_marriage(self, agent: Agent, target: Agent) -> Tuple[bool, str]:
        """检查是否可以求婚"""

        # 已婚检查
        if agent.relationship_status != "single":
            return False, "已有伴侣"

        if target.relationship_status != "single":
            return False, "对方已有伴侣"

        # 关系检查
        if target.id not in agent.relationships:
            return False, "关系不够亲密"

        rel = agent.relationships[target.id]
        if rel.friendship < 0.8 or rel.trust < 0.7:
            return False, "关系不够亲密"

        # 房屋检查
        if not agent.home_location:
            return False, "需要房屋"

        return True, "可以求婚"

    def marry(self, agent1: Agent, agent2: Agent) -> bool:
        """结婚"""

        can_marry, reason = self.can_propose_marriage(agent1, agent2)
        if not can_marry:
            print(f"⚠️ 无法结婚: {reason}")
            return False

        # 更新婚姻状态
        agent1.spouse_id = agent2.id
        agent1.relationship_status = "married"
        agent2.spouse_id = agent1.id
        agent2.relationship_status = "married"

        # 共享房屋
        if agent1.home_location:
            agent2.home_location = agent1.home_location
        elif agent2.home_location:
            agent1.home_location = agent2.home_location

        print(f"💒 {agent1.name} 和 {agent2.name} 结婚了！")
        return True

    def can_conceive(self, agent: Agent) -> Tuple[bool, str]:
        """检查是否可以怀孕"""

        if agent.relationship_status != "married":
            return False, "未婚"

        if agent.pregnancy_start_tick is not None:
            return False, "已怀孕"

        if not agent.home_location:
            return False, "无房屋"

        if agent.inventory.get("food", 0) < 20:
            return False, "食物不足"

        if agent.inventory.get("water", 0) < 10:
            return False, "水源不足"

        # 使用常量判断怀孕概率
        if random.random() > self.PREGNANCY_PROBABILITY:
            return False, "时机未到"

        return True, "可以怀孕"

    def start_pregnancy(self, agent: Agent, current_tick: int) -> bool:
        """开始怀孕"""

        can, reason = self.can_conceive(agent)
        if not can:
            return False

        agent.pregnancy_start_tick = current_tick
        print(f"🤰 {agent.name} 怀孕了！")
        return True

    def check_pregnancy_progress(self, agent: Agent, current_tick: int) -> bool:
        """检查怀孕进度"""

        if agent.pregnancy_start_tick is None:
            return False

        # 使用常量判断怀孕时长
        if current_tick - agent.pregnancy_start_tick >= self.PREGNANCY_DURATION:
            return True  # 可以生了

        return False

    def create_child(
        self,
        parent1: Agent,
        parent2: Agent,
        current_tick: int
    ) -> Optional[Agent]:
        """生成孩子"""

        # 验证配偶关系
        if parent1.spouse_id != parent2.id or parent2.spouse_id != parent1.id:
            print(f"⚠️ 无法生育: 不是配偶关系")
            return None

        # 验证parent1是否怀孕并已到分娩期
        if parent1.pregnancy_start_tick is None:
            print(f"⚠️ 无法生育: {parent1.name} 未怀孕")
            return None

        if current_tick - parent1.pregnancy_start_tick < self.PREGNANCY_DURATION:
            print(f"⚠️ 无法生育: 怀孕尚未足月")
            return None

        # 性格遗传（50%父母平均 + 50%随机）
        personality = {}
        for trait in PersonalityTrait:
            parent_avg = (parent1.personality[trait] + parent2.personality[trait]) / 2
            inherited = parent_avg * 0.5 + random.uniform(0.3, 0.7) * 0.5
            personality[trait] = inherited

        # 技能遗传（30%父母平均）
        skills = {}
        for skill in ["gathering", "crafting", "communication"]:
            p1_skill = parent1.skills.get(skill, 0.3)
            p2_skill = parent2.skills.get(skill, 0.3)
            inherited = (p1_skill + p2_skill) / 2 * 0.3
            skills[skill] = inherited

        # 名字生成
        child_names = ["小明", "小红", "小刚", "小芳", "小华", "小丽"]
        name = random.choice(child_names)

        # 确定安全的生成位置（优先使用家，验证有效性）
        preferred_position = parent1.home_location or parent2.home_location or (0, 0)
        position = self._find_safe_spawn_position(preferred_position)

        # 创建孩子Agent - 使用父母ID和时间戳确保唯一性
        child_id = f"agent_child_{parent1.id}_{parent2.id}_{current_tick}"

        child = Agent(
            id=child_id,
            name=name,
            personality=personality,
            position=position,
            skills=skills,
            hunger=100,
            thirst=100,
            energy=80
        )

        # 记录到父母
        parent1.children.append(child_id)
        parent2.children.append(child_id)

        # 重置怀孕状态（parent1是怀孕的一方）
        parent1.pregnancy_start_tick = None

        print(f"👶 {parent1.name} 和 {parent2.name} 生下了 {name}！")
        return child