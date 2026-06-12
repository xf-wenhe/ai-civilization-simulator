#!/bin/bash

# 一键启动AI Civilization Simulator
echo "========================================"
echo "🚀 AI Civilization - 一键启动"
echo "========================================"
echo ""

# 清理所有旧进程
echo "🧹 清理旧进程..."
pkill -9 -f "working_server.py" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "npm run dev" 2>/dev/null
lsof -ti:8888 | xargs kill -9 2>/dev/null
lsof -ti:9000 | xargs kill -9 2>/dev/null
sleep 2
echo "✓ 清理完成"
echo ""

# 进入项目根目录
cd /Volumes/新/work/claude_project

# 启动后端
echo "🚀 启动后端服务器..."
cd backend
source ../test_env/bin/activate 2>/dev/null || {
    echo "   创建虚拟环境..."
    python3 -m venv ../test_env
    source ../test_env/bin/activate
}
pip install -q fastapi uvicorn python-dotenv chromadb anthropic pydantic aiofiles 2>/dev/null

python3 working_server.py &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"
echo "   后端地址: http://localhost:8888"

sleep 8

# 验证后端
if curl -s http://localhost:8888/ >/dev/null 2>&1; then
    echo "   ✅ 后端启动成功"
else
    echo "   ❌ 后端启动失败"
    exit 1
fi

cd ..

# 启动前端
echo ""
echo "🎨 启动前端服务器..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   安装前端依赖（首次需要几分钟）..."
    npm install --silent
fi

npm run dev &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"
echo "   前端地址: http://localhost:9000"

sleep 8

# 验证前端
if lsof -i:9000 >/dev/null 2>&1; then
    echo "   ✅ 前端启动成功"
else
    echo "   ❌ 前端启动失败"
    exit 1
fi

echo ""
echo "========================================"
echo "✅✅✅ 启动完成！"
echo "========================================"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:9000"
echo "   后端API: http://localhost:8888"
echo ""
echo "📊 查看智能体行动:"
echo "   curl http://localhost:8888/agents"
echo "   curl http://localhost:8888/events"
echo ""
echo "🛑 停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo "========================================"
echo ""
echo "💡 现在打开浏览器访问 http://localhost:9000"
echo ""

# 自动打开浏览器（可选）
open http://localhost:9000 2>/dev/null || echo "   （浏览器已打开或命令不支持）"

echo ""
echo "按Ctrl+C停止所有服务..."

# 等待
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✓ 已停止'; exit 0" INT TERM
wait