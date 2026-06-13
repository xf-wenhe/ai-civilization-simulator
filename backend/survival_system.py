"""
生存系统管理智能体的饥饿、口渴、健康和死亡。
"""

from typing import Optional, Tuple
from agent import Agent
from world_state import WorldState, BiomeType


class SurvivalSystem:
    """管理智能体生存需求"""

    # 衰减速率
    HUNGER_DECAY_BASE = 1.5
    THIRST_DECAY_BASE = 2.0
    ACTIVITY_DECAY_BONUS = 0.5

    # 恢复值
    FOOD_RESTORE = 30
    WATER_RESTORE = 40
    RIVER_DRINK_RESTORE = 50

    # 健康伤害
    LOW_NEED_DAMAGE = 5
    ZERO_NEED_DAMAGE = 15

    def __init__(self, world: WorldState):
        self.world = world

    def update_needs(self, agent: Agent, action_type: str):
        """更新智能体的饥饿和口渴值"""

        if not agent.is_alive:
            return

        # 基础衰减
        agent.hunger = max(0, agent.hunger - self.HUNGER_DECAY_BASE)
        agent.thirst = max(0, agent.thirst - self.THIRST_DECAY_BASE)

        # 高强度活动额外消耗
        if action_type in ["gather", "move", "build", "craft"]:
            agent.hunger = max(0, agent.hunger - self.ACTIVITY_DECAY_BONUS)
            agent.thirst = max(0, agent.thirst - self.ACTIVITY_DECAY_BONUS)

        # 应用健康影响
        self._apply_health_damage(agent)

    def _apply_health_damage(self, agent: Agent):
        """应用饥饿/口渴对健康的影响"""

        if agent.hunger < 20 or agent.thirst < 20:
            agent.health = max(0, agent.health - self.LOW_NEED_DAMAGE)

        if agent.hunger == 0 or agent.thirst == 0:
            agent.health = max(0, agent.health - self.ZERO_NEED_DAMAGE)

    def eat(self, agent: Agent, amount: int = 1) -> bool:
        """进食恢复饥饿值"""

        if agent.inventory.get("food", 0) >= amount:
            agent.inventory["food"] -= amount
            agent.hunger = min(100, agent.hunger + self.FOOD_RESTORE)
            return True
        return False

    def drink(self, agent: Agent) -> bool:
        """喝水恢复口渴值"""

        # 优先从库存喝水
        if agent.inventory.get("water", 0) > 0:
            agent.inventory["water"] -= 1
            agent.thirst = min(100, agent.thirst + self.WATER_RESTORE)
            return True

        # 检查是否在河流附近（可直接喝水）
        location = self.world.get_location(agent.position)
        if location and location.biome == BiomeType.RIVER:
            agent.thirst = min(100, agent.thirst + self.RIVER_DRINK_RESTORE)
            return True

        return False

    def check_death(self, agent: Agent, current_tick: int) -> bool:
        """检查智能体是否死亡"""

        if agent.health <= 0 and agent.is_alive:
            agent.is_alive = False
            agent.death_tick = current_tick
            return True
        return False

    def revive(self, agent: Agent, buildings: list) -> bool:
        """复活智能体（限制1次）"""

        if agent.revival_count >= 1:
            return False

        # 找到最近的建筑
        if buildings:
            # 优先房屋，其次水井
            houses = [b for b in buildings if b.get("type") == "house"]
            if houses:
                # 找最近的房屋
                nearest = min(houses, key=lambda b: abs(b["position"][0] - agent.position[0]) + abs(b["position"][1] - agent.position[1]))
                agent.position = nearest["position"]
            else:
                wells = [b for b in buildings if b.get("type") == "well"]
                if wells:
                    nearest = min(wells, key=lambda b: abs(b["position"][0] - agent.position[0]) + abs(b["position"][1] - agent.position[1]))
                    agent.position = nearest["position"]
        else:
            # 无建筑，在世界中心复活
            agent.position = [self.world.width // 2, self.world.height // 2]

        # 恢复状态
        agent.health = 50
        agent.energy = 50
        agent.hunger = 70
        agent.thirst = 70
        agent.is_alive = True
        agent.death_tick = None
        agent.revival_count += 1

        # 保留20%资源
        for resource in list(agent.inventory.keys()):
            agent.inventory[resource] = int(agent.inventory[resource] * 0.2)

        return True