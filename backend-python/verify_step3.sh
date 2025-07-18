#!/bin/bash

# 第3步增强测试覆盖验证脚本
# 验证所有新增的测试和覆盖率

echo "🔍 第3步增强测试覆盖验证开始..."
echo "================================================"

# 设置工作目录
cd "$(dirname "$0")"

# 1. 运行新增的测试套件
echo "🧪 1. 运行生产环境模拟测试"
python3 -m pytest tests/test_production_simulation.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "  ✅ 生产环境模拟测试通过"
else
    echo "  ❌ 生产环境模拟测试失败"
fi

echo ""
echo "🔄 2. 运行端到端测试"
python3 -m pytest tests/test_e2e.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "  ✅ 端到端测试通过"
else
    echo "  ❌ 端到端测试失败"
fi

echo ""
echo "🚀 3. 运行部署验证测试"
python3 -m pytest tests/test_deployment_validation.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "  ✅ 部署验证测试通过"
else
    echo "  ❌ 部署验证测试失败"
fi

echo ""
echo "📊 4. 运行测试覆盖率分析"
if command -v pytest-cov &> /dev/null; then
    python3 -m pytest --cov=app --cov-report=term-missing tests/ -q
    echo "  📈 测试覆盖率报告已生成"
else
    echo "  ⚠️  pytest-cov未安装，跳过覆盖率分析"
    echo "  💡 提示：pip install pytest-cov"
fi

echo ""
echo "🔥 5. 运行压力测试"
echo "测试并发请求处理能力..."
python3 -c "
import requests
import threading
import time
import subprocess
import os

# 启动应用
proc = subprocess.Popen(['python3', 'app.py'], env={**os.environ, 'PORT': '5005'})
time.sleep(3)

try:
    # 并发测试
    results = []
    errors = []
    
    def make_request(i):
        try:
            response = requests.get('http://localhost:5005/health', timeout=5)
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))
    
    # 创建20个并发请求
    threads = []
    start_time = time.time()
    
    for i in range(20):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f'  📊 20个并发请求完成时间: {total_time:.2f}秒')
    print(f'  ✅ 成功请求: {len([r for r in results if r == 200])}/20')
    print(f'  ❌ 失败请求: {len(errors)}')
    
    if len(errors) == 0 and len([r for r in results if r == 200]) >= 18:
        print('  🎉 并发测试通过')
    else:
        print('  ⚠️  并发测试有问题')
        
finally:
    proc.terminate()
    proc.wait()
" 2>/dev/null || echo "  ⚠️  压力测试需要requests库: pip install requests"

echo ""
echo "🛡️  6. 安全配置检查"
echo "检查敏感信息泄露..."

# 检查是否有硬编码的密钥
if grep -r "secret_key\|password\|token" app.py | grep -v "getenv\|config\|test\|example" | grep -v "#" > /dev/null; then
    echo "  ⚠️  发现可能的硬编码敏感信息"
    grep -r "secret_key\|password\|token" app.py | grep -v "getenv\|config\|test\|example" | grep -v "#"
else
    echo "  ✅ 未发现硬编码敏感信息"
fi

# 检查环境变量使用
env_var_count=$(grep -c "os.getenv\|os.environ" app.py)
echo "  📋 环境变量使用次数: $env_var_count"

if [ "$env_var_count" -gt 5 ]; then
    echo "  ✅ 良好的环境变量使用模式"
else
    echo "  ⚠️  环境变量使用较少，可能需要更多配置化"
fi

echo ""
echo "📋 7. 代码质量检查"

# 检查代码行数和复杂度
total_lines=$(wc -l < app.py)
echo "  📏 主应用代码行数: $total_lines"

if [ "$total_lines" -lt 1000 ]; then
    echo "  ✅ 代码长度合理"
else
    echo "  ⚠️  代码较长，考虑模块化"
fi

# 检查函数数量
function_count=$(grep -c "^def " app.py)
echo "  🔧 函数数量: $function_count"

# 检查路由数量
route_count=$(grep -c "@app.route" app.py)
echo "  🛣️  路由数量: $route_count"

echo ""
echo "🔍 8. 依赖安全检查"
echo "检查已知漏洞..."

if command -v safety &> /dev/null; then
    safety check --json > safety_report.json 2>/dev/null || true
    if [ -f "safety_report.json" ]; then
        vulnerability_count=$(python3 -c "
import json
try:
    with open('safety_report.json', 'r') as f:
        data = json.load(f)
    print(len(data))
except:
    print(0)
")
        if [ "$vulnerability_count" -eq 0 ]; then
            echo "  ✅ 未发现已知安全漏洞"
        else
            echo "  ⚠️  发现 $vulnerability_count 个潜在安全问题"
        fi
        rm -f safety_report.json
    else
        echo "  ✅ 安全检查完成"
    fi
else
    echo "  💡 提示：安装safety进行依赖安全检查: pip install safety"
fi

echo ""
echo "📈 9. 性能基准测试"
echo "测试关键端点响应时间..."

python3 -c "
import time
import subprocess
import os
import requests

# 启动应用
proc = subprocess.Popen(['python3', 'app.py'], env={**os.environ, 'PORT': '5006'})
time.sleep(3)

try:
    endpoints = ['/health', '/health/detailed', '/status', '/version']
    for endpoint in endpoints:
        start_time = time.time()
        try:
            response = requests.get(f'http://localhost:5006{endpoint}', timeout=5)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            status = '✅' if response_time < 500 else '⚠️'
            print(f'  {status} {endpoint}: {response_time:.1f}ms')
        except Exception as e:
            print(f'  ❌ {endpoint}: 请求失败')
            
finally:
    proc.terminate()
    proc.wait()
" 2>/dev/null || echo "  ⚠️  性能测试需要requests库"

echo ""
echo "🏁 10. 全面测试运行"
echo "运行完整测试套件..."

# 运行所有测试并统计
total_tests=$(python3 -m pytest --collect-only -q tests/ 2>/dev/null | grep "test" | wc -l)
echo "  📊 总测试数量: $total_tests"

# 快速测试运行
python3 -m pytest tests/ -x --tb=no -q > test_summary.txt 2>&1
if [ $? -eq 0 ]; then
    passed_tests=$(grep "passed" test_summary.txt | tail -1 | grep -o '[0-9]* passed' | grep -o '[0-9]*')
    echo "  ✅ 通过测试: $passed_tests/$total_tests"
    echo "  🎉 所有测试通过！"
else
    failed_info=$(grep "FAILED\|ERROR" test_summary.txt | head -3)
    echo "  ❌ 部分测试失败："
    echo "$failed_info"
fi

rm -f test_summary.txt

echo ""
echo "================================================"
echo "🎯 第3步增强测试覆盖验证完成！"

# 总结报告
echo ""
echo "📋 验证总结:"
echo "  🧪 生产环境模拟 - 测试Render部署场景"
echo "  🔄 端到端测试 - 验证完整用户流程"  
echo "  🚀 部署验证 - 确保部署就绪性"
echo "  📊 测试覆盖率 - 代码质量保证"
echo "  🔥 压力测试 - 并发处理能力"
echo "  🛡️  安全检查 - 配置安全性"
echo "  📈 性能基准 - 响应时间验证"
