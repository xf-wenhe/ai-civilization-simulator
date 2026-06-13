"""
保证能工作的服务器 - 最简单可靠版本
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os

# 强制使用模拟模式
os.environ['USE_SIMULATION'] = 'true'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
world = None
orchestrator = None
tick_count = 0
action_log = []

@app.on_event("startup")
async def startup():
    global world, orchestrator, action_log

    print("\n" + "=" * 70)
    print("🎮 AI Civilization - 确保能看到智能体行动的版本")
    print("=" * 70 + "\n")

    try:
        from world_state import WorldState
        from orchestrator import EnhancedAgentOrchestrator

        # 创建世界
        print("📍 创建世界...")
        world = WorldState(width=10, height=10)
        world.initialize_world()
        print(f"   ✓ 世界大小: {world.width}x{world.height}")

        # 创建智能体
        print("\n📍 创建智能体...")
        orchestrator = EnhancedAgentOrchestrator(world, agent_count=5)
        print(f"   ✓ 智能体数量: {len(orchestrator.agents)}")

        for agent in orchestrator.agents.values():
            print(f"     - {agent.name}")

        # 初始化日志
        action_log.append("🎮 游戏开始！智能体们开始行动...")

        # 启动模拟
        print("\n📍 启动模拟循环...")
        asyncio.create_task(run_simulation())
        print("   ✓ 模拟已启动\n")

        print("=" * 70)
        print("✅ 系统就绪！每3秒智能体会行动一次")
        print("=" * 70)
        print("\n🌐 API端点:")
        print("   http://localhost:8000/")
        print("   http://localhost:8000/agents")
        print("   http://localhost:8000/events")
        print("\n👀 现在观察终端输出，你会看到智能体每3秒的行动！\n")

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    return {
        "status": "running",
        "agents": len(orchestrator.agents) if orchestrator else 0,
        "tick": tick_count,
        "actions": len(action_log)
    }

@app.get("/agents")
async def get_agents():
    if not orchestrator:
        return []

    result = []
    for a in orchestrator.agents.values():
        result.append({
            "id": a.id,
            "name": a.name,
            "position": list(a.position),
            "health": a.health if hasattr(a, 'health') else 100.0,
            "energy": a.energy,
            "hunger": a.hunger if hasattr(a, 'hunger') else 100.0,
            "thirst": a.thirst if hasattr(a, 'thirst') else 100.0,
            "is_alive": a.is_alive if hasattr(a, 'is_alive') else True,
            "inventory": a.inventory,
            "current_action": a.current_action.value if a.current_action else "idle"
        })
    return result

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取单个智能体详情"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"detail": "Agent not found"}

    a = orchestrator.agents[agent_id]
    return {
        "id": a.id,
        "name": a.name,
        "position": list(a.position),
        "health": a.health if hasattr(a, 'health') else 100.0,
        "energy": a.energy,
        "inventory": a.inventory,
        "current_action": a.current_action.value if a.current_action else "idle",
        "skills": a.skills if hasattr(a, 'skills') else {},
        "personality": a.personality if hasattr(a, 'personality') else {}
    }

@app.get("/agents/{agent_id}/memories")
async def get_agent_memories(agent_id: str):
    """获取智能体记忆"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"memories": []}

    # 返回空列表，因为模拟模式没有实际记忆
    return {"memories": []}

