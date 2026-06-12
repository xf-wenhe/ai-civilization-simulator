#!/bin/bash

echo "========================================"
echo "🔧 快速测试启动"
echo "========================================"
echo ""

cd backend || exit 1

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
fi

echo "✓ 环境准备完成"
echo ""

# 启动测试服务器（有详细输出）
echo "🚀 启动测试服务器..."
python3 test_server.py

# Ctrl+C会自动停止