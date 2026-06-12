#!/bin/bash

echo "========================================="
echo "🚀 AI Civilization Simulator 一键启动"
echo "========================================="
echo ""

# 切换到项目根目录
cd /Volumes/新/work/claude_project || exit 1

# 后端设置
echo "📦 设置后端环境..."
cd backend

# 检查.env
if [ ! -f ".env" ]; then
    echo "  创建.env配置文件..."
    cp .env.example .env
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "  创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "  安装依赖..."
source venv/bin/activate
pip install -q -r requirements.txt

# 测试模块
echo "  测试模块..."
python3 -c "from agent import Agent; from world_state import WorldState; print('  ✓ 后端模块OK')" || exit 1

echo "✓ 后端准备完成"
echo ""

# 启动后端服务
echo "🌐 启动后端服务..."
python3 server.py &
SERVER_PID=$!
sleep 2

echo "🌍 启动模拟引擎..."
python3 main.py &
SIM_PID=$!

cd ..

# 前端设置
echo ""
echo "🎨 设置前端环境..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖（首次需要几分钟）..."
    npm install --silent
fi

echo "✓ 前端准备完成"
echo ""

# 启动前端
echo "💻 启动前端服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "✅ 所有服务启动成功！"
echo "========================================="
echo ""
echo "访问地址："
echo "  🖥️  前端界面: http://localhost:8080"
echo "  📊 后端API: http://localhost:8000"
echo ""
echo "提示："
echo "  - 按 Ctrl+C 停止所有服务"
echo "  - 首次启动可能需要几秒钟加载"
echo ""
echo "等待服务启动..."

# 等待进程
trap "echo ''; echo '停止所有服务...'; kill $SERVER_PID $SIM_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait