#!/bin/bash

# 第1步统一性验证脚本
# 验证开发环境和生产环境的配置统一性

echo "🔍 第1步统一性验证开始..."
echo "================================================"

# 1. Python版本检查
echo "📋 1. Python版本检查"
echo "当前Python版本: $(python3 --version)"
echo "runtime.txt指定版本: $(cat runtime.txt)"
echo ""

# 2. 依赖文件一致性检查
echo "📦 2. 依赖文件一致性检查"

# 检查核心依赖版本是否一致
echo "检查Flask版本一致性:"
flask_dev=$(grep "^Flask==" requirements.txt)
flask_prod=$(grep "^Flask==" requirements_prod.txt)
echo "  开发环境: $flask_dev"
echo "  生产环境: $flask_prod"
if [ "$flask_dev" = "$flask_prod" ]; then
    echo "  ✅ Flask版本一致"
else
    echo "  ❌ Flask版本不一致"
fi

echo ""
echo "检查JWT版本一致性:"
jwt_dev=$(grep "^Flask-JWT-Extended==" requirements.txt)
jwt_prod=$(grep "^Flask-JWT-Extended==" requirements_prod.txt)
echo "  开发环境: $jwt_dev"
echo "  生产环境: $jwt_prod"
if [ "$jwt_dev" = "$jwt_prod" ]; then
    echo "  ✅ JWT版本一致"
else
    echo "  ❌ JWT版本不一致"
fi

echo ""

# 3. 环境变量配置检查
echo "🔧 3. 环境变量配置检查"
echo "检查是否存在环境配置文件:"
if [ -f ".env.example" ]; then
    echo "  ✅ .env.example 存在"
else
    echo "  ❌ .env.example 不存在"
fi

if [ -f ".env.production" ]; then
    echo "  ✅ .env.production 存在"
else
    echo "  ❌ .env.production 不存在"
fi

echo ""

# 4. 应用导入测试
echo "🧪 4. 应用导入测试"
python3 -c "import app; print('  ✅ 应用导入成功')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  应用可以正常导入"
else
    echo "  ❌ 应用导入失败"
fi

echo ""

# 5. Gunicorn配置测试
echo "🚀 5. Gunicorn配置测试"
if command -v gunicorn &> /dev/null; then
    gunicorn --check-config app:app 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ Gunicorn配置正确"
    else
        echo "  ❌ Gunicorn配置有问题"
    fi
else
    echo "  ❌ Gunicorn未安装"
fi

echo ""

# 6. 数据库连接器测试
echo "🗄️  6. 数据库连接器测试"
python3 -c "import psycopg2; print('  ✅ PostgreSQL连接器可用')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  PostgreSQL连接器工作正常"
else
    echo "  ❌ PostgreSQL连接器有问题"
fi

python3 -c "import sqlite3; print('  ✅ SQLite连接器可用')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  SQLite连接器工作正常"
else
    echo "  ❌ SQLite连接器有问题"
fi

echo ""
echo "================================================"
echo "🎯 第1步统一性验证完成！"
