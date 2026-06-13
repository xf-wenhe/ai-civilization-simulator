"""
建筑系统 - 管理建筑建造、升级和效果
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from agent import Agent
from world_state import WorldState, BuildingType, Building


# 建筑配置
BUILDING_CONFIGS = {
    BuildingType.HOUSE: {
        1: {"name": "茅屋", "cost": {"wood": 10, "stone": 5}, "effect": "可生育"},
        2: {"name": "木屋", "cost": {"wood": 20, "stone": 10}, "effect": "恢复+20%"},
        3: {"name": "石屋", "cost": {"wood": 15, "stone": 25}, "effect": "恢复+40%"},
        4: {"name": "豪宅", "cost": {"wood": 30, "stone": 40, "knowledge": 10}, "effect": "恢复+80%"},
    },
    BuildingType.WELL: {
        1: {"name": "简易井", "cost": {"stone": 10, "wood": 5}, "effect": "周围3格可喝水"},
        2: {"name": "深井", "cost": {"stone": 20, "wood": 10}, "effect": "周围5格可喝水"},
        3: {"name": "石井", "cost": {"stone": 35}, "effect": "周围7格可喝水"},
    },
    BuildingType.WAREHOUSE: {
        1: {"name": "木箱", "cost": {"wood": 15}, "effect": "存储100单位"},
        2: {"name": "仓库", "cost": {"wood": 30, "stone": 15}, "effect": "存储300单位"},
        3: {"name": "大仓库", "cost": {"wood": 50, "stone": 30}, "effect": "存储1000单位"},
    }
}


class BuildingSystem:
    """管理建筑建造和效果"""

    def __init__(self, world: WorldState):
        self.world = world
        self.buildings: Dict[str, Building] = {}
        self.building_counter = 0

    def can_build(
        self,
        agent: Agent,
        building_type: BuildingType,
        level: int
    ) -> Tuple[bool, str]:
        """检查是否可以建造"""

        if building_type not in BUILDING_CONFIGS:
            return False, "未知建筑类型"

        if level not in BUILDING_CONFIGS[building_type]:
            return False, "未知建筑等级"

        config = BUILDING_CONFIGS[building_type][level]
        cost = config["cost"]

        # 检查资源
        for resource, amount in cost.items():
            if agent.inventory.get(resource, 0) < amount:
                return False, f"资源不足: 需要{amount}个{resource}"

        # 房屋特殊检查：已有房屋
        if building_type == BuildingType.HOUSE:
            if agent.home_location is not None:
                return False, "已有房屋"

        return True, "可以建造"

    def build(
        self,
        agent: Agent,
        building_type: BuildingType,
        level: int,
        current_tick: int
    ) -> Optional[Building]:
        """建造建筑"""

        can_build, reason = self.can_build(agent, building_type, level)
        if not can_build:
            print(f"⚠️ 无法建造: {reason}")
            return None

        config = BUILDING_CONFIGS[building_type][level]
        cost = config["cost"]

        # 消耗资源（使用get避免KeyError）
        for resource, amount in cost.items():
            agent.inventory[resource] = agent.inventory.get(resource, 0) - amount

        # 创建建筑
        self.building_counter += 1
        building_id = f"building_{self.building_counter}"

        building = Building(
            id=building_id,
            type=building_type,
            level=level,
            position=agent.position,
            owner_id=agent.id,
            build_tick=current_tick,
            name=config["name"]
        )

        self.buildings[building_id] = building

        # 添加到Location
        location = self.world.get_location(agent.position)
        if location:
            location.buildings.append(building_id)

        # 如果是房屋，设置home_location
        if building_type == BuildingType.HOUSE:
            agent.home_location = agent.position

        return building

    def get_nearby_buildings(
        self,
        position: Tuple[int, int],
        building_type: Optional[BuildingType] = None
    ) -> List[Building]:
        """获取附近的建筑"""

        nearby = []

        for building in self.buildings.values():
            # 距离计算
            distance = abs(building.position[0] - position[0]) + abs(building.position[1] - position[1])

            # 水井范围
            # TODO: range_map logic duplicates information that should be in BUILDING_CONFIGS
            # Consider adding a numeric "range" field to BUILDING_CONFIGS for each level
            if building.type == BuildingType.WELL:
                range_map = {1: 3, 2: 5, 3: 7}
                if distance <= range_map.get(building.level, 3):
                    if building_type is None or building.type == building_type:
                        nearby.append(building)

            # 其他建筑：当前位置
            elif distance == 0:
                if building_type is None or building.type == building_type:
                    nearby.append(building)

        return nearby

    def get_building_effect(self, building: Building) -> str:
        """获取建筑效果描述"""
        config = BUILDING_CONFIGS.get(building.type, {}).get(building.level, {})
        return config.get("effect", "无效果")