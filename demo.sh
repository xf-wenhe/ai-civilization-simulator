#!/bin/bash

echo "========================================="
echo "🎮 AI文明演示 - 简单版"
echo "========================================="
echo ""

# 停止所有旧服务
echo "🛑 停止旧服务..."
kill -9 $(lsof -ti:8000) 2>/dev/null
kill -9 $(lsof -ti:8080) 2>/dev/null
sleep 2
echo "✓ 清理完成"
echo ""

cd backend || exit 1

# 准备环境
if [ ! -d "venv" ]; then
    echo "📦 创建环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q fastapi uvicorn python-dotenv 2>/dev/null

echo "🚀 启动演示服务器..."
echo ""
echo "⚠️  注意：你会看到智能体实时行动的输出！"
echo ""

python3 simple_demo.py

# Ctrl+C停止