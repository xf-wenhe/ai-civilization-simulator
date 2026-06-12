# AI文明增强功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为AI文明模拟器添加生存、建筑、感情、繁衍功能，让智能体可以饥饿、口渴、建造、结婚、生育

**Architecture:** 模块化设计，新增4个独立系统模块（survival_system、building_system、reproduction_system、dialogue_generator），扩展现有Agent类和决策逻辑

**Tech Stack:** Python 3.9, FastAPI, Anthropic Claude API, React 18, TypeScript, Vite

---

## 文件结构规划

### 新增文件
```
backend/
├── survival_system.py          # 生存系统
├── building_system.py          # 建筑系统
├── reproduction_system.py      # 繁衍系统
└── dialogue_generator.py       # 对话生成

frontend/src/
├── components/
│   ├── SurvivalBars.tsx        # 饥饿/口渴显示组件
│   └── RelationshipView.tsx    # 关系展示组件
└── types/
    └── building.ts             # 建筑类型定义
```

### 修改文件
```
backend/
├── agent.py                    # 添加生存/婚姻字段
├── world_state.py             # 添加建筑数据结构
├── orchestrator.py            # 集成所有新系统
└── working_server.py          # 新增API端点

frontend/src/
├── components/
│   ├── AgentCard.tsx          # 显示生存状态
│   ├── AgentDetails.tsx       # 显示关系/家族
│   └── WorldMapComponent.tsx  # 显示建筑
└── App.tsx                    # 新事件翻译
```

---

## 阶段1：生存系统（生存优先）

### Task 1: 扩展Agent类字段

**Files:**
- Modify: `backend/agent.py:61-83`

- [ ] **Step 1: 添加生存系统字段**

在Agent类中添加新字段：

```python
@dataclass
class Agent:
    # Identity
    id: str
    name: str
    personality: Dict[PersonalityTrait, float]

    # State
    position: tuple[int, int] = (0, 0)
    health: float = 100.0
    energy: float = 100.0
    inventory: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, float] = field(default_factory=dict)

    # Mental state
    goals: List[Goal] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)

    # Current state
    current_action: Optional[ActionType] = None
    conversation_history: List[str] = field(default_factory=list)

    # === 新增：生存系统 ===
    hunger: float = 100.0           # 饥饿值 0-100
    thirst: float = 100.0           # 口渴值 0-100
    is_alive: bool = True           # 生命状态
    death_tick: Optional[int] = None  # 死亡时间
    revival_count: int = 0          # 已复活次数

    # === 新增：感情婚姻系统 ===
    spouse_id: Optional[str] = None  # 配偶ID
    relationship_status: str = "single"  # single/dating/married
    children: List[str] = field(default_factory=list)  # 孩子ID
    pregnancy_start_tick: Optional[int] = None  # 怀孕开始时间

    # === 新增：家庭系统 ===
    home_location: Optional[tuple[int, int]] = None  # 家的位置
```

- [ ] **Step 2: 更新to_dict方法**

在`agent.py`的`to_dict`方法中添加新字段序列化：

```python
def to_dict(self) -> Dict:
    """Serialize agent state to dict"""
    return {
        "id": self.id,
        "name": self.name,
        "personality": {t.value: v for t, v in self.personality.items()},
        "position": self.position,
        "health": self.health,
        "energy": self.energy,
        "inventory": self.inventory,
        "skills": self.skills,
        "goals": [{"description": g.description, "priority": g.priority, "completed": g.completed} for g in self.goals],
        "memories": [{"content": m.content, "timestamp": m.timestamp, "importance": m.importance, "memory_type": m.memory_type} for m in self.memories],
        "relationships": {k: {"trust": v.trust, "friendship": v.friendship, "interactions": v.interactions} for k, v in self.relationships.items()},
        "current_action": self.current_action.value if self.current_action else None,
        "conversation_history": self.conversation_history,

        # 新增字段
        "hunger": self.hunger,
        "thirst": self.thirst,
        "is_alive": self.is_alive,
        "death_tick": self.death_tick,
        "revival_count": self.revival_count,
        "spouse_id": self.spouse_id,
        "relationship_status": self.relationship_status,
        "children": self.children,
        "pregnancy_start_tick": self.pregnancy_start_tick,
        "home_location": self.home_location
    }
```

- [ ] **Step 3: 验证修改**

运行服务器测试：

```bash
cd backend && python3 -c "from agent import Agent; a = Agent('test', 'Test', {}); print('hunger:', a.hunger)"
```

Expected: 输出 `hunger: 100.0`

- [ ] **Step 4: 提交**

```bash
git add backend/agent.py
git commit -m "feat: 扩展Agent类添加生存和婚姻字段

- 添加饥饿/口渴/死亡/复活字段
- 添加配偶/孩子/家庭位置字段
- 更新to_dict序列化方法"
```

---

### Task 2: 创建生存系统模块

**Files:**
- Create: `backend/survival_system.py`

- [ ] **Step 1: 创建基础生存系统类**

```python
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
            agent.position = (self.world.width // 2, self.world.height // 2)

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
```

- [ ] **Step 2: 创建测试脚本**

创建`backend/test_survival.py`:

```python
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
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && python3 test_survival.py
```

Expected: 输出 "✅ 所有生存系统测试通过"

- [ ] **Step 4: 提交**

