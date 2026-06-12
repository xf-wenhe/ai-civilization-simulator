#!/bin/bash

echo "========================================="
echo "AI Civilization Simulator - 系统检查"
echo "========================================="
echo ""

# 检查Python版本
echo "📋 检查Python版本..."
PYTHON_VERSION=$(python3 --version)
echo "  $PYTHON_VERSION"
echo ""

# 检查项目结构
echo "📁 检查项目结构..."
if [ -d "backend" ]; then
    echo "  ✓ backend目录存在"
else
    echo "  ✗ backend目录不存在"
    exit 1
fi

if [ -d "frontend" ]; then
    echo "  ✓ frontend目录存在"
else
    echo "  ✗ frontend目录不存在"
    exit 1
fi

if [ -f "backend/.env" ]; then
    echo "  ✓ backend/.env配置文件存在"
else
    echo "  ✗ backend/.env不存在，从模板创建..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "  ✓ 已创建.env文件"
    else
        echo "  ✗ backend/.env.example不存在"
        exit 1
    fi
fi
echo ""

# 测试Python模块导入
echo "🔍 测试Python模块导入..."
python3 -c "import sys; sys.path.insert(0, 'backend'); from agent import Agent; print('  ✓ agent模块OK')" || exit 1
python3 -c "import sys; sys.path.insert(0, 'backend'); from world_state import WorldState; print('  ✓ world_state模块OK')" || exit 1
python3 -c "import sys; sys.path.insert(0, 'backend'); from memory_system import AgentMemorySystem; print('  ✓ memory_system模块OK')" 2>/dev/null || echo "  ⚠ memory_system需要chromadb（稍后安装）"
python3 -c "import sys; sys.path.insert(0, 'backend'); from communication import CommunicationSystem; print('  ✓ communication模块OK')" 2>/dev/null || echo "  ⚠ communication需要anthropic（稍后安装）"
python3 -c "import sys; sys.path.insert(0, 'backend'); from knowledge_system import KnowledgeSystem; print('  ✓ knowledge_system模块OK')" || exit 1
python3 -c "import sys; sys.path.insert(0, 'backend'); from crafting import CraftingSystem; print('  ✓ crafting模块OK')" || exit 1
echo ""

echo "========================================="
echo "✅ 系统检查通过！"
echo "========================================="
echo ""
echo "现在可以运行: ./start.sh"
echo ""