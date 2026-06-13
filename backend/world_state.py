"""
World state manager for AI civilization simulator.
Manages environment, resources, locations, and global events.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import random


class BiomeType(Enum):
    """World biome types"""
    FOREST = "forest"
    PLAINS = "plains"
    MOUNTAIN = "mountain"
    RIVER = "river"
    DESERT = "desert"
    VILLAGE = "village"


class ResourceType(Enum):
    """Available resources"""
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    WATER = "water"
    KNOWLEDGE = "knowledge"


class BuildingType(Enum):
    """建筑类型"""
    HOUSE = "house"
    WELL = "well"
    WAREHOUSE = "warehouse"


@dataclass
class Building:
    """建筑实例"""
    id: str
    type: BuildingType
    level: int
    position: Tuple[int, int]
    owner_id: str
    build_tick: int
    name: str = ""  # 建筑名称


@dataclass
class Location:
    """World location"""
    position: Tuple[int, int]
    biome: BiomeType
    resources: Dict[ResourceType, int] = field(default_factory=dict)
    agents_present: List[str] = field(default_factory=list)
    buildings: List[str] = field(default_factory=list)


@dataclass
class WorldState:
    """Global world state"""

    # Configuration
    width: int = 50
    height: int = 50

    # Time
    tick: int = 0
    day: int = 1
    time_of_day: float = 0.0  # 0-24 hours

    # Environment
    locations: Dict[Tuple[int, int], Location] = field(default_factory=dict)
    weather: str = "clear"

    # Global state
    total_resources_gathered: Dict[ResourceType, int] = field(default_factory=dict)
    events_log: List[str] = field(default_factory=list)

    def initialize_world(self):
        """Generate initial world state"""
        # Create locations with biomes and resources
        for x in range(self.width):
            for y in range(self.height):
                biome = self._generate_biome(x, y)
                resources = self._generate_resources(biome)
                self.locations[(x, y)] = Location(
                    position=(x, y),
                    biome=biome,
                    resources=resources
                )

        self.events_log.append(f"Day {self.day}: World created")

    def _generate_biome(self, x: int, y: int) -> BiomeType:
        """Generate biome based on position"""
        # Simple biome generation - can be more sophisticated later
        center_dist = abs(x - self.width//2) + abs(y - self.height//2)

        if center_dist < 5:
            return BiomeType.VILLAGE
        elif random.random() < 0.3:
            return BiomeType.FOREST
        elif random.random() < 0.2:
            return BiomeType.RIVER
        elif center_dist > 20:
            return BiomeType.MOUNTAIN
        else:
            return BiomeType.PLAINS

    def _generate_resources(self, biome: BiomeType) -> Dict[ResourceType, int]:
        """Generate resources based on biome"""
        resources = {}

        if biome == BiomeType.FOREST:
            resources[ResourceType.WOOD] = random.randint(10, 30)
            resources[ResourceType.FOOD] = random.randint(5, 15)
        elif biome == BiomeType.RIVER:
            resources[ResourceType.WATER] = random.randint(20, 50)
            resources[ResourceType.FOOD] = random.randint(3, 8)
        elif biome == BiomeType.PLAINS:
            resources[ResourceType.FOOD] = random.randint(5, 12)
        elif biome == BiomeType.MOUNTAIN:
            resources[ResourceType.STONE] = random.randint(15, 40)
        elif biome == BiomeType.VILLAGE:
            resources[ResourceType.KNOWLEDGE] = random.randint(1, 5)

        return resources

    def get_location(self, position: Tuple[int, int]) -> Optional[Location]:
        """Get location at position"""
        return self.locations.get(position)

    def update_agent_position(self, agent_id: str, old_pos: Tuple[int, int], new_pos: Tuple[int, int]):
        """Update agent presence at locations"""
        if old_pos in self.locations:
            self.locations[old_pos].agents_present.remove(agent_id)
        if new_pos in self.locations:
            self.locations[new_pos].agents_present.append(agent_id)

    def gather_resource(self, position: Tuple[int, int], resource_type: ResourceType, amount: int) -> int:
        """Gather resource from location, return actual amount gathered"""
        location = self.get_location(position)
        if not location:
            return 0

        available = location.resources.get(resource_type, 0)
        gathered = min(available, amount)

        location.resources[resource_type] = available - gathered
        self.total_resources_gathered[resource_type] = self.total_resources_gathered.get(resource_type, 0) + gathered

        return gathered

    def advance_time(self):
        """Advance world time by one tick"""
        self.tick += 1
        self.time_of_day += 0.5  # Each tick = 0.5 hours

        if self.time_of_day >= 24:
            self.time_of_day = 0
            self.day += 1
            self.events_log.append(f"Day {self.day} begins")
            self._regenerate_resources()

    def _regenerate_resources(self):
        """Regenerate resources daily"""
        for location in self.locations.values():
            if location.biome == BiomeType.FOREST:
                location.resources[ResourceType.WOOD] = min(
                    location.resources.get(ResourceType.WOOD, 0) + 5,
                    30
                )
                location.resources[ResourceType.FOOD] = min(
                    location.resources.get(ResourceType.FOOD, 0) + 3,
                    15
                )
            elif location.biome == BiomeType.RIVER:
                location.resources[ResourceType.WATER] = min(
                    location.resources.get(ResourceType.WATER, 0) + 10,
                    50
                )

    def to_dict(self) -> Dict:
        """Serialize world state"""
        return {
            "width": self.width,
            "height": self.height,
            "tick": self.tick,
            "day": self.day,
            "time_of_day": self.time_of_day,
            "weather": self.weather,
            "locations": {
                f"{pos[0]},{pos[1]}": {
                    "position": loc.position,
                    "biome": loc.biome.value,
                    "resources": {r.value: v for r, v in loc.resources.items()},
                    "agents_present": loc.agents_present,
                    "buildings": loc.buildings
                }
                for pos, loc in self.locations.items()
            },
            "total_resources_gathered": {r.value: v for r, v in self.total_resources_gathered.items()},
            "events_log": self.events_log
        }