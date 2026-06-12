"""
Crafting system - agents can create items and tools from gathered resources.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os
import random
import random  # Add at top of file


@dataclass
class Recipe:
    """Crafting recipe"""
    name: str
    category: str  # tool, food, shelter, weapon, clothing
    required_resources: Dict[str, int]  # resource -> amount
    required_skills: Dict[str, float]  # skill -> minimum level
    result_amount: int  # How many items created
    difficulty: float  # 0-1, higher = harder


@dataclass
class CraftedItem:
    """Crafted item instance"""
    name: str
    category: str
    quality: float  # 0-1
    creator_id: str
    timestamp: int


class CraftingSystem:
    """Manages crafting recipes and item creation"""

    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self.crafted_items: Dict[str, List[CraftedItem]] = {}  # agent_id -> items

        # Initialize with basic recipes
        self._init_basic_recipes()

    def _init_basic_recipes(self):
        """Initialize basic crafting recipes"""

        basic_recipes = [
            Recipe(
                name="stone_axe",
                category="tool",
                required_resources={"stone": 5, "wood": 3},
                required_skills={"crafting": 0.3},
                result_amount=1,
                difficulty=0.3
            ),
            Recipe(
                name="wooden_shelter",
                category="shelter",
                required_resources={"wood": 20, "stone": 5},
                required_skills={"crafting": 0.5},
                result_amount=1,
                difficulty=0.5
            ),
            Recipe(
                name="cooked_food",
                category="food",
                required_resources={"food": 3, "wood": 1},
                required_skills={"crafting": 0.2},
                result_amount=2,
                difficulty=0.2
            ),
            Recipe(
                name="stone_hammer",
                category="tool",
                required_resources={"stone": 8, "wood": 4},
                required_skills={"crafting": 0.4},
                result_amount=1,
                difficulty=0.4
            ),
            Recipe(
                name="water_container",
                category="tool",
                required_resources={"wood": 5},
                required_skills={"crafting": 0.25},
                result_amount=1,
                difficulty=0.25
            ),
        ]

        for recipe in basic_recipes:
            self.recipes[recipe.name] = recipe

    def get_available_recipes(self, agent_skills: Dict[str, float]) -> List[str]:
        """Get recipes agent can craft based on skills"""
        available = []

        for recipe_name, recipe in self.recipes.items():
            can_craft = True

            for skill, min_level in recipe.required_skills.items():
                if agent_skills.get(skill, 0.0) < min_level:
                    can_craft = False
                    break

            if can_craft:
                available.append(recipe_name)

        return available

    def can_craft_recipe(self, recipe_name: str, agent_resources: Dict[str, int],
                         agent_skills: Dict[str, float]) -> bool:
        """Check if agent can craft specific recipe"""

        if recipe_name not in self.recipes:
            return False

        recipe = self.recipes[recipe_name]

        # Check resources
        for resource, amount in recipe.required_resources.items():
            if agent_resources.get(resource, 0) < amount:
                return False

        # Check skills
        for skill, min_level in recipe.required_skills.items():
            if agent_skills.get(skill, 0.0) < min_level:
                return False

        return True

    def craft_item(self, recipe_name: str, agent_id: str, agent_resources: Dict[str, int],
                   agent_skills: Dict[str, float], timestamp: int) -> Optional[CraftedItem]:
        """Craft an item"""

        if not self.can_craft_recipe(recipe_name, agent_resources, agent_skills):
            return None

        recipe = self.recipes[recipe_name]

        # Consume resources
        for resource, amount in recipe.required_resources.items():
            agent_resources[resource] -= amount

        # Calculate quality based on skill level and difficulty
        skill_level = agent_skills.get("crafting", 0.3)
        quality = skill_level - recipe.difficulty + 0.3
        quality = max(0.0, min(1.0, quality))

        # Add random variance
        quality += random.uniform(-0.1, 0.1)
        quality = max(0.0, min(1.0, quality))

        item = CraftedItem(
            name=recipe_name,
            category=recipe.category,
            quality=quality,
            creator_id=agent_id,
            timestamp=timestamp
        )

        # Record crafted item
        if agent_id not in self.crafted_items:
            self.crafted_items[agent_id] = []

        self.crafted_items[agent_id].append(item)

        # Chance to improve crafting skill
        if random.random() < 0.15:
            agent_skills["crafting"] = min(1.0, agent_skills.get("crafting", 0) + 0.05)

        return item

    def get_agent_crafted_items(self, agent_id: str) -> List[CraftedItem]:
        """Get items crafted by agent"""
        return self.crafted_items.get(agent_id, [])

    def add_recipe(self, recipe: Recipe):
        """Add new recipe to system"""
        self.recipes[recipe.name] = recipe

    def save_recipes(self, filepath: str = "data/recipes.json"):
        """Save recipes to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data = {
            name: {
                "name": r.name,
                "category": r.category,
                "required_resources": r.required_resources,
                "required_skills": r.required_skills,
                "result_amount": r.result_amount,
                "difficulty": r.difficulty
            }
            for name, r in self.recipes.items()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_recipes(self, filepath: str = "data/recipes.json"):
        """Load recipes from file"""
        if not os.path.exists(filepath):
            return

        with open(filepath, 'r') as f:
            data = json.load(f)

        for name, recipe_data in data.items():
            recipe = Recipe(**recipe_data)
            self.recipes[name] = recipe


import random  # Add at top of file