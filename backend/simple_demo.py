"""
最简单的测试服务器 - 确保能看到智能体行动
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os

os.environ['USE_SIMULATION'] = 'true'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量 - 在模块级别定义
world = None
orchestrator = None
events = []  # 在这里定义，不在函数内部

@app.on_event("startup")
async def startup():
    global world, orchestrator, events

    print("\n" + "=" * 60)
    print("🎮 启动最简单的演示版本...")
    print("=" * 60 + "\n")

    from world_state import WorldState
    from orchestrator import EnhancedAgentOrchestrator

    # 创建小世界
    world = WorldState(width=10, height=10)
    world.initialize_world()
    print("✓ 世界创建完成")

    # 创建智能体
    orchestrator = EnhancedAgentOrchestrator(world, agent_count=5)
    print(f"✓ 创建了 {len(orchestrator.agents)} 个智能体")

    # 初始化事件
    events = ["游戏开始！智能体们开始在世界上活动..."]

    # 启动模拟
    asyncio.create_task(simulation_loop())
    print("✓ 模拟循环启动")

    print("\n" + "=" * 60)
    print("✅ 服务器就绪！")
    print("=" * 60)
    print("\n📱 API端点:")
    print("   http://localhost:8000/")
    print("   http://localhost:8000/agents")
    print("   http://localhost:8000/events")
    print("\n👀 观察智能体行动（终端会实时输出）\n")

@app.get("/")
async def root():
    global events
    return {
        "status": "running",
        "agents": len(orchestrator.agents) if orchestrator else 0,
        "tick": world.tick if world else 0,
        "events_count": len(events)
    }

@app.get("/agents")
async def get_agents():
    if not orchestrator:
        return []

    return [{
        "id": a.id,
        "name": a.name,
        "position": list(a.position),
        "energy": a.energy,
        "inventory": a.inventory,
        "action": a.current_action.value if a.current_action else "idle"
    } for a in orchestrator.agents.values()]

@app.get("/events")
async def get_events():
    global events
    return {"events": events[-20:], "total": len(events)}

@app.get("/world")
async def get_world():
    return {
        "tick": world.tick,
        "day": world.day,
        "size": f"{world.width}x{world.height}"
    }

async def simulation_loop():
    """模拟循环 - 让智能体真正动起来"""
    global events  # 声明使用全局变量

    print("\n" + "=" * 60)
    print("🤖 智能体开始行动了！每3秒一次决策")
    print("=" * 60 + "\n")

    while True:
        try:
            # 推进时间
            world.advance_time()

            # 每个智能体行动
            for agent in orchestrator.agents.values():
                # 决策
                decision = orchestrator._simulate_decision(agent)

                # 执行
                await orchestrator.execute_action_and_learn(agent, decision)

                # 记录事件
                action = decision['action'].value.upper()
                reason = decision.get('reasoning', 'no reason')
                event = f"Tick {world.tick}: {agent.name} {action} - {reason}"
                events.append(event)

                # 保持最近100个事件
                if len(events) > 100:
                    events = events[-100:]

                # **关键：实时输出到终端**
                print(f"🤖 {event}")
                print(f"   📍 位置: {agent.position} | ⚡ 能量: {agent.energy:.0f} | 🎒 物品: {agent.inventory}")
                print()

            # 每3秒一次
            await asyncio.sleep(3)

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(3)

if __name__ == "__main__":
    print("\n启动演示服务器...\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")