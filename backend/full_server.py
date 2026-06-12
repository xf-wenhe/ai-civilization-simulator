"""
完整功能的后端服务器 - 带真实模拟循环和事件记录
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os
import json

# 设置模拟模式
os.environ['USE_SIMULATION'] = 'true'

app = FastAPI(title="AI Civilization Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
world = None
orchestrator = None
recent_events = []
websocket_clients = []

@app.on_event("startup")
async def startup():
    global world, orchestrator, recent_events

    print("\n" + "=" * 60)
    print("🚀 AI Civilization Simulator - 启动中...")
    print("=" * 60 + "\n")

    try:
        # 1. 创建世界
        print("📍 步骤1: 创建世界...")
        from world_state import WorldState
        world = WorldState(width=20, height=20)
        world.initialize_world()
        print(f"   ✓ 世界创建成功: {world.width}x{world.height}")

        # 2. 创建智能体
        print("\n📍 步骤2: 创建AI智能体...")
        from orchestrator import EnhancedAgentOrchestrator
        orchestrator = EnhancedAgentOrchestrator(world, agent_count=5)
        print(f"   ✓ 智能体创建成功: {len(orchestrator.agents)}个")

        # 初始化事件日志
        recent_events = world.events_log.copy()

        # 3. 启动模拟循环
        print("\n📍 步骤3: 启动模拟引擎...")
        asyncio.create_task(run_simulation())
        print("   ✓ 模拟引擎已启动")

        print("\n" + "=" * 60)
        print("✅ 所有系统就绪！")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/")
async def root():
    return {
        "message": "AI Civilization Simulator",
        "status": "running",
        "agents": len(orchestrator.agents) if orchestrator else 0,
        "world_size": f"{world.width}x{world.height}" if world else "unknown",
        "tick": world.tick if world else 0
    }

@app.get("/world")
async def get_world():
    if not world:
        return {"error": "World not initialized"}
    return {
        "tick": world.tick,
        "day": world.day,
        "time_of_day": world.time_of_day,
        "weather": world.weather,
        "width": world.width,
        "height": world.height
    }

@app.get("/world/map")
async def get_world_map():
    if not world:
        return {"error": "World not initialized"}
    return world.to_dict()

@app.get("/agents")
async def get_agents():
    if not orchestrator:
        return []

    agents_data = []
    for agent in orchestrator.agents.values():
        agents_data.append({
            "id": agent.id,
            "name": agent.name,
            "position": list(agent.position),
            "health": agent.health,
            "energy": agent.energy,
            "inventory": agent.inventory,
            "current_action": agent.current_action.value if agent.current_action else None,
            "skills": agent.skills,
            "personality": {k.value: v for k, v in agent.personality.items()}
        })
    return agents_data

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return agent.to_dict()

@app.get("/agents/{agent_id}/memories")
async def get_agent_memories(agent_id: str, limit: int = 20):
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    recent = agent.memories[-limit:]

    return {
        "agent_id": agent_id,
        "memories": recent
    }

@app.get("/agents/{agent_id}/relationships")
async def get_agent_relationships(agent_id: str):
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return {
        "agent_id": agent_id,
        "relationships": agent.relationships
    }

@app.get("/events")
async def get_events(limit: int = 50):
    """获取最近的事件"""
    return {
        "tick": world.tick if world else 0,
        "events": recent_events[-limit:]
    }

@app.post("/world/intervene")
async def intervene_world(event_type: str, description: str):
    """触发自定义事件"""
    if not world:
        return {"error": "World not initialized"}

    event_text = f"Tick {world.tick}: INTERVENTION - {event_type}: {description}"
    recent_events.append(event_text)
    world.events_log.append(event_text)

    # 通知WebSocket客户端
    await broadcast_event(event_text)

    return {
        "status": "success",
        "event": event_text,
        "tick": world.tick
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时更新"""
    await websocket.accept()
    websocket_clients.append(websocket)

    try:
        while True:
            if world and orchestrator:
                data = {
                    "type": "world_update",
                    "tick": world.tick,
                    "day": world.day,
                    "time_of_day": world.time_of_day,
                    "agents": [
                        {
                            "id": agent.id,
                            "name": agent.name,
                            "position": list(agent.position),
                            "current_action": agent.current_action.value if agent.current_action else None,
                            "energy": agent.energy,
                            "inventory": agent.inventory
                        }
                        for agent in orchestrator.agents.values()
                    ],
                    "recent_events": recent_events[-10:]
                }
                await websocket.send_json(data)
            await asyncio.sleep(1)
    except:
        websocket_clients.remove(websocket)

async def broadcast_event(event_text):
    """广播事件到所有WebSocket客户端"""
    for client in websocket_clients:
        try:
            await client.send_json({
                "type": "event",
                "data": event_text
            })
        except:
            pass

async def run_simulation():
    """真实的模拟循环 - 让智能体真正行动"""
    print("\n🔄 模拟循环开始运行...\n")

    while True:
        try:
            # 推进世界时间
            world.advance_time()

            # 每个tick都让智能体行动
            for agent_id, agent in orchestrator.agents.items():
                try:
                    # 生成决策
                    decision = orchestrator._simulate_decision(agent)

                    # 执行动作
                    result = await orchestrator.execute_action_and_learn(agent, decision)

                    # 记录事件
                    action_str = decision['action'].value.upper()
                    reasoning = decision.get('reasoning', '')
                    event_text = f"Tick {world.tick}: {agent.name} {action_str} - {reasoning}"
                    recent_events.append(event_text)

                    # 保持最近100个事件
                    if len(recent_events) > 100:
                        recent_events = recent_events[-100:]

                    # 输出到终端
                    if world.tick % 5 == 0:
                        print(f"  ⏰ Tick {world.tick}: {agent.name} {action_str} - {reasoning}")
                        print(f"     位置: {agent.position}, 能量: {agent.energy:.0f}, 物品: {agent.inventory}")

                    # 广播到WebSocket
                    await broadcast_event(event_text)

                except Exception as e:
                    print(f"  ❌ {agent.name} 决策错误: {e}")

            # 每5秒一个tick
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n❌ 模拟循环错误: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("启动完整功能的AI Civilization Simulator...")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False
    )