```bash
git add backend/survival_system.py backend/test_survival.py
git commit -m "feat: 实现生存系统核心功能

- 饥饿/口渴值衰减机制
- 进食/喝水恢复
- 健康伤害计算
- 死亡判定
- 复活机制（限制1次）
- 完整测试覆盖"
```

---

### Task 3: 集成生存系统到Orchestrator

**Files:**
- Modify: `backend/orchestrator.py:25-60`
- Modify: `backend/orchestrator.py:188-248`

- [ ] **Step 1: 导入生存系统**

在`orchestrator.py`顶部添加：

```python
from survival_system import SurvivalSystem
```

在`EnhancedAgentOrchestrator.__init__`中初始化：

```python
def __init__(self, world: WorldState, agent_count: int = 5):
    # ... 现有代码 ...

    # Initialize memory system
    self.memory_system = AgentMemorySystem(persist_directory="./data/chroma")

    # === 新增：初始化生存系统 ===
    self.survival_system = SurvivalSystem(world)

    # Create initial agents
    for i in range(agent_count):
        agent = self._create_agent(i)
        self.agents[agent.id] = agent
        self.world.locations[agent.position].agents_present.append(agent.id)
```

- [ ] **Step 2: 修改决策逻辑添加生存优先**

修改`_simulate_decision`方法：

```python
def _simulate_decision(self, agent: Agent) -> Dict:
    """Heuristic-based decision with personality influence"""
    import random

    # === 新增：死亡检查 ===
    if not agent.is_alive:
        return {"action": ActionType.REST, "parameters": "", "reasoning": "Agent is dead"}

    # === 新增：生存优先 ===
    if agent.hunger < 30 or agent.thirst < 30:
        if agent.thirst < agent.hunger and agent.thirst < 30:
            # 优先解决口渴
            return {"action": ActionType.GATHER, "parameters": "water", "reasoning": f"Thirst critical ({agent.thirst:.0f})"}
        elif agent.hunger < 30:
            # 解决饥饿
            return {"action": ActionType.GATHER, "parameters": "food", "reasoning": f"Hunger critical ({agent.hunger:.0f})"}

    # 能量低于30强制休息
    if agent.energy < 30:
        return {"action": ActionType.REST, "parameters": "", "reasoning": "Low energy, need to rest"}

    # 能量恢复后才能继续其他行动
    if agent.energy < 50:
        return {"action": ActionType.REST, "parameters": "", "reasoning": "Low energy, need to rest"}

    # ... 剩余原有逻辑 ...
```

- [ ] **Step 3: 在动作执行后更新生存状态**

修改`execute_action_and_learn`方法：

```python
async def execute_action_and_learn(self, agent: Agent, action_data: Dict):
    """Execute action and store in memory"""

    action = action_data.get("action", ActionType.REST)
    params = action_data.get("parameters", "")
    reasoning = action_data.get("reasoning", "")

    agent.current_action = action

    # Execute action
    result = await self._execute_action(agent, action, params)

    # === 新增：更新生存需求 ===
    self.survival_system.update_needs(agent, action.value if hasattr(action, 'value') else str(action))

    # === 新增：检查死亡 ===
    if self.survival_system.check_death(agent, self.world.tick):
        print(f"💀 {agent.name} 死亡了！原因：健康值归零")
        return

    # Store as episodic memory
    memory_content = f"{action.value.capitalize()} - {reasoning}. Result: {result}"
    self.memory_system.store_memory(
        agent_id=agent.id,
        memory_type="episodic",
        content=memory_content,
        timestamp=self.world.tick,
        importance=self._calculate_importance(action, result)
    )

    # Decrease energy
    if action != ActionType.REST:
        agent.energy = max(0, agent.energy - 10)
```

- [ ] **Step 4: 测试集成**

重启后端服务器：

```bash
cd backend && python3 working_server.py
```

等待10个tick，观察日志：

```bash
# 在另一个终端
curl -s http://localhost:8888/agents | jq '.[0] | {name, hunger, thirst, health}'
```

Expected: 看到hunger和thirst值在减少

- [ ] **Step 5: 提交**

```bash
git add backend/orchestrator.py
git commit -m "feat: 集成生存系统到Orchestrator

- 添加生存系统实例初始化
- 决策逻辑添加生存优先级
- 动作执行后更新饥饿/口渴值
- 检查并处理死亡事件"
```

---

### Task 4: 添加进食和喝水动作

**Files:**
- Modify: `backend/orchestrator.py:285-297`

- [ ] **Step 1: 添加EAT和DRINK动作类型**

在`agent.py`的ActionType枚举中添加：

```python
class ActionType(Enum):
    """Available actions agents can take"""
    MOVE = "move"
    GATHER = "gather"
    CRAFT = "craft"
    COMMUNICATE = "communicate"
    REST = "rest"
    BUILD = "build"
    TEACH = "teach"
    TRADE = "trade"
    # === 新增 ===
    EAT = "eat"
    DRINK = "drink"
```

- [ ] **Step 2: 实现进食和喝水执行方法**

在`orchestrator.py`的`_execute_action`方法中添加：

```python
async def _execute_action(self, agent: Agent, action: ActionType, params: str) -> str:
    """Execute specific action and return result"""

    if action == ActionType.MOVE:
        return self._execute_move(agent, params)
    elif action == ActionType.GATHER:
        return self._execute_gather(agent, params)
    elif action == ActionType.REST:
        return self._execute_rest(agent)
    elif action == ActionType.COMMUNICATE:
        return await self._execute_communicate(agent, params)
    # === 新增 ===
    elif action == ActionType.EAT:
        return self._execute_eat(agent)
    elif action == ActionType.DRINK:
        return self._execute_drink(agent)
    else:
        return "Action not implemented"

def _execute_eat(self, agent: Agent) -> str:
    """执行进食"""
    success = self.survival_system.eat(agent)
    if success:
        return f"Ate food, hunger now {agent.hunger:.0f}"
    return "No food available"

def _execute_drink(self, agent: Agent) -> str:
    """执行喝水"""
    success = self.survival_system.drink(agent)
    if success:
        return f"Drank water, thirst now {agent.thirst:.0f}"
    return "No water available"
```

- [ ] **Step 3: 更新决策逻辑**

修改`_simulate_decision`方法，在生存优先部分：

```python
# === 新增：主动进食/喝水 ===
if agent.hunger < 50 and agent.inventory.get("food", 0) > 0:
    return {"action": ActionType.EAT, "parameters": "", "reasoning": "Eating food from inventory"}

if agent.thirst < 50:
    # 检查是否有水或靠近河流
    location = self.world.get_location(agent.position)
    if agent.inventory.get("water", 0) > 0 or (location and location.biome == BiomeType.RIVER):
        return {"action": ActionType.DRINK, "parameters": "", "reasoning": "Drinking water"}
```

- [ ] **Step 4: 测试进食/喝水**

观察智能体事件日志：

```bash
curl -s 'http://localhost:8888/events?limit=20' | jq '.recent_actions[]' | grep -i "EAT\|DRINK\|进食\|喝水"
```

Expected: 看到进食/喝水事件

- [ ] **Step 5: 提交**

```bash
git add backend/agent.py backend/orchestrator.py
git commit -m "feat: 实现进食和喝水动作

- 添加EAT和DRINK动作类型
- 实现进食/喝水执行逻辑
- 决策系统主动进食/喝水
- 智能体可从库存或河流喝水"
```

---

## 阶段2：对话生成系统

### Task 5: 创建对话生成器

**Files:**
- Create: `backend/dialogue_generator.py`

- [ ] **Step 1: 创建对话生成器类**

```python
"""
对话生成器 - 使用Claude API生成自然对话
"""

from typing import Dict, Optional
import os
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
from dotenv import load_dotenv

from agent import Agent, PersonalityTrait


class DialogueGenerator:
    """使用Claude API生成智能体对话"""

    def __init__(self):
        load_dotenv()

        if Anthropic and os.getenv("ANTHROPIC_API_KEY"):
            client_kwargs = {"api_key": os.getenv("ANTHROPIC_API_KEY")}
            base_url = os.getenv("ANTHROPIC_BASE_URL")
            if base_url:
                client_kwargs["base_url"] = base_url
            self.client = Anthropic(**client_kwargs)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        else:
            self.client = None

    def generate_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        context: str,
        dialogue_type: str = "greeting"
    ) -> str:
        """生成对话内容"""

        if not self.client:
            # Fallback: 模板对话
            return self._fallback_dialogue(speaker, listener, dialogue_type)

        prompt = self._build_dialogue_prompt(speaker, listener, context, dialogue_type)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"⚠️ 对话生成失败: {e}")
            return self._fallback_dialogue(speaker, listener, dialogue_type)

    def _build_dialogue_prompt(
        self,
        speaker: Agent,
        listener: Agent,
        context: str,
        dialogue_type: str
    ) -> str:
        """构建Claude API提示词"""

        personality_desc = ", ".join([
            f"{t.value}: {v:.2f}"
            for t, v in speaker.personality.items()
        ])

        relationship = speaker.relationships.get(listener.id, None)
        trust = relationship.trust if relationship else 0.0
        friendship = relationship.friendship if relationship else 0.0

        stage = self._get_relationship_stage(trust, friendship)

        return f"""你是{speaker.name}，正在与{listener.name}对话。

你的性格（0-1）：
{personality_desc}

你们的关系：
- 信任度: {trust:.2f}
- 友谊值: {friendship:.2f}
- 关系阶段: {stage}

当前情境：
{context}

对话类型：{dialogue_type}

你的状态：
- 饥饿: {speaker.hunger:.0f}/100
- 口渴: {speaker.thirst:.0f}/100
- 能量: {speaker.energy:.0f}/100

生成一句自然的对话（10-30字），反映你的性格和状态。只输出对话内容，不要其他说明。
"""

    def _get_relationship_stage(self, trust: float, friendship: float) -> str:
        """获取关系阶段"""
        if friendship >= 0.8 and trust >= 0.7:
            return "恋爱"
        elif friendship >= 0.7 and trust >= 0.5:
            return "好友"
        elif friendship >= 0.5:
            return "朋友"
        elif friendship >= 0.2:
            return "熟人"
        else:
            return "陌生人"

    def _fallback_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        dialogue_type: str
    ) -> str:
        """Fallback模板对话"""

        templates = {
            "greeting": f"你好{listener.name}，我是{speaker.name}。",
            "trade": f"{listener.name}，我有些资源想要交易。",
            "friendly": f"嗨{listener.name}，最近怎么样？",
            "romantic": f"{listener.name}，能和你在一起真开心。",
        }
        return templates.get(dialogue_type, f"你好{listener.name}。")
```

