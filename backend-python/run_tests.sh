#!/bin/bash

# 测试运行脚本
# 用于运行不同类型的测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all         运行所有测试"
    echo "  unit        运行单元测试"
    echo "  integration 运行集成测试"
    echo "  security    运行安全性测试"
    echo "  performance 运行性能测试"
    echo "  coverage    运行测试并生成覆盖率报告"
    echo "  quick       运行快速测试（排除慢速测试）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 all                 # 运行所有测试"
    echo "  $0 unit                # 只运行单元测试"
    echo "  $0 coverage            # 运行测试并生成覆盖率报告"
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}检查测试依赖...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 python3${NC}"
        exit 1
    fi
    
    if ! python3 -c "import pytest" &> /dev/null; then
        echo -e "${RED}错误: 未找到 pytest，请运行 pip install pytest${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}依赖检查完成${NC}"
}

# 运行所有测试
run_all_tests() {
    echo -e "${BLUE}运行所有测试...${NC}"
    python3 -m pytest -v
}

# 运行单元测试
run_unit_tests() {
    echo -e "${BLUE}运行单元测试...${NC}"
    python3 -m pytest tests/test_database.py -v
}

# 运行集成测试
run_integration_tests() {
    echo -e "${BLUE}运行集成测试...${NC}"
    python3 -m pytest tests/test_api.py::TestIntegration -v
}

# 运行安全性测试
run_security_tests() {
    echo -e "${BLUE}运行安全性测试...${NC}"
    python3 -m pytest tests/test_security.py -v
}

# 运行性能测试
run_performance_tests() {
    echo -e "${BLUE}运行性能测试...${NC}"
    python3 -m pytest tests/test_performance.py -v
}

# 运行覆盖率测试
run_coverage_tests() {
    echo -e "${BLUE}运行覆盖率测试...${NC}"
    python3 -m pytest --cov=app --cov=database --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}覆盖率报告已生成到 htmlcov/ 目录${NC}"
}

# 运行快速测试
run_quick_tests() {
    echo -e "${BLUE}运行快速测试...${NC}"
    python3 -m pytest -v -m "not slow"
}

# 清理测试文件
cleanup() {
    echo -e "${BLUE}清理测试文件...${NC}"
    rm -f test_*.db
    rm -rf __pycache__
    rm -rf tests/__pycache__
    rm -rf .pytest_cache
    echo -e "${GREEN}清理完成${NC}"
}

# 主函数
main() {
    case "${1:-all}" in
        all)
            check_dependencies
            run_all_tests
            ;;
        unit)
            check_dependencies
            run_unit_tests
            ;;
        integration)
            check_dependencies
            run_integration_tests
            ;;
        security)
            check_dependencies
            run_security_tests
            ;;
        performance)
            check_dependencies
            run_performance_tests
            ;;
        coverage)
            check_dependencies
            run_coverage_tests
            ;;
        quick)
            check_dependencies
            run_quick_tests
            ;;
        clean)
            cleanup
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知选项 '$1'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'echo -e "${RED}测试运行中断${NC}"; cleanup; exit 1' INT TERM

# 运行主函数
main "$@"

echo -e "${GREEN}测试完成！${NC}"
