#!/bin/bash
# GPU API系统测试运行脚本

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
print_info "检查测试依赖..."
pip install -q pytest pytest-cov pytest-mock pytest-asyncio 2>/dev/null || true

# 创建测试报告目录
mkdir -p test_reports/{coverage,performance,integration}

# 解析命令行参数
TEST_TYPE=${1:-all}  # 默认运行所有测试

case "$TEST_TYPE" in
    unit)
        print_info "运行单元测试..."
        pytest tests/unit/ \
            -v \
            --cov=services \
            --cov=utils \
            --cov-report=html:test_reports/coverage/unit \
            --cov-report=term-missing \
            --junit-xml=test_reports/unit_tests.xml
        ;;

    integration)
        print_info "运行集成测试..."
        pytest tests/integration/ \
            -v \
            -m integration \
            --junit-xml=test_reports/integration_tests.xml
        ;;

    performance)
        print_info "运行性能测试..."
        pytest tests/performance/ \
            -v \
            -m performance \
            --junit-xml=test_reports/performance_tests.xml \
            > test_reports/performance/performance_results.txt
        ;;

    gpu)
        print_info "运行GPU相关测试..."
        pytest tests/ \
            -v \
            -m gpu \
            --junit-xml=test_reports/gpu_tests.xml
        ;;

    quick)
        print_info "运行快速测试（不包括慢速测试）..."
        pytest tests/unit/ \
            -v \
            -m "not slow" \
            --maxfail=5 \
            --junit-xml=test_reports/quick_tests.xml
        ;;

    coverage)
        print_info "生成完整测试覆盖率报告..."
        pytest tests/ \
            -v \
            --cov=services \
            --cov=utils \
            --cov=config \
            --cov-report=html:test_reports/coverage/full \
            --cov-report=term-missing \
            --cov-report=xml:test_reports/coverage/coverage.xml \
            --junit-xml=test_reports/all_tests.xml

        print_info "覆盖率报告已生成: test_reports/coverage/full/index.html"
        ;;

    all)
        print_info "运行所有测试..."

        # 单元测试
        print_info "1/3 运行单元测试..."
        pytest tests/unit/ \
            -v \
            --cov=services \
            --cov=utils \
            --cov-report=html:test_reports/coverage/unit \
            --junit-xml=test_reports/unit_tests.xml || true

        # 集成测试
        print_info "2/3 运行集成测试..."
        pytest tests/integration/ \
            -v \
            -m integration \
            --junit-xml=test_reports/integration_tests.xml || true

        # 性能测试
        print_info "3/3 运行性能测试..."
        pytest tests/performance/ \
            -v \
            -m performance \
            --junit-xml=test_reports/performance_tests.xml \
            > test_reports/performance/performance_results.txt || true

        # 生成总体覆盖率报告
        print_info "生成总体覆盖率报告..."
        pytest tests/ \
            --cov=services \
            --cov=utils \
            --cov-report=html:test_reports/coverage/full \
            --cov-report=term-missing \
            --cov-report=xml:test_reports/coverage/coverage.xml \
            --junit-xml=test_reports/all_tests.xml || true
        ;;

    *)
        print_error "未知的测试类型: $TEST_TYPE"
        echo "用法: $0 [unit|integration|performance|gpu|quick|coverage|all]"
        exit 1
        ;;
esac

# 检查测试结果
if [ $? -eq 0 ]; then
    print_info "✓ 测试完成"
else
    print_warning "⚠ 部分测试失败，请查看报告"
fi

# 显示覆盖率摘要
if [ -f "test_reports/coverage/coverage.xml" ] || [ -f "test_reports/coverage/full/index.html" ]; then
    print_info "测试报告位置:"
    echo "  - 覆盖率报告: test_reports/coverage/full/index.html"
    echo "  - XML报告: test_reports/coverage/coverage.xml"
    echo "  - JUnit报告: test_reports/*.xml"
fi

print_info "测试运行完成！"
