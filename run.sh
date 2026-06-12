#!/bin/bash

echo "========================================="
echo "🚀 AI Civilization Simulator 启动"
echo "========================================="
echo ""

# 切换到backend目录
cd backend || exit 1

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env不存在，从模板创建..."
    cp .env.example .env
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装Python依赖..."
pip install -q -r requirements.txt
echo "✓ 依赖安装完成"

# 测试模块导入
echo "🔍 测试模块导入..."
python3 -c "from agent import Agent; print('  ✓ agent')" &&
python3 -c "from world_state import WorldState; print('  ✓ world_state')" &&
python3 -c "from orchestrator import EnhancedAgentOrchestrator; print('  ✓ orchestrator')" &&
echo "✓ 所有模块测试通过"

echo ""
echo "========================================="
echo "✅ 系统准备完成！"
echo "========================================="
echo ""
echo "现在启动服务："
echo "  - 后端API: http://localhost:8000"
echo "  - 前端界面: http://localhost:8080"
echo ""
echo "按Ctrl+C停止所有服务"
echo ""

# 启动后端服务器（后台运行）
python3 server.py &
SERVER_PID=$!

# 等待服务器启动
sleep 3

# 启动模拟引擎（后台运行）
python3 main.py &
SIM_PID=$!

# 切换到frontend目录
cd ../frontend || exit 1

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install --silent
fi

# 启动前端开发服务器
echo "🎨 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 所有服务已启动！"
echo ""

# 等待所有进程
wait $SERVER_PID $SIM_PID $FRONTEND_PID