- [ ] **Step 2: 创建测试**

创建`backend/test_dialogue.py`:

```python
"""测试对话生成"""

from dialogue_generator import DialogueGenerator
from agent import Agent, PersonalityTrait

def test_fallback_dialogue():
    """测试Fallback对话"""
    gen = DialogueGenerator()

    speaker = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    listener = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    dialogue = gen.generate_dialogue(
        speaker,
        listener,
        "初次见面",
        "greeting"
    )

    print(f"生成的对话: {dialogue}")
    assert len(dialogue) > 0
    assert "Bob" in dialogue

    print("✓ 对话生成测试通过")

if __name__ == "__main__":
    test_fallback_dialogue()
    print("\n✅ 对话生成器测试通过")
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && python3 test_dialogue.py
```

Expected: 输出对话内容和 "✅ 对话生成器测试通过"

- [ ] **Step 4: 提交**

```bash
git add backend/dialogue_generator.py backend/test_dialogue.py
git commit -m "feat: 实现对话生成器

- Claude API生成自然对话
- 性格/关系/情境整合
- Fallback模板对话
- 完整测试覆盖"
```

---

### Task 6: 激活COMMUNICATE动作

**Files:**
- Modify: `backend/orchestrator.py:335-361`

- [ ] **Step 1: 集成对话生成器**

在`orchestrator.py`导入：

```python
from dialogue_generator import DialogueGenerator
```

在`__init__`中初始化：

```python
def __init__(self, world: WorldState, agent_count: int = 5):
    # ... 现有代码 ...

    # === 新增：初始化对话生成器 ===
    self.dialogue_generator = DialogueGenerator()
```

- [ ] **Step 2: 更新_communicate执行方法**

修改`_execute_communicate`方法：

```python
async def _execute_communicate(self, agent: Agent, target_id: str) -> str:
    if target_id not in self.agents:
        return f"Agent {target_id} not found"

    target = self.agents[target_id]
    location = self.world.get_location(agent.position)

    if target_id not in (location.agents_present if location else []):
        return f"{target.name} is not nearby"

    # 初始化关系
    if target_id not in agent.relationships:
        agent.relationships[target_id] = {
            "agent_id": target_id,
            "trust": 0.0,
            "friendship": 0.0,
            "interactions": 0
        }

    # 增加互动次数
    agent.relationships[target_id]["interactions"] += 1

    # === 新增：生成对话 ===
    dialogue_type = self._determine_dialogue_type(agent, target)
    context = f"在{location.biome.value if location else '未知'}相遇"

    dialogue = self.dialogue_generator.generate_dialogue(
        agent,
        target,
        context,
        dialogue_type
    )

    print(f"💬 {agent.name}: {dialogue}")

    # === 更新关系 ===
    if agent.personality[PersonalityTrait.AGREEABLENESS] > 0.5:
        agent.relationships[target_id]["friendship"] = min(
            1.0,
            agent.relationships[target_id]["friendship"] + 0.1
        )

    return f"Communicated with {target.name}: {dialogue}"

def _determine_dialogue_type(self, agent: Agent, target: Agent) -> str:
    """确定对话类型"""

    if target.id not in agent.relationships:
        return "greeting"

    relationship = agent.relationships[target.id]

    if relationship["friendship"] >= 0.8 and relationship["trust"] >= 0.7:
        return "romantic"
    elif relationship["friendship"] >= 0.5:
        return "friendly"
    else:
        return "greeting"
```

- [ ] **Step 3: 降低COMMUNICATE触发条件**

修改`_simulate_decision`中的社交部分：

```python
# Social interaction for extraverted agents
location = self.world.get_location(agent.position)
if location and len(location.agents_present) > 1:
    others = [a for a in location.agents_present if a != agent.id]
    extraversion = agent.personality[PersonalityTrait.EXTRAVERSION]

    # === 降低触发条件 ===
    if others and extraversion > 0.3:  # 从0.6降到0.3
        target = random.choice(others)
        return {"action": ActionType.COMMUNICATE, "parameters": target, "reasoning": f"Social interaction (extraversion: {extraversion:.2f})"}
```

- [ ] **Step 4: 测试交流**

观察事件日志：

```bash
curl -s 'http://localhost:8888/events?limit=50' | jq '.recent_actions[]' | grep -i "COMMUNICATE\|交流"
```

Expected: 看到更多交流事件

- [ ] **Step 5: 提交**

```bash
git add backend/orchestrator.py
git commit -m "feat: 激活COMMUNICATE动作并集成对话生成

- 集成DialogueGenerator
- 生成自然语言对话
- 更新关系值
- 降低交流触发条件（外向性>0.3）"
```

---

## 阶段3：建筑系统

### Task 7: 扩展Location类添加建筑数据

**Files:**
- Modify: `backend/world_state.py:33-39`

- [ ] **Step 1: 添加建筑数据结构**

在`world_state.py`添加：

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum


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
    buildings: List[str] = field(default_factory=list)  # 建筑ID列表
```

- [ ] **Step 2: 提交**

```bash
git add backend/world_state.py
git commit -m "feat: 扩展Location类添加建筑数据结构

