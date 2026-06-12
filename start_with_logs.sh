#!/bin/bash

# 完整的启动脚本 - 带详细输出和日志
echo "========================================"
echo "🚀 AI Civilization Simulator 启动"
echo "========================================"
echo ""

# 进入backend
cd backend || exit 1
echo "✓ 进入backend目录"

# 确保.env存在
if [ ! -f ".env" ]; then
    echo "⚠️  .env不存在，从模板创建..."
    cp .env.example .env
fi
echo "✓ .env配置已确认"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv || exit 1
    echo "✓ 虚拟环境创建完成"
fi

# 激活并安装依赖
echo "🔧 激活虚拟环境..."
source venv/bin/activate || exit 1

echo "📦 检查并安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt || exit 1
echo "✓ 依赖安装完成"

# 验证安装
echo "🔍 验证模块导入..."
python3 -c "from agent import Agent; print('  ✓ agent模块')" || exit 1
python3 -c "from world_state import WorldState; print('  ✓ world_state模块')" || exit 1
python3 -c "from orchestrator import EnhancedAgentOrchestrator; print('  ✓ orchestrator模块')" || exit 1
python3 -c "from server import app; print('  ✓ server模块')" || exit 1

echo ""
echo "✅ 后端准备完成"
echo ""

# 启动后端服务（带日志）
echo "🌐 启动后端API服务..."
echo "  地址: http://localhost:8000"
python3 server.py &
SERVER_PID=$!
echo "  PID: $SERVER_PID"
sleep 3

# 检查服务器是否启动
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✓ API服务器响应正常"
else
    echo "⚠️  API服务器启动可能有问题，请查看日志"
fi

echo ""
echo "🌍 启动AI文明模拟引擎..."
python3 main.py &
SIM_PID=$!
echo "  PID: $SIM_PID"
sleep 2

echo "✓ 模拟引擎已启动"
echo ""

# 返回根目录准备前端
cd ..

echo "🎨 准备前端..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖（首次需要几分钟）..."
    npm install --silent || exit 1
    echo "✓ 前端依赖安装完成"
else
    echo "✓ 前端依赖已存在"
fi

echo ""
echo "💻 启动前端服务..."
echo "  地址: http://localhost:8080"
npm run dev &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID"

sleep 3

echo ""
echo "========================================"
echo "✅ 所有服务启动完成！"
echo "========================================"
echo ""
echo "📊 服务状态检查："

# 检查各服务状态
if curl -s http://localhost:8000/world > /dev/null 2>&1; then
    echo "  ✓ 后端API: 正常响应"
    echo "    访问: http://localhost:8000/world"
else
    echo "  ⚠️  后端API: 可能未启动"
fi

if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "  ✓ 前端界面: 正常运行"
    echo "    访问: http://localhost:8080"
else
    echo "  ⚠️  前端界面: 可能未启动"
fi

echo ""
echo "========================================"
echo ""
echo "💡 提示："
echo "  - 按 Ctrl+C 停止所有服务"
echo "  - 后端日志会实时输出"
echo "  - 如果前端卡住，刷新浏览器"
echo ""
echo "========================================"

# 等待所有进程，显示输出
trap "echo ''; echo '🛑 停止所有服务...'; kill $SERVER_PID $SIM_PID $FRONTEND_PID 2>/dev/null; echo '✓ 服务已停止'; exit 0" INT TERM

# 显示后端输出（实时日志）
wait $SERVER_PID $SIM_PID $FRONTEND_PID