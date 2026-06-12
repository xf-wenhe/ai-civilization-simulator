"""
简化版测试服务器 - 用于快速验证，确保能成功运行
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os

# 设置模拟模式
os.environ['USE_SIMULATION'] = 'true'

app = FastAPI(title="AI Civilization Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
world = None
orchestrator = None

@app.on_event("startup")
async def startup():
    global world, orchestrator

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
        print(f"   ✓ 总位置数: {len(world.locations)}")

        # 2. 创建智能体
        print("\n📍 步骤2: 创建AI智能体...")
        from orchestrator import EnhancedAgentOrchestrator
        orchestrator = EnhancedAgentOrchestrator(world, agent_count=5)
        print(f"   ✓ 智能体创建成功: {len(orchestrator.agents)}个")

        for agent_id, agent in orchestrator.agents.items():
            print(f"     - {agent.name} (位置: {agent.position})")

        print(f"   ✓ 模拟模式: {'是' if orchestrator.use_simulation else '否'}")

        # 3. 启动模拟循环
        print("\n📍 步骤3: 启动模拟引擎...")
        asyncio.create_task(run_simulation())
        print("   ✓ 模拟引擎已启动（后台运行）")

        print("\n" + "=" * 60)
        print("✅ 所有系统就绪！服务器启动成功！")
        print("=" * 60)
        print("\n🌐 API端点:")
        print("   - 根路径: http://localhost:8000/")
        print("   - 世界状态: http://localhost:8000/world")
        print("   - 智能体列表: http://localhost:8000/agents")
        print("   - 地图数据: http://localhost:8000/world/map")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "AI Civilization Simulator",
        "status": "running",
        "agents": len(orchestrator.agents) if orchestrator else 0,
        "world_size": f"{world.width}x{world.height}" if world else "unknown",
        "tick": world.tick if world else 0,
        "simulation_mode": orchestrator.use_simulation if orchestrator else True
    }

@app.get("/world")
async def get_world():
    """获取世界状态"""
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

@app.get("/agents")
async def get_agents():
    """获取所有智能体"""
    if not orchestrator:
        return []

    return [
        {
            "id": agent.id,
            "name": agent.name,
            "position": list(agent.position),
            "health": agent.health,
            "energy": agent.energy,
            "inventory": agent.inventory,
            "current_action": agent.current_action.value if agent.current_action else None,
            "skills": agent.skills
        }
        for agent in orchestrator.agents.values()
    ]

@app.get("/world/map")
async def get_world_map():
    """获取完整地图数据"""
    if not world:
        return {"error": "World not initialized"}

    return world.to_dict()

async def run_simulation():
    """模拟循环 - 后台运行"""
    print("\n🔄 模拟循环开始运行...\n")

    while True:
        try:
            # 推进时间
            world.advance_time()

            # 每10个tick输出一次状态
            if world.tick % 10 == 0:
                print(f"\n⏰ Tick {world.tick} | Day {world.day} | Time: {world.time_of_day:.1f}h")

                # 让每个智能体做决策
                for agent_id, agent in orchestrator.agents.items():
                    try:
                        # 使用模拟决策
                        decision = orchestrator._simulate_decision(agent)

                        # 执行动作
                        await orchestrator.execute_action_and_learn(agent, decision)

                        # 输出决策
                        action_str = decision['action'].value
                        reasoning = decision.get('reasoning', '')
                        print(f"   🤖 {agent.name}: {action_str.upper()} - {reasoning}")

                    except Exception as e:
                        print(f"   ❌ {agent.name} 决策错误: {e}")

            # 每5秒一个tick
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n❌ 模拟循环错误: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("启动AI Civilization Simulator 测试服务器...")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False  # 减少日志输出
    )