#!/bin/bash

# 🚀 Quote Web Python 后端 - 快速启动脚本

echo "🚀 正在启动 Quote Web Python 后端..."
echo "=================================="

# 检查是否在正确目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在 backend-python 目录中运行此脚本"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误：未找到 Python"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ 使用 Python: $PYTHON_CMD"

# 检查依赖
echo "📦 检查依赖..."
if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
    echo "❌ 缺少依赖，正在安装..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 检查数据库
if [ ! -f "db/quote.db" ]; then
    echo "📊 初始化数据库..."
    $PYTHON_CMD database.py
    if [ $? -ne 0 ]; then
        echo "❌ 数据库初始化失败"
        exit 1
    fi
fi

echo "✅ 准备就绪"
echo ""
echo "🌐 启动服务器..."
echo "📍 地址: http://localhost:3001"
echo "🛑 按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
$PYTHON_CMD app.py
