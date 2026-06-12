#!/bin/bash

echo "========================================"
echo "🎯 AI Civilization - 安全启动脚本"
echo "========================================"
echo ""

# 只停止我们自己的进程（不影响其他应用）
echo "🧹 清理AI Civilization进程..."
pkill -9 -f "working_server.py" 2>/dev/null
pkill -9 -f "simple_demo.py" 2>/dev/null

# 只检查我们的端口是否被占用
if lsof -ti:8888 >/dev/null 2>&1; then
    echo "⚠️  端口8888被占用，停止占用进程..."
    lsof -ti:8888 | xargs kill -9 2>/dev/null
fi

if lsof -ti:9000 >/dev/null 2>&1; then
    echo "⚠️  端口9000被占用，停止占用进程..."
    lsof -ti:9000 | xargs kill -9 2>/dev/null
fi

sleep 1
echo "✓ 清理完成（仅AI Civilization进程）"
echo ""

# 进入backend
cd backend || exit 1

# 准备环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔧 激活环境..."
source venv/bin/activate

echo "📦 确保依赖安装..."
pip install -q fastapi uvicorn python-dotenv chromadb anthropic pydantic aiofiles 2>/dev/null

echo ""
echo "✅ 准备完成"
echo ""

# 启动服务器
echo "🚀 启动服务器..."
echo ""
echo "========================================="
echo "👀 现在看终端输出！"
echo "   你会看到智能体每3秒的行动！"
echo "========================================="
echo ""
echo "🌐 后端API: http://localhost:8888"
echo ""

python3 working_server.py

# Ctrl+C停止