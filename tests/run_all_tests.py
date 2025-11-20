"""
MyStocks项目综合测试套件
统一运行所有单元测试，生成覆盖率报告

使用方法:
    python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
    python run_all_tests.py
"""

import pytest
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
TEST_CONFIG = {
    'verbose': True,
    'tb': 'short',  # 简短的错误回溯
    'strict_markers': True,
    'strict_config': True,
    'cov_enabled': True,
    'cov_source': 'src',
    'cov_report': ['term', 'html', 'xml'],
    'cov_fail_under': 30,  # 最低覆盖率要求30%
    'markers': [
        'unit: 单元测试',
        'integration: 集成测试',
        'e2e: 端到端测试',
        'slow: 慢速测试',
        'api: API测试',
        'database: 数据库测试',
        'adapter: 适配器测试'
    ]
}


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("🚀 开始运行MyStocks单元测试套件")
    print("=" * 60)
    
    # 构建pytest命令
    cmd = [
        'python', '-m', 'pytest',
        'tests/',  # 测试目录
        '-v',      # 详细输出
        '--tb=short',  # 简短回溯
        '--strict-markers',
        '--strict-config',
        f'--cov={TEST_CONFIG["cov_source"]}',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--cov-report=xml:coverage.xml',
        f'--cov-fail-under={TEST_CONFIG["cov_fail_under"]}',
        '--durations=10',  # 显示最慢的10个测试
        '--maxfail=5',     # 最多允许5个失败
        '-m', 'unit or integration or e2e',  # 运行所有标记的测试
    ]
    
    try:
        # 运行测试
        result = subprocess.run(cmd, check=False, capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ 所有测试通过!")
            generate_test_summary()
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            print("请查看上面的错误信息进行调试")
            
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 运行测试时发生错误: {e}")
        return 1


def generate_test_summary():
    """生成测试摘要报告"""
    print("\n" + "=" * 60)
    print("📊 测试执行摘要")
    print("=" * 60)
    
    # 检查测试结果文件
    test_results_file = Path("test-results/.last-run.json")
    if test_results_file.exists():
        print("📁 测试结果文件: test-results/.last-run.json")
    
    # 检查覆盖率报告
    html_coverage = Path("htmlcov/index.html")
    if html_coverage.exists():
        print("📊 HTML覆盖率报告: htmlcov/index.html")
    
    # 检查覆盖率XML
    xml_coverage = Path("coverage.xml")
    if xml_coverage.exists():
        print("📊 XML覆盖率报告: coverage.xml")
    
    print("\n🎯 建议:")
    print("1. 查看HTML覆盖率报告了解覆盖率详情")
    print("2. 关注失败的测试并尽快修复")
    print("3. 逐步提高测试覆盖率目标")
    print("4. 将测试集成到CI/CD流程中")


def run_specific_test_category(category):
    """运行特定类别的测试"""
    marker_mapping = {
        'unit': 'unit',
        'adapter': 'unit and adapter',
        'integration': 'integration',
        'e2e': 'e2e',
        'slow': 'slow'
    }
    
    marker = marker_mapping.get(category, 'unit')
    print(f"🎯 运行 {category} 测试 (标记: {marker})")
    
    cmd = [
        'python', '-m', 'pytest',
        'tests/',
        '-v',
        '-m', marker
    ]
    
    return subprocess.run(cmd)


def show_test_statistics():
    """显示测试统计信息"""
    print("📊 MyStocks项目测试统计")
    print("=" * 60)
    
    # 统计测试文件
    test_files = list(Path("tests").rglob("test_*.py"))
    print(f"📁 测试文件数量: {len(test_files)}")
    
    # 统计测试用例
    test_cases = 0
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单计算测试函数数量
                test_functions = content.count('def test_')
                test_cases += test_functions
        except Exception:
            continue
    
    print(f"🧪 测试用例数量: {test_cases}")
    
    # 按模块统计
    modules = {}
    for file_path in test_files:
        module_name = file_path.parent.name
        modules[module_name] = modules.get(module_name, 0) + 1
    
    print("\n📋 按模块统计:")
    for module, count in sorted(modules.items()):
        print(f"  {module}: {count} 个测试文件")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MyStocks测试运行器')
    parser.add_argument('--category', choices=['unit', 'adapter', 'integration', 'e2e', 'slow'], 
                       help='运行特定类别的测试')
    parser.add_argument('--stats', action='store_true', help='显示测试统计信息')
    parser.add_argument('--coverage', action='store_true', help='只生成覆盖率报告')
    parser.add_argument('--install-deps', action='store_true', help='安装测试依赖')
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("📦 安装测试依赖...")
        subprocess.run(['pip', 'install', 'pytest-cov', 'pytest-html', 'pytest-xdist'])
        print("✅ 依赖安装完成")
        return
    
    if args.stats:
        show_test_statistics()
        return
    
    if args.category:
        result = run_specific_test_category(args.category)
        sys.exit(result.returncode)
    
    if args.coverage:
        cmd = [
            'python', '-m', 'pytest',
            'tests/', 
            f'--cov={TEST_CONFIG["cov_source"]}',
            '--cov-report=html:htmlcov',
            '--cov-report=term'
        ]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    
    # 默认运行所有测试
    exit_code = run_tests_with_coverage()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()