- 添加BuildingType枚举
- 添加Building数据类
- Location添加建筑ID列表"
```

---

### Task 8: 创建建筑系统模块

**Files:**
- Create: `backend/building_system.py`

- [ ] **Step 1: 创建建筑系统类**

```python
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

        # 消耗资源
        for resource, amount in cost.items():
            agent.inventory[resource] -= amount

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
```

- [ ] **Step 2: 创建测试**

创建`backend/test_building.py`:

```python
"""测试建筑系统"""

from building_system import BuildingSystem, BuildingType
from agent import Agent, PersonalityTrait
from world_state import WorldState

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
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && python3 test_building.py
```

Expected: "✅ 所有建筑系统测试通过"

- [ ] **Step 4: 提交**

```bash
git add backend/building_system.py backend/test_building.py
git commit -m "feat: 实现建筑系统核心功能

- 建筑类型和等级配置
- 建造条件检查
- 资源消耗
- 建筑效果
- 附近建筑查找
- 完整测试覆盖"
```

---

### Task 9: 实现BUILD动作

**Files:**
- Modify: `backend/orchestrator.py`

- [ ] **Step 1: 导入建筑系统**

在`orchestrator.py`添加：

```python
from building_system import BuildingSystem, BuildingType
```

在`__init__`中初始化：

```python
# Initialize building system
self.building_system = BuildingSystem(world)
```

- [ ] **Step 2: 添加BUILD执行方法**

在`_execute_action`中添加：

```python
async def _execute_action(self, agent: Agent, action: ActionType, params: str) -> str:
    """Execute specific action and return result"""

    if action == ActionType.MOVE:
        return self._execute_move(agent, params)
    elif action == ActionType.GATHER:
        return self._execute_gather(agent, params)
    elif action == ActionType.REST:
        return self._execute_rest(agent)
    elif action == ActionType.COMMUNICATE:
        return await self._execute_communicate(agent, params)
    elif action == ActionType.EAT:
        return self._execute_eat(agent)
    elif action == ActionType.DRINK:
        return self._execute_drink(agent)
    # === 新增 ===
    elif action == ActionType.BUILD:
        return self._execute_build(agent, params)
    else:
        return "Action not implemented"

def _execute_build(self, agent: Agent, params: str) -> str:
    """执行建造"""

    # 解析参数: "house:1" 或 "well:2"
    try:
        parts = params.split(":")
        building_type_str = parts[0].lower()
        level = int(parts[1]) if len(parts) > 1 else 1

        building_type = BuildingType(building_type_str)
    except (ValueError, IndexError):
        return f"Invalid building parameters: {params}"

    building = self.building_system.build(
        agent,
        building_type,
        level,
        self.world.tick
    )

    if building:
        effect = self.building_system.get_building_effect(building)
        log = f"建造了{building.name}（{effect}）"
        print(f"🏠 {agent.name} {log}")
        return log
    else:
        return "建造失败"
```

- [ ] **Step 3: 更新决策逻辑添加建造需求**

在`_simulate_decision`中添加：

```python
# === 新增：建筑需求 ===
if agent.spouse_id and not agent.home_location:
    # 结婚但无房，优先建造
    if agent.inventory.get("wood", 0) >= 10 and agent.inventory.get("stone", 0) >= 5:
        return {"action": ActionType.BUILD, "parameters": "house:1", "reasoning": "Building house for family"}

# 高尽责性智能体倾向于建造
conscientiousness = agent.personality[PersonalityTrait.CONSCIENTIOUSNESS]
if conscientiousness > 0.7:
    # 检查是否需要水井
    wells = self.building_system.get_nearby_buildings(agent.position, BuildingType.WELL)
    if not wells and agent.inventory.get("stone", 0) >= 10:
        return {"action": ActionType.BUILD, "parameters": "well:1", "reasoning": "Building well for water"}
```

- [ ] **Step 4: 测试建造**

观察事件日志：

```bash
curl -s 'http://localhost:8888/events?limit=50' | jq '.recent_actions[]' | grep -i "BUILD\|建造\|房屋"
```

Expected: 看到建造事件

- [ ] **Step 5: 提交**

```bash
git add backend/orchestrator.py
git commit -m "feat: 实现BUILD动作

- 集成BuildingSystem
- 实现建造执行逻辑
- 决策系统添加建造需求
- 智能体可根据情况建造房屋和水井"
```

---

## 阶段4：感情婚姻系统

### Task 10: 创建繁衍系统模块

**Files:**
- Create: `backend/reproduction_system.py`

- [ ] **Step 1: 创建繁衍系统类**

```python
"""
繁衍系统 - 管理关系发展、婚姻、怀孕和生育
"""

from typing import Dict, List, Optional, Tuple
import random

from agent import Agent, PersonalityTrait, ActionType
from world_state import WorldState


class ReproductionSystem:
    """管理智能体繁衍"""

    def __init__(self, world: WorldState):
        self.world = world

    def update_relationship(
        self,
        agent: Agent,
        target_id: str,
        interaction_type: str = "friendly"
    ) -> str:
        """更新关系"""

        if target_id not in agent.relationships:
            agent.relationships[target_id] = {
                "agent_id": target_id,
                "trust": 0.0,
                "friendship": 0.0,
                "interactions": 0
            }

        relationship = agent.relationships[target_id]

        # 增加互动次数
        relationship["interactions"] += 1

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

        relationship["trust"] = max(-1, min(1, relationship["trust"] + trust_gain))
        relationship["friendship"] = max(0, min(1, relationship["friendship"] + friendship_gain))

        # 返回关系阶段
        return self.get_relationship_stage(agent, target_id)

    def get_relationship_stage(self, agent: Agent, target_id: str) -> str:
        """获取关系阶段"""

        if target_id not in agent.relationships:
            return "陌生人"

        rel = agent.relationships[target_id]
        trust = rel["trust"]
        friendship = rel["friendship"]
        interactions = rel["interactions"]

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
        if rel["friendship"] < 0.8 or rel["trust"] < 0.7:
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

        # 5%概率怀孕
        if random.random() > 0.05:
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

        # 怀孕持续20个tick
        if current_tick - agent.pregnancy_start_tick >= 20:
            return True  # 可以生了

        return False

    def create_child(
        self,
        parent1: Agent,
        parent2: Agent,
        current_tick: int
    ) -> Optional[Agent]:
        """生成孩子"""

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

        # 在家附近出生
        position = parent1.home_location

        # 创建孩子Agent
        child_id = f"agent_child_{current_tick}"

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

        # 重置怀孕状态
        parent1.pregnancy_start_tick = None

        print(f"👶 {parent1.name} 和 {parent2.name} 生下了 {name}！")
        return child
```

- [ ] **Step 2: 创建测试**

创建`backend/test_reproduction.py`:

```python
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
    assert agent1.relationships[agent2.id]["friendship"] > 0

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
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && python3 test_reproduction.py
```

Expected: "✅ 所有繁衍系统测试通过"

- [ ] **Step 4: 提交**

```bash
git add backend/reproduction_system.py backend/test_reproduction.py
git commit -m "feat: 实现繁衍系统核心功能

- 关系发展阶段（陌生人→配偶）
- 婚姻系统
- 怀孕机制
- 孩子生成（遗传父母特质）
- 完整测试覆盖"
```

---

### Task 11: 集成繁衍系统

**Files:**
- Modify: `backend/orchestrator.py`

- [ ] **Step 1: 导入繁衍系统**

```python
from reproduction_system import ReproductionSystem
```

在`__init__`中初始化：

```python
# Initialize reproduction system
self.reproduction_system = ReproductionSystem(world)
```

- [ ] **Step 2: 在交流中更新关系**

修改`_execute_communicate`:

```python
async def _execute_communicate(self, agent: Agent, target_id: str) -> str:
    if target_id not in self.agents:
        return f"Agent {target_id} not found"

    target = self.agents[target_id]
    location = self.world.get_location(agent.position)

    if target_id not in (location.agents_present if location else []):
        return f"{target.name} is not nearby"

    # 生成对话
    dialogue_type = self._determine_dialogue_type(agent, target)
    context = f"在{location.biome.value if location else '未知'}相遇"

    dialogue = self.dialogue_generator.generate_dialogue(
        agent,
        target,
        context,
        dialogue_type
    )

    print(f"💬 {agent.name}: {dialogue}")

    # === 更新关系 ===
    stage = self.reproduction_system.update_relationship(agent, target_id, "friendly")
    self.reproduction_system.update_relationship(target, agent.id, "friendly")

    # === 检查是否可以求婚 ===
    if agent.relationship_status == "single" and target.relationship_status == "single":
        if stage == "恋爱":
            # 20%概率求婚
            if random.random() < 0.2:
                success = self.reproduction_system.marry(agent, target)
                if success:
                    dialogue += f" 我们结婚吧！"

    return f"Communicated with {target.name}: {dialogue}"
```

- [ ] **Step 3: 在主循环中检查怀孕和生产**

在`run_simulation`函数中添加：

```python
# 让每个智能体行动
if orchestrator:
    for agent in orchestrator.agents.values():
        # === 新增：检查怀孕和生产 ===
        if agent.pregnancy_start_tick and orchestrator.reproduction_system.check_pregnancy_progress(agent, tick_count):
            # 找到配偶
            if agent.spouse_id and agent.spouse_id in orchestrator.agents:
                spouse = orchestrator.agents[agent.spouse_id]
                child = orchestrator.reproduction_system.create_child(agent, spouse, tick_count)
                if child:
                    orchestrator.agents[child.id] = child
                    location = world.get_location(child.position)
                    if location:
                        location.agents_present.append(child.id)

        # 决策
        decision = orchestrator._simulate_decision(agent)

        # 执行
        await orchestrator.execute_action_and_learn(agent, decision)

        # === 新增：尝试怀孕 ===
        if agent.relationship_status == "married" and agent.pregnancy_start_tick is None:
            if random.random() < 0.05:  # 每tick 5%概率尝试
                orchestrator.reproduction_system.start_pregnancy(agent, tick_count)
```

- [ ] **Step 4: 测试婚姻和生育**

观察事件日志：

```bash
curl -s 'http://localhost:8888/events?limit=100' | jq '.recent_actions[]' | grep -i "结婚\|怀孕\|生下"
```

Expected: 看到结婚、怀孕、生育事件

- [ ] **Step 5: 提交**

```bash
git add backend/orchestrator.py
git commit -m "feat: 集成繁衍系统

