#!/bin/bash

# 完整的启动脚本 - 已全面测试
echo "========================================"
echo "🚀 AI Civilization Simulator"
echo "========================================"
echo ""

# 进入backend
cd backend || exit 1

# 确保.env存在
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ 创建.env配置"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv || exit 1
fi

# 激活并安装依赖
echo "🔧 激活虚拟环境..."
source venv/bin/activate || exit 1

echo "📦 安装依赖（首次需要几分钟）..."
pip install -q --upgrade pip
pip install -q -r requirements.txt || exit 1

# 验证安装
echo "🔍 验证模块..."
python3 -c "from agent import Agent; print('  ✓ agent')" || exit 1
python3 -c "from world_state import WorldState; print('  ✓ world_state')" || exit 1
python3 -c "from orchestrator import EnhancedAgentOrchestrator; print('  ✓ orchestrator')" || exit 1

echo ""
echo "✅ 后端准备完成"
echo ""

# 启动后端服务
echo "🌐 启动后端API服务 (http://localhost:8000)..."
python3 server.py > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

echo "🌍 启动AI文明模拟引擎..."
python3 main.py > /dev/null 2>&1 &
SIM_PID=$!

echo "✓ 后端服务已启动"
echo ""

# 返回根目录
cd ..

# 前端准备
echo "🎨 准备前端..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖（首次需要几分钟）..."
    npm install --silent || exit 1
fi

echo "✅ 前端准备完成"
echo ""

# 启动前端
echo "💻 启动前端服务 (http://localhost:8080)..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "✅ 所有服务启动成功！"
echo "========================================"
echo ""
echo "访问地址:"
echo "  🖥️  前端界面: http://localhost:8080"
echo "  📊 后端API: http://localhost:8000"
echo ""
echo "提示:"
echo "  - 5个AI智能体正在自主运行"
echo "  - 使用讯飞API或智能模拟模式"
echo "  - 按 Ctrl+C 停止所有服务"
echo ""

# 等待
trap "echo ''; echo '🛑 停止所有服务...'; kill $SERVER_PID $SIM_PID $FRONTEND_PID 2>/dev/null; echo '✓ 服务已停止'; exit 0" INT TERM

wait