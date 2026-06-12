#!/bin/bash

# 确保能工作的启动脚本
echo "========================================  "
echo "🎯 AI Civilization - 保证能工作的版本"
echo "========================================  "
echo ""

# 清理
echo "🧹 清理旧进程..."
kill -9 $(lsof -ti:8000) 2>/dev/null
kill -9 $(lsof -ti:8080) 2>/dev/null
sleep 1
echo "✓ 清理完成"
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
pip install -q fastapi uvicorn python-dotenv 2>/dev/null

echo ""
echo "✅ 环境准备完成"
echo ""

# 启动服务器
echo "🚀 启动服务器..."
echo ""
echo "⚠️  你会看到智能体每3秒的行动输出！"
echo ""

python3 working_server.py

# Ctrl+C停止