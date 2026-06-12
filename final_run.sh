#!/bin/bash

echo "========================================="
echo "🚀 AI Civilization Simulator"
echo "========================================="
echo ""

# 切换到backend目录
cd backend || exit 1

# 检查.env
if [ ! -f ".env" ]; then
    echo "⚠️  创建.env配置文件..."
    cp .env.example .env
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv || exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate || exit 1

# 安装依赖
echo "📦 安装Python依赖..."
pip install -q -r requirements.txt || exit 1
echo "✓ 依赖安装完成"

# 测试模块
echo "🔍 测试模块导入..."
python3 -c "from agent import Agent; print('  ✓ agent模块')" || exit 1
python3 -c "from world_state import WorldState; print('  ✓ world_state模块')" || exit 1
python3 -c "from orchestrator import EnhancedAgentOrchestrator; print('  ✓ orchestrator模块')" || exit 1

echo ""
echo "✅ 后端准备完成"
echo ""

# 启动后端服务
echo "🌐 启动后端服务 (port 8000)..."
python3 server.py &
SERVER_PID=$!
sleep 2

echo "🌍 启动模拟引擎..."
python3 main.py &
SIM_PID=$!

# 返回项目根目录
cd ..

# 前端设置
echo ""
echo "🎨 准备前端..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install --silent || exit 1
fi

echo "✅ 前端准备完成"
echo ""

# 启动前端
echo "💻 启动前端服务 (port 8080)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "✅ 所有服务已启动！"
echo "========================================="
echo ""
echo "访问地址:"
echo "  🖥️  前端: http://localhost:8080"
echo "  📊 后端: http://localhost:8000"
echo ""
echo "按Ctrl+C停止所有服务"
echo ""

# 等待进程
trap "echo ''; echo '停止服务...'; kill $SERVER_PID $SIM_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait