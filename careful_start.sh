#!/bin/bash

echo "========================================="
echo "🎯 AI Civilization - 最安全启动"
echo "========================================="
echo ""

# 完全不kill任何进程，只检查端口
echo "🔍 检查端口..."

# 检查8888端口
if lsof -i:8888 >/dev/null 2>&1; then
    echo "❌ 端口8888已被占用，请先停止占用的程序"
    echo "   查看占用进程: lsof -i:8888"
    exit 1
fi

echo "✅ 端口8888可用"
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

echo "📦 安装依赖..."
pip install -q fastapi uvicorn python-dotenv chromadb anthropic pydantic aiofiles 2>/dev/null

echo ""
echo "✅ 准备完成"
echo ""

# 启动服务器
echo "🚀 启动服务器..."
echo ""
echo "========================================="
echo "📊 服务信息:"
echo "   后端API: http://localhost:8888"
echo "   智能体数量: 5"
echo "   更新频率: 每3秒"
echo "========================================="
echo ""
echo "👀 观察终端输出，你会看到智能体行动！"
echo ""

python3 working_server.py

# Ctrl+C停止