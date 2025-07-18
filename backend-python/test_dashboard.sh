#!/bin/bash

# 测试状态仪表板脚本
# 用于快速检查测试状态和生成报告

echo "🧪 Flask 后端测试状态仪表板"
echo "=================================="
echo ""

# 检查是否在正确目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在 backend-python 目录中运行此脚本"
    exit 1
fi

# 检查依赖
echo "📦 检查测试依赖..."
if ! python -c "import pytest, flask, bcrypt, flask_jwt_extended, flask_cors" 2>/dev/null; then
    echo "❌ 缺少测试依赖，正在安装..."
    pip install -r test_requirements.txt
fi

echo "✅ 依赖检查完成"
echo ""

# 运行测试并解析结果
echo "🏃 运行测试套件..."
TEST_OUTPUT=$(python -m pytest --tb=no --no-header -q 2>&1)
TEST_EXIT_CODE=$?

# 解析测试结果
if [ $TEST_EXIT_CODE -eq 0 ]; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -o '[0-9]* passed' | grep -o '[0-9]*')
    TOTAL_TIME=$(echo "$TEST_OUTPUT" | grep -o 'in [0-9]*\.[0-9]*s' | grep -o '[0-9]*\.[0-9]*')
    
    echo "✅ 测试状态：全部通过"
    echo "📊 测试统计："
    echo "   通过：$PASSED"
    echo "   失败：0"
    echo "   错误：0"
    echo "   通过率：100%"
    echo "   执行时间：${TOTAL_TIME}s"
else
    # 解析失败结果
    FAILED=$(echo "$TEST_OUTPUT" | grep -o '[0-9]* failed' | grep -o '[0-9]*' | head -1)
    PASSED=$(echo "$TEST_OUTPUT" | grep -o '[0-9]* passed' | grep -o '[0-9]*' | head -1)
    ERROR=$(echo "$TEST_OUTPUT" | grep -o '[0-9]* error' | grep -o '[0-9]*' | head -1)
    
    # 处理空值
    FAILED=${FAILED:-0}
    PASSED=${PASSED:-0}
    ERROR=${ERROR:-0}
    
    TOTAL=$((PASSED + FAILED + ERROR))
    if [ $TOTAL -gt 0 ]; then
        PASS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc -l)
    else
        PASS_RATE=0
    fi
    
    echo "❌ 测试状态：有失败"
    echo "📊 测试统计："
    echo "   通过：$PASSED"
    echo "   失败：$FAILED"
    echo "   错误：$ERROR"
    echo "   通过率：${PASS_RATE}%"
fi

echo ""
echo "📁 测试文件结构："
echo "   tests/test_database.py    - 数据库测试"
echo "   tests/test_api.py         - API测试"
echo "   tests/test_security.py    - 安全测试"
echo "   tests/test_performance.py - 性能测试"
echo "   tests/test_edge_cases.py  - 边界测试"

echo ""
echo "🔧 快速命令："
echo "   ./run_tests.sh           - 运行所有测试"
echo "   ./test_dashboard.sh      - 查看此仪表板"
echo "   pytest tests/ -v         - 详细测试输出"
echo "   pytest --lf              - 只运行失败的测试"

echo ""
echo "📋 报告文件："
echo "   TEST_SUMMARY_UPDATED.md  - 最新测试摘要"
echo "   TEST_FIXES_REPORT.md     - 修复报告"
echo "   TESTING_GUIDE.md         - 测试指南"

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 状态：测试套件健康 ✅"
else
    echo "⚠️  状态：需要修复失败的测试 ❌"
fi

echo "=================================="
echo "最后更新：$(date)"
