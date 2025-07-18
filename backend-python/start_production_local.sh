#!/bin/bash

# 本地生产环境测试脚本
# 模拟 Render 部署环境

echo "🚀 启动本地生产环境测试..."

# 设置工作目录
cd "$(dirname "$0")"

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装或不可用"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装生产依赖
echo "📥 安装生产环境依赖..."
pip install -r requirements_prod.txt

# 检查环境变量文件
if [ ! -f ".env.production" ]; then
    echo "⚠️  警告：.env.production 文件不存在，将使用默认配置"
fi

# 设置环境变量
export FLASK_ENV=production
export JWT_SECRET_KEY=local_production_test_key
export PORT=5001
export DEBUG=False

echo "🔍 环境配置："
echo "  FLASK_ENV: $FLASK_ENV"
echo "  PORT: $PORT"
echo "  DEBUG: $DEBUG"

# 初始化数据库
echo "🗄️  初始化数据库..."
python3 -c "from app import init_database; init_database()"

# 启动服务（使用 gunicorn 模拟生产环境）
echo "🌟 启动生产环境服务器 (gunicorn)..."
echo "📱 访问地址: http://localhost:$PORT"
echo "🛑 按 Ctrl+C 停止服务"

gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 --access-logfile - --error-logfile - app:app
