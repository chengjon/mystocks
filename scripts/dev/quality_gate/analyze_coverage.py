#!/usr/bin/env python3
"""
测试覆盖率分析脚本
- 分析当前测试覆盖率
- 识别低覆盖率模块
- 生成改进建议
"""
import os
import sys
import json
from pathlib import Path
from collections import defaultdict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def analyze_module_structure():
    """分析src目录模块结构"""
    src_path = project_root / "src"
    modules = defaultdict(dict)

    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(src_path)

                # 计算代码行数
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

                # 模块分类
                parts = str(rel_path).split('/')
                if len(parts) >= 2:
                    module_type = parts[0]
                    module_name = str(rel_path.with_suffix(''))

                    modules[module_type][module_name] = {
                        'path': str(rel_path),
                        'code_lines': code_lines,
                        'test_file': None
                    }

    return modules

def find_test_files():
    """查找测试文件"""
    tests_path = project_root / "tests"
    test_files = {}

    for root, dirs, files in os.walk(tests_path):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = Path(root) / file
                test_files[file] = str(file_path.relative_to(tests_path))

    return test_files

def match_tests_to_modules(modules, test_files):
    """匹配测试文件到模块"""
    for test_file, test_path in test_files.items():
        # 从测试文件名推断被测试的模块
        module_name = test_file.replace('test_', '').replace('.py', '')

        # 查找对应的源代码模块
        for module_type, module_dict in modules.items():
            for mod_name, mod_info in module_dict.items():
                if module_name in mod_name or mod_name.endswith(module_name):
                    mod_info['test_file'] = test_path
                    break

def calculate_priority_score(module_info):
    """计算改进优先级分数
    分数越高，越需要优先改进
    """
    score = 0

    # 1. 代码行数（大型模块优先）
    code_lines = module_info['code_lines']
    if code_lines > 1000:
        score += 50
    elif code_lines > 500:
        score += 30
    elif code_lines > 200:
        score += 10

    # 2. 是否有测试（没有测试的优先）
    if not module_info['test_file']:
        score += 40

    # 3. 模块类型（核心模块优先）
    module_path = module_info['path']
    if module_path.startswith('core/'):
        score += 30
    elif module_path.startswith('data_access/'):
        score += 25
    elif module_path.startswith('adapters/'):
        score += 20

    return score

def generate_coverage_report():
    """生成覆盖率分析报告"""
    print("=" * 80)
    print("MyStocks 测试覆盖率分析报告")
    print("=" * 80)
    print()

    # 1. 分析模块结构
    print("1. 分析源代码模块结构...")
    modules = analyze_module_structure()
    print(f"   找到 {sum(len(m) for m in modules.values())} 个源代码模块")

    # 2. 查找测试文件
    print("\n2. 查找测试文件...")
    test_files = find_test_files()
    print(f"   找到 {len(test_files)} 个测试文件")

    # 3. 匹配测试到模块
    print("\n3. 匹配测试文件到源代码模块...")
    match_tests_to_modules(modules, test_files)

    # 4. 统计覆盖率
    print("\n4. 统计测试覆盖率...")
    total_modules = sum(len(m) for m in modules.values())
    tested_modules = sum(
        1 for module_dict in modules.values()
        for mod_info in module_dict.values()
        if mod_info['test_file']
    )

    coverage_rate = (tested_modules / total_modules * 100) if total_modules > 0 else 0
    print(f"   总模块数: {total_modules}")
    print(f"   已测试模块: {tested_modules}")
    print(f"   测试覆盖率: {coverage_rate:.1f}%")

    # 5. 按模块类型分组统计
    print("\n5. 按模块类型统计:")
    for module_type, module_dict in sorted(modules.items()):
        total = len(module_dict)
        tested = sum(1 for m in module_dict.values() if m['test_file'])
        rate = (tested / total * 100) if total > 0 else 0
        print(f"   {module_type:20s}: {tested:3d}/{total:3d} ({rate:5.1f}%)")

    # 6. 识别优先改进模块
    print("\n6. 优先改进模块 (Top 20):")
    print("   " + "-" * 76)
    print(f"   {'优先级':<6} {'模块路径':<50} {'行数':<8} {'测试':<6}")
    print("   " + "-" * 76)

    all_modules = []
    for module_type, module_dict in modules.items():
        for mod_name, mod_info in module_dict.items():
            priority = calculate_priority_score(mod_info)
            all_modules.append({
                'type': module_type,
                'name': mod_name,
                'path': mod_info['path'],
                'lines': mod_info['code_lines'],
                'has_test': '✓' if mod_info['test_file'] else '✗',
                'priority': priority,
                'test_file': mod_info['test_file']
            })

    # 按优先级排序
    all_modules.sort(key=lambda x: x['priority'], reverse=True)

    for i, mod in enumerate(all_modules[:20], 1):
        print(f"   {i:2d}. ({mod['priority']:3d}) {mod['path']:<50} {mod['lines']:>6}  {mod['has_test']}")

    # 7. 生成详细报告文件
    print("\n7. 生成详细报告...")
    report = {
        'summary': {
            'total_modules': total_modules,
            'tested_modules': tested_modules,
            'coverage_rate': round(coverage_rate, 2),
            'total_test_files': len(test_files)
        },
        'by_type': {
            module_type: {
                'total': len(module_dict),
                'tested': sum(1 for m in module_dict.values() if m['test_file']),
                'coverage_rate': round(
                    (sum(1 for m in module_dict.values() if m['test_file']) / len(module_dict) * 100)
                    if len(module_dict) > 0 else 0, 2
                )
            }
            for module_type, module_dict in modules.items()
        },
        'priority_modules': all_modules[:20]
    }

    report_path = project_root / "docs" / "reports" / "test_coverage_analysis.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"   详细报告已保存到: {report_path}")

    # 8. 生成改进建议
    print("\n8. 改进建议:")
    print("\n   Phase 1: 修复测试基础设施 (1-2天)")
    print("   - 修复所有测试导入错误 (src模块导入)")
    print("   - 配置正确的PYTHONPATH")
    print("   - 运行完整测试套件验证")
    print("\n   Phase 2: 核心模块测试覆盖 (3-5天)")
    print("   - data_access层: PostgreSQL 67% → 90%+")
    print("   - data_access层: TDengine 56% → 90%+")
    print("   - core层: data_manager.py, unified_manager.py")
    print("\n   Phase 3: 大型模块TDD (5-7天)")
    print("   - database_service.py (1,454行) → 80%+")
    print("   - tdx_adapter.py (1,305行) → 80%+")
    print("\n   Phase 4: 适配器层完善 (3-4天)")
    print("   - 为所有7个适配器补充完整测试")
    print("   - 目标: 100%适配器覆盖")

    print("\n" + "=" * 80)
    print(f"分析完成! 当前整体覆盖率约 {coverage_rate:.1f}%，目标 80%")
    print(f"需要补充测试的模块: {total_modules - tested_modules} 个")
    print("=" * 80)

    return report

if __name__ == '__main__':
    try:
        report = generate_coverage_report()
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
