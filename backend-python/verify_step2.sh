#!/bin/bash

# 第2步监控端点验证脚本
# 验证健康检查和监控功能

echo "🔍 第2步监控端点验证开始..."
echo "================================================"

# 切换到正确目录
cd "$(dirname "$0")"

# 启动应用（后台运行）
echo "🚀 启动应用进行测试..."
PORT=5002 python3 app.py &
APP_PID=$!

# 等待应用启动
sleep 3

# 测试基础健康检查
echo "📋 1. 测试基础健康检查端点"
response=$(curl -s -w "%{http_code}" http://localhost:5002/health)
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "  ✅ /health 端点正常 (HTTP $http_code)"
else
    echo "  ❌ /health 端点异常 (HTTP $http_code)"
fi

# 测试详细健康检查
echo ""
echo "🔍 2. 测试详细健康检查端点"
response=$(curl -s -w "%{http_code}" http://localhost:5002/health/detailed)
http_code="${response: -3}"
if [ "$http_code" = "200" ] || [ "$http_code" = "503" ]; then
    echo "  ✅ /health/detailed 端点正常 (HTTP $http_code)"
    # 显示响应内容的一部分
    response_body="${response%???}"
    echo "  📊 响应预览: $(echo "$response_body" | head -c 100)..."
else
    echo "  ❌ /health/detailed 端点异常 (HTTP $http_code)"
fi

# 测试系统状态
echo ""
echo "🖥️  3. 测试系统状态端点"
response=$(curl -s -w "%{http_code}" http://localhost:5002/status)
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "  ✅ /status 端点正常 (HTTP $http_code)"
else
    echo "  ❌ /status 端点异常 (HTTP $http_code)"
fi

# 测试版本信息
echo ""
echo "📌 4. 测试版本信息端点"
response=$(curl -s -w "%{http_code}" http://localhost:5002/version)
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "  ✅ /version 端点正常 (HTTP $http_code)"
else
    echo "  ❌ /version 端点异常 (HTTP $http_code)"
fi

# 测试响应时间
echo ""
echo "⏱️  5. 测试响应时间"
start_time=$(python3 -c "import time; print(int(time.time() * 1000))")
curl -s http://localhost:5002/health > /dev/null
end_time=$(python3 -c "import time; print(int(time.time() * 1000))")
response_time=$((end_time - start_time))
echo "  📊 健康检查响应时间: ${response_time}ms"
if [ "$response_time" -lt 1000 ]; then
    echo "  ✅ 响应时间良好 (<1秒)"
else
    echo "  ⚠️  响应时间较慢 (>1秒)"
fi

# 测试JSON格式
echo ""
echo "📄 6. 测试JSON响应格式"
health_json=$(curl -s http://localhost:5002/health)
if echo "$health_json" | python3 -m json.tool > /dev/null 2>&1; then
    echo "  ✅ 健康检查返回有效JSON"
else
    echo "  ❌ 健康检查返回无效JSON"
fi

# 停止应用
echo ""
echo "🛑 停止测试应用..."
kill $APP_PID 2>/dev/null || true
sleep 1

# 运行单元测试
echo ""
echo "🧪 7. 运行健康检查单元测试"
if [ -f "tests/test_health_checks.py" ]; then
    python3 -m pytest tests/test_health_checks.py -v --tb=short
    if [ $? -eq 0 ]; then
        echo "  ✅ 健康检查单元测试通过"
    else
        echo "  ❌ 健康检查单元测试失败"
    fi
else
    echo "  ⚠️  健康检查测试文件不存在"
fi

echo ""
echo "================================================"
echo "🎯 第2步监控端点验证完成！"
