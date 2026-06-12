#!/bin/bash

# 完整功能启动脚本 - 智能体真正会行动
echo "========================================"
echo "🚀 AI Civilization Simulator - 完整版"
echo "========================================"
echo ""

# 清理旧进程
echo "🧹 清理旧进程..."
kill -9 $(lsof -ti:8000) 2>/dev/null
kill -9 $(lsof -ti:8080) 2>/dev/null
sleep 2
echo "✓ 清理完成"
echo ""

# 进入backend
cd backend || exit 1

# 确保.env存在
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv || exit 1
fi

# 激活并安装依赖
echo "🔧 激活虚拟环境..."
source venv/bin/activate || exit 1

echo "📦 安装/更新依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt || exit 1
echo "✓ 依赖就绪"

# 验证模块
echo ""
echo "🔍 验证系统..."
python3 -c "from agent import Agent; print('  ✓ agent模块')" || exit 1
python3 -c "from world_state import WorldState; print('  ✓ world_state模块')" || exit 1
python3 -c "from memory_system import AgentMemorySystem; print('  ✓ memory_system模块')" || exit 1
python3 -c "from orchestrator import EnhancedAgentOrchestrator; print('  ✓ orchestrator模块')" || exit 1

echo ""
echo "✅ 后端准备完成"
echo ""

# 启动完整功能的后端
echo "🌐 启动完整功能后端 (http://localhost:8000)..."
echo "  功能："
echo "    - 真实模拟循环"
echo "    - 智能体实时行动"
echo "    - 事件记录"
echo "    - WebSocket实时推送"
python3 full_server.py > /tmp/civilization_full.log 2>&1 &
SERVER_PID=$!
echo "  PID: $SERVER_PID"
sleep 5

# 检查启动状态
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "  ✓ API服务器响应正常"
    echo ""
    echo "📊 启动日志:"
    tail -20 /tmp/civilization_full.log
else
    echo "  ❌ API服务器启动失败"
    echo "  查看日志:"
    cat /tmp/civilization_full.log
    exit 1
fi

# 返回根目录准备前端
cd ..

echo ""
echo "🎨 准备前端..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install --silent || exit 1
fi

echo "✓ 前端准备完成"
echo ""

# 启动前端
echo "💻 启动前端服务 (http://localhost:8080)..."
npm run dev > /tmp/civilization_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID"

sleep 3

echo ""
echo "========================================"
echo "✅ 所有服务启动成功！"
echo "========================================"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:8080"
echo "   后端API: http://localhost:8000"
echo ""
echo "📊 测试API:"
echo "   curl http://localhost:8000/agents"
echo "   curl http://localhost:8000/events"
echo "   curl http://localhost:8000/world"
echo ""
echo "💡 特性:"
echo "   ✓ 智能体每5秒行动一次"
echo "   ✓ 实时事件记录"
echo "   ✓ WebSocket实时推送"
echo "   ✓ 前端自动更新"
echo ""
echo "========================================"

# 等待并显示实时日志
trap "echo ''; echo '🛑 停止所有服务...'; kill $SERVER_PID $FRONTEND_PID 2>/dev/null; echo '✓ 服务已停止'; exit 0" INT TERM

echo ""
echo "📺 实时日志 (Ctrl+C停止):"
echo "========================================"
tail -f /tmp/civilization_full.log &

wait