- 交流时更新关系
- 自动求婚和结婚
- 怀孕和生产机制
- 孩子自动加入世界"
```

---

## 阶段5：复活机制

### Task 12: 实现复活逻辑

**Files:**
- Modify: `backend/working_server.py`

- [ ] **Step 1: 在working_server中添加复活检查**

在`run_simulation`函数中添加：

```python
# 让每个智能体行动
if orchestrator:
    for agent in orchestrator.agents.values():
        # === 新增：死亡检查 ===
        if not agent.is_alive:
            # 检查是否可以复活
            if agent.revival_count < 1:
                # 获取所有建筑
                buildings = list(orchestrator.building_system.buildings.values())
                success = orchestrator.survival_system.revive(agent, buildings)
                if success:
                    print(f"⚡ {agent.name} 复活了！")
            continue  # 跳过已死亡智能体的行动

        # 决策
        decision = orchestrator._simulate_decision(agent)

        # 执行
        await orchestrator.execute_action_and_learn(agent, decision)
```

- [ ] **Step 2: 添加生存状态API端点**

在`working_server.py`中添加新端点：

```python
@app.get("/agents/{agent_id}/survival")
async def get_agent_survival(agent_id: str):
    """获取智能体生存状态"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"detail": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return {
        "hunger": agent.hunger,
        "thirst": agent.thirst,
        "health": agent.health,
        "energy": agent.energy,
        "is_alive": agent.is_alive,
        "revival_count": agent.revival_count
    }
```

- [ ] **Step 3: 测试复活**

让智能体死亡后观察复活：

```bash
# 等待智能体死亡
curl -s http://localhost:8888/agents | jq '.[] | select(.is_alive == false) | {name, revival_count}'

# 观察复活事件
curl -s 'http://localhost:8888/events?limit=50' | jq '.recent_actions[]' | grep "复活"
```

Expected: 看到复活事件

- [ ] **Step 4: 提交**

```bash
git add backend/working_server.py
git commit -m "feat: 实现复活机制

- 死亡后自动复活（限制1次）
- 在建筑附近复活
- 添加生存状态API端点"
```

---

## 阶段6：前端集成

### Task 13: 扩展前端类型定义

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: 添加生存和婚姻字段**

```typescript
export interface Agent {
  id: string;
  name: string;
  position: [number, number];
  health: number;
  energy: number;
  inventory: Record<string, number>;
  current_action: string | null;
  skills?: Record<string, number>;
  personality?: Record<string, number>;
  goals?: Array<{
    description: string;
    priority: number;
    completed: boolean;
  }>;

  // === 新增：生存系统 ===
  hunger: number;
  thirst: number;
  is_alive: boolean;
  revival_count: number;

  // === 新增：感情婚姻系统 ===
  spouse_id?: string;
  relationship_status: string;
  children: string[];
  home_location?: [number, number];
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: 扩展Agent类型定义添加生存和婚姻字段"
```

---

### Task 14: 创建生存状态显示组件

**Files:**
- Create: `frontend/src/components/SurvivalBars.tsx`

- [ ] **Step 1: 创建SurvivalBars组件**

```tsx
import React from 'react';

interface SurvivalBarsProps {
  hunger: number;
  thirst: number;
  health: number;
  energy: number;
}

export const SurvivalBars: React.FC<SurvivalBarsProps> = ({
  hunger,
  thirst,
  health,
  energy
}) => {
  const getBarColor = (value: number) => {
    if (value < 30) return '#ff4444';
    if (value < 50) return '#ffaa00';
    return '#44ff44';
  };

  return (
    <div className="survival-bars">
      <div className="survival-bar">
        <label>🍖 饥饿</label>
        <div className="bar-container">
          <div
            className="bar-fill"
            style={{
              width: `${hunger}%`,
              backgroundColor: getBarColor(hunger)
            }}
          />
        </div>
        <span>{hunger.toFixed(0)}%</span>
      </div>

      <div className="survival-bar">
        <label>💧 口渴</label>
        <div className="bar-container">
          <div
            className="bar-fill"
            style={{
              width: `${thirst}%`,
              backgroundColor: getBarColor(thirst)
            }}
          />
        </div>
        <span>{thirst.toFixed(0)}%</span>
      </div>

      <div className="survival-bar">
        <label>❤️ 健康</label>
        <div className="bar-container">
          <div
            className="bar-fill"
            style={{
              width: `${health}%`,
              backgroundColor: getBarColor(health)
            }}
          />
        </div>
        <span>{health.toFixed(0)}%</span>
      </div>

      <div className="survival-bar">
        <label>⚡ 能量</label>
        <div className="bar-container">
          <div
            className="bar-fill"
            style={{
              width: `${energy}%`,
              backgroundColor: getBarColor(energy)
            }}
          />
        </div>
        <span>{energy.toFixed(0)}%</span>
      </div>
    </div>
  );
};
```

- [ ] **Step 2: 添加CSS样式**

在`AgentCard.css`中添加：

```css
.survival-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.survival-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.survival-bar label {
  font-size: 11px;
  min-width: 50px;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}
```

- [ ] **Step 3: 集成到AgentCard**

修改`AgentCard.tsx`：

```tsx
import { SurvivalBars } from './SurvivalBars';

export const AgentCard: React.FC<AgentCardProps> = ({ agent, isSelected, onClick }) => {
  // ... 现有代码 ...

  return (
    <div className={`agent-card ${isSelected ? 'selected' : ''}`} ...>
      {/* 现有内容 */}

      {/* === 新增：生存状态条 === */}
      <SurvivalBars
        hunger={agent.hunger}
        thirst={agent.thirst}
        health={agent.health}
        energy={agent.energy}
      />

      {/* 显示配偶和孩子 */}
      {agent.spouse_id && (
        <div className="family-info">
          💍 已婚
        </div>
      )}
      {agent.children.length > 0 && (
        <div className="family-info">
          👶 {agent.children.length}个孩子
        </div>
      )}
    </div>
  );
};
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/SurvivalBars.tsx frontend/src/components/AgentCard.tsx frontend/src/components/AgentCard.css
git commit -m "feat: 添加生存状态显示组件

- 饥饿/口渴/健康/能量进度条
- 颜色警告（红/黄/绿）
- 显示配偶和孩子信息"
```

---

### Task 15: 扩展事件翻译

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 添加新事件翻译**

在`App.tsx`的事件翻译部分添加：

```tsx
const translatedEvents = (data.recent_actions || []).map((event: string) => {
  return event
    .replace(/Tick (\d+):/, '时间片 $1:')
    .replace(/GATHER/g, '采集')
    .replace(/REST/g, '休息')
    .replace(/MOVE/g, '移动')
    .replace(/CRAFT/g, '制作')
    .replace(/BUILD/g, '建造')
    .replace(/COMMUNICATE/g, '交流')
    .replace(/EAT/g, '进食')
    .replace(/DRINK/g, '喝水')
    .replace(/TEACH/g, '教学')
    .replace(/TRADE/g, '交易')
    .replace(/Need food/g, '需要食物')
    .replace(/Need water/g, '需要水')
    .replace(/Need wood/g, '需要木材')
    .replace(/Low energy, need to rest/g, '能量低，需要休息')
    .replace(/\(current: (\d+)\)/g, '(当前: $1)')
    // === 新增翻译 ===
    .replace(/结婚了/g, '举办了婚礼 💒')
    .replace(/怀孕了/g, '怀孕了 🤰')
    .replace(/生下了/g, '生下了 👶')
    .replace(/建造了茅屋/g, '建造了茅屋 🏠')
    .replace(/建造了木屋/g, '建造了木屋 🏠')
    .replace(/建造了水井/g, '建造了水井 ⛲')
    .replace(/复活/g, '复活 ⚡')
    .replace(/死亡/g, '去世 💀');
});
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/App.tsx
git commit -m "feat: 添加新事件类型中文翻译

- 建筑、婚姻、生育事件翻译
- 死亡和复活事件翻译
- 添加emoji图标"
```

---

## 最终整合和测试

### Task 16: 完整系统测试

- [ ] **Step 1: 重启所有服务**

```bash
# 停止现有服务
pkill -f working_server.py

# 重启后端
cd backend && python3 working_server.py &

# 重启前端
cd frontend && npm run dev &
```

- [ ] **Step 2: 观察完整文明演化**

访问 `http://localhost:9000`，观察：

1. ✅ 智能体饥饿/口渴值在减少
2. ✅ 智能体主动进食/喝水
3. ✅ 智能体之间交流对话
4. ✅ 智能体建造房屋和水井
5. ✅ 智能体发展关系、结婚
6. ✅ 智能体怀孕、生育
7. ✅ 死亡和复活事件

- [ ] **Step 3: API测试**

```bash
# 测试生存状态
curl -s http://localhost:8888/agents/agent_0/survival | jq

# 测试建筑
curl -s http://localhost:8888/world/map | jq '.locations | to_entries | .[0] | .value.buildings'

# 测试关系
curl -s http://localhost:8888/agents | jq '.[0].relationships'
```

- [ ] **Step 4: 最终提交**

```bash
git add .
git commit -m "feat: 完成AI文明增强功能实现

✅ 生存系统：饥饿/口渴/死亡/复活
✅ 对话系统：自然语言对话生成
✅ 建筑系统：房屋/水井/仓库建造
✅ 繁衍系统：关系/婚姻/怀孕/生育
✅ 前端集成：生存状态显示、事件翻译

智能体现在可以：
- 感受饥饿和口渴，主动寻找食物和水源
- 与其他智能体自然对话，建立关系
- 建造房屋、水井，形成定居点
- 发展感情，结婚生子
- 死亡后可复活一次

文明演化更加真实和复杂！"
```

---

## 计划总结

**总任务数**: 16个主任务，约70个子步骤
**预计时间**: 10-12小时
**技术栈**: Python 3.9, FastAPI, Claude API, React 18, TypeScript

**实施顺序**:
1. 阶段1：生存系统（Task 1-4）
2. 阶段2：对话系统（Task 5-6）
3. 阶段3：建筑系统（Task 7-9）
4. 阶段4：繁衍系统（Task 10-11）
5. 阶段5：复活机制（Task 12）
6. 阶段6：前端集成（Task 13-15）
7. 最终测试（Task 16）

**关键决策**:
- 模块化设计，每个系统独立文件
- TDD方法，先写测试再实现
- 渐进式集成，每阶段可独立测试
- 频繁提交，每完成一个小功能就提交

**风险评估**:
- Claude API调用可能增加成本 → 已实现fallback机制
- 系统复杂度增加可能影响性能 → 优化决策逻辑频率
- 前端显示大量数据可能卡顿 → 分批加载和缓存

准备好开始实施了吗？