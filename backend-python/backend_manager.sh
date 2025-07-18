#!/bin/bash

# Python Flask Backend Management Script

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR"

# 检测Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 错误：未找到 Python"
    exit 1
fi

case "$1" in
    start)
        echo "🚀 启动 Python Flask 后端..."
        cd "$BACKEND_DIR"
        $PYTHON_CMD app.py &
        echo "✅ 后端已启动: http://localhost:3001"
        ;;
    stop)
        echo "🛑 停止 Python Flask 后端..."
        pkill -f "app.py"
        echo "✅ 后端已停止"
        ;;
    restart)
        echo "🔄 重启 Python Flask 后端..."
        pkill -f "app.py"
        sleep 2
        cd "$BACKEND_DIR"
        $PYTHON_CMD app.py &
        echo "✅ 后端已重启: http://localhost:3001"
        ;;
    status)
        if pgrep -f "app.py" > /dev/null; then
            echo "✅ 后端正在运行"
        else
            echo "❌ 后端未运行"
        fi
        ;;
    init)
        echo "📊 初始化数据库..."
        cd "$BACKEND_DIR"
        $PYTHON_CMD database.py
        echo "✅ 数据库已初始化"
        ;;
    test)
        echo "🧪 测试 API 端点..."
        echo "1. 测试根端点:"
        curl -s http://localhost:3001/ | python -m json.tool 2>/dev/null || curl -s http://localhost:3001/
        echo -e "\n\n2. 测试名言端点:"
        curl -s "http://localhost:3001/api/quotes?page=1&pageSize=3" | python -m json.tool 2>/dev/null || curl -s "http://localhost:3001/api/quotes?page=1&pageSize=3"
        echo -e "\n\n3. 测试用户注册:"
        curl -s -X POST http://localhost:3001/api/auth/register \
          -H "Content-Type: application/json" \
          -d '{"username": "testapi", "password": "testpass123"}' | python -m json.tool 2>/dev/null || curl -s -X POST http://localhost:3001/api/auth/register -H "Content-Type: application/json" -d '{"username": "testapi", "password": "testpass123"}'
        echo -e "\n\n✅ API 测试完成"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|init|test}"
        echo "  start   - 启动后端服务器"
        echo "  stop    - 停止后端服务器"
        echo "  restart - 重启后端服务器"
        echo "  status  - 检查后端运行状态"
        echo "  init    - 初始化数据库"
        echo "  test    - 运行 API 测试"
        exit 1
        ;;
esac

exit 0
