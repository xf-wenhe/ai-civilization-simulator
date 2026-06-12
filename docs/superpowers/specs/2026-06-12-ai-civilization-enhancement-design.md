# AI Civilization Simulator - 功能增强设计文档

**日期**: 2026-06-12
**目标**: 激活交流、建造系统；添加生存、感情、繁衍机制

---

## 一、整体架构

### 新增模块结构

```
backend/
├── survival_system.py         # 【新增】生存管理
│   ├── 饥饿值、口渴值衰减
│   ├── 进食、喝水恢复
│   ├── 健康值计算
│   ├── 死亡判定和复活
│
├── building_system.py         # 【新增】建筑管理
│   ├── 建筑类型定义（房屋/水井/仓库）
│   ├── 建筑等级系统（茅屋→豪宅）
│   ├── 建造资源消耗
│   ├── 建筑效果（提供功能）
│
├── reproduction_system.py     # 【新增】繁衍管理
│   ├── 关系发展阶段
│   ├── 婚姻系统
│   ├── 怀孕机制
│   ├── 孩子生成和成长
│
├── dialogue_generator.py      # 【新增】对话生成
│   ├── Claude API对话生成
│   ├── 对话上下文管理
│   ├── 性格/关系/情境整合
│
└── [现有模块修改]
    ├── agent.py               # 扩展Agent类字段
    ├── world_state.py         # 扩展Location类（建筑数据）
    ├── orchestrator.py        # 修改决策逻辑
    └── working_server.py      # 集成新系统
```

### Agent类扩展字段

```python
@dataclass
class Agent:
    # 生存系统
    hunger: float = 100.0           # 饥饿值 0-100
    thirst: float = 100.0           # 口渴值 0-100
    is_alive: bool = True           # 生命状态
    death_tick: Optional[int] = None  # 死亡时间
    revival_count: int = 0          # 已复活次数（限制1次）

    # 感情婚姻系统
    spouse_id: Optional[str] = None  # 配偶ID
    relationship_status: str = "single"  # single/dating/married
    children: List[str] = field(default_factory=list)  # 孩子ID列表
    pregnancy_start_tick: Optional[int] = None  # 怀孕开始时间

    # 家庭系统
    home_location: Optional[Tuple[int, int]] = None  # 家的位置
```

---

## 二、生存系统设计

### 饥饿/口渴机制

**每tick衰减**：
- 饥饿值：-1.5（基础）
- 口渴值：-2.0（水更重要）
- 高活动（采集/移动/建造）额外-0.5

**进食/喝水恢复**：
- 进食：hunger +30，消耗1份食物
- 喝水：thirst +40，消耗1份水
- 河流位置：可直接喝水（thirst +50，免费）

**健康值影响**：
```python
if hunger < 20 or thirst < 20:
    health -= 5  # 开始受伤

if hunger == 0 or thirst == 0:
    health -= 15  # 快速死亡风险
```

### 死亡判定与复活

**死亡条件**：
- health <= 0 且 is_alive = True
- 标记死亡，记录原因和时间

**复活机制**（限制1次）：
- 找到最近的建筑（房屋优先，其次水井）
- 如果有建筑：在该位置复活
- 如果无建筑：在世界中心复活
- 恢复值：health=50, energy=50, hunger=70, thirst=70
- 清空部分物品（保留20%资源）
- revival_count += 1

### API端点扩展

```python
GET /agents/{id}/survival  # 返回饥饿/口渴/健康详细数据
POST /agents/{id}/eat      # 手动进食
POST /agents/{id}/drink    # 手动喝水
```

---

## 三、建筑系统设计

### 建筑类型与等级

**房屋（House）** - 用于生育和庇护

| 等级 | 名称 | 需求资源 | 效果 |
|------|------|---------|------|
| 1 | 茅屋 | 木材x10, 石头x5 | 可生育，提供庇护 |
| 2 | 木屋 | 木材x20, 石头x10 | 可生育，恢复速度+20% |
| 3 | 石屋 | 木材x15, 石头x25 | 可生育，恢复速度+40% |
| 4 | 豪宅 | 木材x30, 石头x40, 知识x10 | 可生育，恢复速度+80%，提升孩子属性 |

**水井（Well）** - 提供稳定水源

| 等级 | 名称 | 需求资源 | 效果 |
|------|------|---------|------|
| 1 | 简易井 | 石头x10, 木材x5 | 周围3格内可喝水 |
| 2 | 深井 | 石头x20, 木材x10 | 周围5格内，清洁水源 |
| 3 | 石井 | 石头x35 | 周围7格，永久水源 |

**仓库（Warehouse）** - 存储资源

| 等级 | 名称 | 需求资源 | 效果 |
|------|------|---------|------|
| 1 | 木箱 | 木材x15 | 存储100单位资源 |
| 2 | 仓库 | 木材x30, 石头x15 | 存储300单位，防丢失 |
| 3 | 大仓库 | 木材x50, 石头x30 | 存储1000单位，共享存储 |

### 建造机制

**建造条件**：
- 在目标位置
- 有足够资源
- 有建造技能（影响速度和质量）

**建造过程**：
```
Action: BUILD
Parameters: "house:1"  # 类型:等级

步骤：
1. 检查资源和技能
2. 消耗资源（从inventory）
3. 创建建筑（Location.buildings.append）
4. 记录建造者（owner_id）
5. 提升建造技能
6. 设置home_location（如果是房屋）
```

**建筑归属**：
- 建造者拥有建筑
- 可共享给家人（配偶、孩子）
- 死亡后建筑归属配偶或孩子

---

## 四、感情婚姻系统设计

### 关系发展阶段

| 阶段 | 条件 | 效果 |
|------|------|------|
| 陌生人 | 初次见面 | trust=0, friendship=0 |
| 熟人 | 互动≥3次 | trust=0.3, friendship=0.2 |
| 朋友 | friendship≥0.5, 互动≥10次 | 可合作、分享资源 |
| 好友 | friendship≥0.7, trust≥0.5 | 互相帮助优先 |
| 恋爱 | friendship≥0.8, trust≥0.7, 双方有意向 | 特殊互动，准备婚姻 |
| 婚姻 | 恋爱持续20+ ticks, 有房屋, 双方同意 | 可生育，共享资源 |

### 关系数值变化

**交流效果**：
- 友好交流：trust +0.05, friendship +0.1
- 争吵：trust -0.1, friendship -0.15
- 合作成功：trust +0.15, friendship +0.1

**性格影响**：
```python
# 高亲和性 -> 更容易建立关系
if agreeableness > 0.7:
    friendship_gain *= 1.3

# 高神经质 -> 关系不稳定
if neuroticism > 0.7:
    friendship_loss *= 1.2

# 高外向性 -> 更频繁交流
if extraversion > 0.7:
    communication_frequency += 1
```

### 婚姻机制

**求婚条件**：
- 恋爱状态持续≥20 ticks
- 双方都有房屋（或一方有高级房屋）
- 双方同意（性格影响同意概率）

**婚姻效果**：
- 配偶共享房屋和仓库
- 死亡时配偶健康-10（悲伤）
- 可以生育孩子
- 事件日志记录："Alice 和 Bob 举办了婚礼！💒"

---

## 五、繁衍系统设计

### 怀孕机制

**怀孕条件**：
```python
def can_conceive(agent):
    return (
        agent.relationship_status == "married" and
        agent.pregnancy_start_tick is None and
        agent.home_location is not None and  # 有房子
        agent.inventory.get("food", 0) >= 20 and  # 足够食物
        agent.inventory.get("water", 0) >= 10 and  # 足够水
        random.random() < 0.05  # 每tick 5%概率
    )
```

**怀孕周期**：
- 持续20个tick
- 消耗增加：食物x1.5, 水1.5
- 行动受限：不能高强度活动
- 需要配偶照顾（提供食物/水）

**孩子生成**：
```python
def create_child(parent1, parent2, world):
    # 性格遗传（50%父母平均 + 50%随机）
    personality = {
        trait: (p1.personality[trait] + p2.personality[trait]) / 2 * 0.5
               + random.uniform(0.3, 0.7) * 0.5
        for trait in PersonalityTrait
    }

    # 技能遗传（30%父母平均）
    skills = {
        skill: (p1.skills.get(skill, 0.3) + p2.skills.get(skill, 0.3)) / 2 * 0.3
        for skill in ["gathering", "crafting", "communication"]
    }

    # 在家附近出生
    position = parent1.home_location

    # 名字随机生成
    name = random.choice(child_names)

    return Agent(...)
```

### 孩子成长

| 时期 | ticks | 能力 | 特点 |
|------|-------|------|------|
| 新生儿 | 0-5 | 不能移动 | 依赖父母喂食 |
| 幼儿 | 5-20 | 可移动学习 | 开始学习技能 |
| 成年 | 20+ | 完全独立 | 可工作、结婚 |

---

## 六、对话生成系统设计

### Claude API调用

**系统提示词模板**：
```python
def build_dialogue_prompt(speaker, listener, context, dialogue_type):
    return f"""你是{speaker.name}，正在与{listener.name}对话。

你的性格：
- 开放性: {speaker.personality[OPENNESS]:.2f} (好奇心/创造力)
- 尽责性: {speaker.personality[CONSCIENTIOUSNESS]:.2f} (自律/负责)
- 外向性: {speaker.personality[EXTRAVERSION]:.2f} (社交/活跃)
- 亲和性: {speaker.personality[AGREEABLENESS]:.2f} (友好/合作)
- 神经质: {speaker.personality[NEUROTICISM]:.2f} (敏感/情绪化)

你们的关系：
- 信任度: {speaker.relationships[listener.id].trust:.2f}
- 友谊值: {speaker.relationships[listener.id].friendship:.2f}
- 关系阶段: {get_relationship_stage(speaker, listener)}

当前情境：
{context}

对话类型：{dialogue_type}

你的状态：
- 饥饿: {speaker.hunger:.0f}/100
- 口渴: {speaker.thirst:.0f}/100
- 能量: {speaker.energy:.0f}/100

生成一句自然的对话（10-30字），反映性格和状态。只输出对话内容。
"""
```

### 对话类型

| 类型 | 触发条件 | Claude调用 |
|------|---------|-----------|
| 问候 | 初次见面/日常 | 是 |
| 交易 | 资源交换 | 是 |
| 情感 | 友谊发展/恋爱/求婚 | 是 |
| 冲突 | 争吵/竞争 | 是 |
| 教学 | 技能传授 | 是 |

---

## 七、决策系统集成

### 优先级调整

```python
def _simulate_decision(agent):
    # 0. 死亡检查
    if not agent.is_alive:
        return {"action": REST, "reasoning": "Dead"}

    # 1. 生存优先（最高）
    if agent.hunger < 30 or agent.thirst < 30:
        if agent.thirst < agent.hunger:
            # 找水或喝水
            return {"action": DRINK, ...}
        else:
            return {"action": EAT, ...}

    # 2. 能量恢复
    if agent.energy < 30:
        return {"action": REST, ...}

    # 3. 资源收集（生存储备）
    if agent.inventory.get("food", 0) < 5:
        return {"action": GATHER, "parameters": "food"}
    if agent.inventory.get("water", 0) < 3:
        return {"action": GATHER, "parameters": "water"}

    # 4. 建筑需求（有配偶但无房）
    if agent.spouse_id and not agent.home_location:
        if agent.inventory.get("wood", 0) >= 10:
            return {"action": BUILD, "parameters": "house:1"}

    # 5. 社交需求（性格驱动）
    extraversion = agent.personality[EXTRAVERSION]
    if extraversion > 0.6:
        nearby = get_nearby_agents(agent)
        if nearby and agent.relationship_status == "single":
            return {"action": COMMUNICATE, ...}

    # 6. 发展需求（建造升级/制作）
    conscientiousness = agent.personality[CONSCIENTIOUSNESS]
    if conscientiousness > 0.6 and agent.inventory.get("wood", 0) >= 20:
        return {"action": BUILD, "parameters": "house:2"}

    # 7. 默认：探索或采集
    ...
```

---

## 八、前端展示扩展

### 新增显示元素

**AgentCard组件**：
- 饥饿/口渴进度条（颜色警告）
- 配偶和孩子标识
- 房屋位置标记

**AgentDetails组件**：
- 生存状态详细数据
- 关系图谱（友谊/恋爱/婚姻）
- 家族树（父母、配偶、孩子）

**WorldMap组件**：
- 建筑图标和等级
- 建筑归属显示
- 死亡标记（墓碑）

### 新事件类型

```
"Tick 100: Alice 和 Bob 举办了婚礼！💒"
"Tick 120: Alice 生下了小明 👶"
"Tick 150: Bob 建造了一座木屋 🏠"
"Tick 180: Charlie 因饥饿去世 💀"
"Tick 181: Charlie 在房屋附近复活 ⚡"
```

---

## 九、数据持久化

### civilization_state.json扩展

```json
{
  "tick": 1000,
  "agents": [
    {
      "id": "agent_0",
      "name": "Alice",
      "hunger": 75.0,
      "thirst": 60.0,
      "spouse_id": "agent_1",
      "children": ["agent_5"],
      "home_location": [5, 5],
      "is_alive": true,
      "revival_count": 0
    }
  ],
  "buildings": [
    {
      "id": "building_0",
      "type": "house",
      "level": 2,
      "position": [5, 5],
      "owner_id": "agent_0",
      "build_tick": 100
    }
  ]
}
```

---

## 十、实现计划

### 阶段划分

**阶段1：生存系统**（2-3小时）
- 创建 survival_system.py
- 扩展 Agent 类字段
- 修改 orchestrator.py 集成生存逻辑
- 测试饥饿/口渴/死亡/复活

**阶段2：对话激活**（1小时）
- 创建 dialogue_generator.py
- 激活 COMMUNICATE 动作
- 测试对话生成

**阶段3：建筑系统**（2小时）
- 创建 building_system.py
- 实现 BUILD 动作
- 测试建造功能

**阶段4：感情婚姻**（2小时）
- 创建 reproduction_system.py
- 实现关系发展逻辑
- 测试婚姻机制

**阶段5：繁衍系统**（2-3小时）
- 实现怀孕机制
- 实现孩子生成
- 测试生育和成长

**阶段6：前端集成**（1-2小时）
- 扩展 AgentCard、AgentDetails
- 添加建筑显示
- 新事件类型中文翻译

---

## 十一、技术要点

### 性能考虑

- 对话生成缓存：避免重复调用Claude API
- 建筑查找优化：使用位置索引
- 关系计算频率：每5个tick更新一次

### 错误处理

- Claude API调用失败：fallback到模板对话
- 建筑资源不足：提示并等待
- 复活位置无建筑：使用默认位置

### 测试策略

- 单元测试：每个系统独立测试
- 集成测试：多系统协同测试
- 场景测试：完整文明演化测试

---

**设计完成时间**: 2026-06-12 20:30
**预计实现时间**: 10-12小时