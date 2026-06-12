#!/bin/bash

echo "========================================"
echo "🎯 AI Civilization - 完整启动（修复版）"
echo "========================================"
echo ""

# 检查并清理端口
echo "🔍 检查端口状态..."

# 检查8888
if lsof -i:8888 >/dev/null 2>&1; then
    echo "⚠️  8888端口已被占用"
    OLD_BACKEND=$(lsof -ti:8888)
    if ps -p $OLD_BACKEND -o command= | grep -q "working_server"; then
        echo "   停止旧的working_server进程..."
        kill -9 $OLD_BACKEND 2>/dev/null
        sleep 2
    else
        echo "❌ 端口被其他程序占用，请手动处理"
        lsof -i:8888
        exit 1
    fi
fi

# 检查9000
if lsof -i:9000 >/dev/null 2>&1; then
    echo "⚠️  9000端口已被占用"
    OLD_FRONTEND=$(lsof -ti:9000)
    if ps -p $OLD_FRONTEND -o command= | grep -q "vite\|node"; then
        echo "   停止旧的前端进程..."
        kill -9 $OLD_FRONTEND 2>/dev/null
        sleep 2
    else
        echo "❌ 端口被其他程序占用，请手动处理"
        lsof -i:9000
        exit 1
    fi
fi

echo "✅ 端口检查完成"
echo ""

# 启动后端
echo "🚀 启动后端服务器..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "   创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q fastapi uvicorn python-dotenv chromadb anthropic pydantic aiofiles 2>/dev/null

# 启动后端（在前台运行以便看到输出）
python3 working_server.py &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"
echo "   后端API: http://localhost:8888"

sleep 5

# 检查后端
if curl -s http://localhost:8888/ > /dev/null 2>&1; then
    echo "   ✅ 后端启动成功"
else
    echo "   ❌ 后端启动失败"
    exit 1
fi

cd ..

# 启动前端
echo ""
echo "🎨 启动前端服务器..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "   安装前端依赖（首次需要几分钟）..."
    npm install --silent 2>/dev/null
fi

echo "   启动Vite开发服务器..."
npm run dev 2>&1 &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"
echo "   前端界面: http://localhost:9000"

sleep 5

# 检查前端
if lsof -i:9000 >/dev/null 2>&1; then
    echo "   ✅ 前端启动成功"
    echo ""
    echo "========================================"
    echo "✅✅✅ 所有服务启动完成！"
    echo "========================================"
    echo ""
    echo "🌐 访问地址:"
    echo "   🖥️  前端界面: http://localhost:9000"
    echo "   📊 后端API: http://localhost:8888"
    echo ""
    echo "💡 提示:"
    echo "   - 智能体每3秒行动一次"
    echo "   - 能量低于30会自动休息恢复"
    echo "   - 文明状态每10tick自动保存"
    echo ""
    echo "🛑 停止服务:"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "========================================"
else
    echo "   ❌ 前端启动失败"
    echo "   查看错误:"
    npm run dev
fi

# 保持运行
trap "echo ''; echo '🛑 停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✓ 服务已停止'; exit 0" INT TERM

# 等待
wait