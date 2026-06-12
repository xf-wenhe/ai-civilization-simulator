#!/bin/bash

echo "========================================"
echo "🎯 AI Civilization - 完整启动"
echo "========================================"
echo ""

# 检查端口
if lsof -i:8888 >/dev/null 2>&1; then
    echo "❌ 端口8888已被占用"
    exit 1
fi

if lsof -i:9000 >/dev/null 2>&1; then
    echo "⚠️  端口9000已被占用，前端可能已在运行"
fi

echo "✅ 端口检查完成"
echo ""

# 启动后端
cd backend || exit 1

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q fastapi uvicorn python-dotenv chromadb anthropic pydantic aiofiles 2>/dev/null

echo "🚀 启动后端服务器..."
python3 working_server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"
echo "   后端API: http://localhost:8888"

sleep 5

# 检查后端
if curl -s http://localhost:8888/ > /dev/null 2>&1; then
    echo "   ✅ 后端启动成功"
else
    echo "   ❌ 后端启动失败"
    cat /tmp/backend.log
    exit 1
fi

cd ..

# 启动前端
echo ""
echo "🎨 启动前端服务器..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "   安装前端依赖..."
    npm install --silent
fi

npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"
echo "   前端界面: http://localhost:9000"

sleep 3

if lsof -i:9000 >/dev/null 2>&1; then
    echo "   ✅ 前端启动成功"
else
    echo "   ❌ 前端启动失败"
    cat /tmp/frontend.log
fi

echo ""
echo "========================================"
echo "✅ 所有服务启动完成！"
echo "========================================"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:9000"
echo "   后端API: http://localhost:8888"
echo ""
echo "💾 文明会自动保存到: backend/data/civilization_state.json"
echo "   重启后会自动加载之前的进度"
echo ""
echo "🛑 停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo "========================================"
echo ""

# 保持运行
trap "echo ''; echo '🛑 停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✓ 服务已停止'; exit 0" INT TERM

# 显示后端日志
tail -f /tmp/backend.log