@app.get("/agents/{agent_id}/survival")
async def get_agent_survival(agent_id: str):
    """获取智能体生存状态"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"detail": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return {
        "agent_id": agent.id,
        "name": agent.name,
        "hunger": agent.hunger if hasattr(agent, 'hunger') else 100.0,
        "thirst": agent.thirst if hasattr(agent, 'thirst') else 100.0,
        "health": agent.health if hasattr(agent, 'health') else 100.0,
        "energy": agent.energy,
        "is_alive": agent.is_alive if hasattr(agent, 'is_alive') else True,
        "revival_count": agent.revival_count if hasattr(agent, 'revival_count') else 0
    }

@app.get("/events")
async def get_events():
    return {
        "tick": tick_count,
        "total_actions": len(action_log),
        "recent_actions": action_log[-20:]
    }

@app.get("/world")
async def get_world():
    return {
        "tick": tick_count,
        "day": world.day if world else 1,
        "time_of_day": world.time_of_day if world else 0.0,
        "weather": world.weather if world else "clear",
        "width": world.width if world else 10,
        "height": world.height if world else 10
    }

@app.get("/world/map")
async def get_world_map():
    """Return world map data"""
    if not world:
        return {"width": 0, "height": 0, "locations": {}}

    locations = {}
    for pos, location in world.locations.items():
        key = f"{pos[0]},{pos[1]}"
        locations[key] = {
            "position": list(pos),
            "biome": location.biome.value if hasattr(location.biome, 'value') else str(location.biome),
            "resources": {k.value if hasattr(k, 'value') else str(k): v for k, v in location.resources.items()},
            "agents_present": location.agents_present,
            "buildings": location.buildings
        }

    return {
        "width": world.width,
        "height": world.height,
        "locations": locations
    }

async def run_simulation():
    """模拟循环 - 让智能体每3秒行动一次"""
    global tick_count, action_log

    print("🚀 模拟循环开始！\n")

    # 尝试加载之前的状态
    try:
        if os.path.exists("data/civilization_state.json"):
            import json
            with open("data/civilization_state.json", "r") as f:
                saved_state = json.load(f)
                tick_count = saved_state.get("tick", 0)
                action_log = saved_state.get("actions", [])
                print(f"✓ 加载存档: Tick {tick_count}, {len(action_log)}个历史事件\n")
    except Exception as e:
        print(f"⚠️  无存档或加载失败: {e}\n")

    save_counter = 0

    while True:
        try:
            # 增加tick
            tick_count += 1

            # 推进世界
            if world:
                world.advance_time()

            # 让每个智能体行动
            if orchestrator:
                # === 新增：死亡检查和复活 ===
                # 先收集所有建筑（避免重复构建）
                buildings = []
                for pos, location in world.locations.items():
                    for building_id in location.buildings:
                        # 从orchestrator的building_system获取建筑信息
                        if hasattr(orchestrator, 'building_system'):
                            building = orchestrator.building_system.get_building(building_id)
                            if building:
                                buildings.append({
                                    "type": building.building_type.value if hasattr(building.building_type, 'value') else str(building.building_type),
                                    "position": building.position
                                })

                for agent in orchestrator.agents.values():
                    # 检查智能体是否死亡
                    if not getattr(agent, 'is_alive', True):
                        # 检查是否可以复活
                        if getattr(agent, 'revival_count', 0) < 1:
                            # 尝试复活
                            if orchestrator.survival_system.revive(agent, buildings):
                                action_log.append(f"Tick {tick_count}: 💀➡️❤️ {agent.name} 复活了！")
                                print(f"💀➡️❤️ {agent.name} 在位置 {agent.position} 复活了！")
                                print(f"   ❤️ 健康: {agent.health}, ⚡ 能量: {agent.energy}")
                                print(f"   🍖 饥饿: {agent.hunger}, 💧 口渴: {agent.thirst}")
                            else:
                                # 复活失败，跳过这个智能体
                                continue
                        else:
                            # 已经复活过，跳过这个智能体
                            continue

                    # 决策
                    decision = orchestrator._simulate_decision(agent)

                    # 执行
                    await orchestrator.execute_action_and_learn(agent, decision)

                    # 记录
                    action = decision['action'].value.upper()
                    reason = decision.get('reasoning', '')
                    log_entry = f"Tick {tick_count}: {agent.name} {action} - {reason}"
                    action_log.append(log_entry)

                    # 保持最近100条
                    if len(action_log) > 100:
                        action_log = action_log[-100:]

                    # **关键：输出到终端**
                    print(f"🤖 {log_entry}")
                    print(f"   📍 位置: {agent.position}")
                    print(f"   ⚡ 能量: {agent.energy:.0f}")
                    print(f"   🎒 物品: {agent.inventory}")
                    print()

                # === 新增：繁衍系统更新 ===
                # 1. 检查怀孕进度并生育
                agents_to_check = list(orchestrator.agents.values())
                for agent in agents_to_check:
                    if agent.pregnancy_start_tick is not None:
                        if orchestrator.reproduction_system.check_pregnancy_progress(agent, tick_count):
                            # 找到配偶
                            if agent.spouse_id and agent.spouse_id in orchestrator.agents:
                                spouse = orchestrator.agents[agent.spouse_id]
                                child = orchestrator.reproduction_system.create_child(
                                    agent,
                                    spouse,
                                    tick_count
                                )
                                if child:
                                    # 将孩子添加到世界
                                    orchestrator.agents[child.id] = child
                                    # 添加位置验证
                                    if child.position in world.locations:
                                        world.locations[child.position].agents_present.append(child.id)
                                    action_log.append(f"Tick {tick_count}: 👶 {child.name} 出生了！")
                                    print(f"👶 {agent.name} 和 {spouse.name} 生下了 {child.name}！")

                # 2. 尝试让已婚智能体怀孕
                for agent in orchestrator.agents.values():
                    if (agent.relationship_status == "married" and
                        agent.pregnancy_start_tick is None and
                        agent.spouse_id and
                        agent.spouse_id in orchestrator.agents):

                        # 检查是否可以怀孕
                        can_conceive, reason = orchestrator.reproduction_system.can_conceive(agent)
                        if can_conceive:
                            success = orchestrator.reproduction_system.start_pregnancy(agent, tick_count)
                            if success:
                                action_log.append(f"Tick {tick_count}: 🤰 {agent.name} 怀孕了！")

            # 每10个tick保存一次
            save_counter += 1
            if save_counter >= 10:
                save_counter = 0
                save_civilization_state()

            # 每3秒一次
            await asyncio.sleep(3)

        except Exception as e:
            print(f"❌ 循环错误: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(3)

def save_civilization_state():
    """保存文明状态到文件"""
    try:
        import json
        os.makedirs("data", exist_ok=True)

        state = {
            "tick": tick_count,
            "actions": action_log[-100:],  # 保存最近100个事件
            "world": {
                "day": world.day if world else 1,
                "time_of_day": world.time_of_day if world else 0,
                "weather": world.weather if world else "clear"
            },
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "position": list(a.position),
                    "energy": a.energy,
                    "inventory": a.inventory
                }
                for a in orchestrator.agents.values()
            ] if orchestrator else []
        }

        with open("data/civilization_state.json", "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print(f"💾 已保存文明状态 (Tick {tick_count})")

    except Exception as e:
        print(f"⚠️  保存失败: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("启动确保能看到输出的服务器...")
    print("=" * 70 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,  # 改为8888避免冲突
        log_level="error",  # 减少干扰日志
        access_log=False
    )