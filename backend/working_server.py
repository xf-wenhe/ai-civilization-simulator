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
            "energy": a.energy,
            "inventory": a.inventory,
            "current_action": a.current_action.value if a.current_action else "idle"
        })
    return result

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
        "size": f"{world.width}x{world.height}" if world else "0x0"
    }

async def run_simulation():
    """模拟循环 - 让智能体每3秒行动一次"""
    global tick_count, action_log

    print("🚀 模拟循环开始！\n")

    while True:
        try:
            # 增加tick
            tick_count += 1

            # 推进世界
            if world:
                world.advance_time()

            # 让每个智能体行动
            if orchestrator:
                for agent in orchestrator.agents.values():
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

            # 每3秒一次
            await asyncio.sleep(3)

        except Exception as e:
            print(f"❌ 循环错误: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(3)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("启动确保能看到输出的服务器...")
    print("=" * 70 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="error",  # 减少干扰日志
        access_log=False
    )