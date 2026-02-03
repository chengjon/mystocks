#!/usr/bin/env python3
"""
批量修复测试文件导入路径

将旧的导入路径转换为新的标准导入路径：
- from core.xxx → from src.core.xxx
- from adapters.xxx → from src.adapters.xxx
- from db_manager.xxx → from src.db_manager.xxx
- from monitoring.xxx → from src.monitoring.xxx
- from interfaces.xxx → from src.interfaces.xxx
- from storage.xxx → from src.storage.xxx
- from utils.xxx → from src.utils.xxx

用法:
    python scripts/quality_gate/fix_test_imports.py --dry-run  # 预览
    python scripts/quality_gate/fix_test_imports.py           # 执行
    python scripts/quality_gate/fix_test_imports.py --verify  # 验证
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入路径映射规则
IMPORT_MAPPINGS = {
    'from core.': 'from src.core.',
    'from adapters.': 'from src.adapters.',
    'from db_manager.': 'from src.db_manager.',
    'from monitoring.': 'from src.monitoring.',
    'from interfaces.': 'from src.interfaces.',
    'from storage.': 'from src.storage.',
    'from utils.': 'from src.utils.',
    'from data_sources.': 'from src.data_sources.',
    'from gpu.': 'from src.gpu.',
    'from ml_strategy.': 'from src.ml_strategy.',
    'from contract_testing.': 'from src.contract_testing.',
    'from routes.': 'from src.routes.',
    'from api.': 'from src.api.',
    'from backup_recovery.': 'from src.backup_recovery.',
    'from cron.': 'from src.cron.',
    'from database.': 'from src.database.',
    'from database_optimization.': 'from src.database_optimization.',
    'from factories.': 'from src.factories.',
    'from mock.': 'from src.mock.',
    'from reporting.': 'from src.reporting.',
}

# 排除的目录
EXCLUDE_DIRS = {
    '__pycache__',
    '.pytest_cache',
    '.git',
    'venv',
    'env',
    '.venv',
    'virtualenv',
    'htmlcov',
    'dist',
    'build',
    '*.egg-info',
}

# 排除的文件
EXCLUDE_FILES = {
    '__init__.py',
    'conftest.py',
}


def should_exclude_file(file_path: Path) -> bool:
    """检查文件是否应该被排除"""
    if file_path.name in EXCLUDE_FILES:
        return True

    # 检查是否在排除的目录中
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return True

    return False


def find_test_files(tests_dir: Path) -> list[Path]:
    """查找所有测试文件"""
    test_files = []

    for test_file in tests_dir.rglob('test_*.py'):
        if not should_exclude_file(test_file):
            test_files.append(test_file)

    for test_file in tests_dir.rglob('*_test.py'):
        if not should_exclude_file(test_file):
            test_files.append(test_file)

    return sorted(test_files)


def analyze_imports(file_path: Path) -> dict:
    """分析文件中的导入语句"""
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    imports_found = {}
    for i, line in enumerate(lines, 1):
        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            if old_pattern in line:
                if i not in imports_found:
                    imports_found[i] = []
                imports_found[i].append({
                    'line': line.strip(),
                    'old_pattern': old_pattern,
                    'new_pattern': new_pattern,
                })

    return imports_found


def fix_imports(file_path: Path, dry_run: bool = False) -> dict:
    """修复文件中的导入路径"""
    result = {
        'file': str(file_path.relative_to(project_root)),
        'changes': [],
        'status': 'skipped',
    }

    content = file_path.read_text(encoding='utf-8')
    original_content = content
    lines = content.split('\n')

    for i, line in enumerate(lines):
        modified = False
        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            if old_pattern in line:
                # 替换导入
                new_line = line.replace(old_pattern, new_pattern)
                if new_line != line:
                    lines[i] = new_line
                    result['changes'].append({
                        'line_no': i + 1,
                        'old': line.strip(),
                        'new': new_line.strip(),
                    })
                    modified = True

        # 特殊处理: import xxx (不是 from import)
        if not modified:
            for module in ['core', 'adapters', 'db_manager', 'monitoring', 'interfaces',
                          'storage', 'utils', 'data_sources', 'gpu']:
                pattern = f'import {module}.'
                if pattern in line and 'import src.' not in line:
                    new_line = line.replace(pattern, f'import src.{module}.')
                    lines[i] = new_line
                    result['changes'].append({
                        'line_no': i + 1,
                        'old': line.strip(),
                        'new': new_line.strip(),
                    })

    if result['changes']:
        if dry_run:
            result['status'] = 'dry_run'
        else:
            new_content = '\n'.join(lines)
            file_path.write_text(new_content, encoding='utf-8')
            result['status'] = 'fixed'

    return result


def main():
    parser = argparse.ArgumentParser(
        description='批量修复测试文件导入路径',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s --dry-run    # 预览将要修复的文件
  %(prog)s              # 执行修复
  %(prog)s --verify     # 验证修复结果
  %(prog)s --report     # 生成详细报告
        '''
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际修改文件'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='验证模式，检查是否还有未修复的导入'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='生成详细报告并保存到文件'
    )

    parser.add_argument(
        '--tests-dir',
        type=Path,
        default=project_root / 'tests',
        help='测试文件目录 (默认: tests/)'
    )

    args = parser.parse_args()

    # 查找所有测试文件
    print("=" * 80)
    print("测试文件导入路径修复工具")
    print("=" * 80)
    print()

    print(f"扫描目录: {args.tests_dir}")
    test_files = find_test_files(args.tests_dir)
    print(f"找到测试文件: {len(test_files)} 个")
    print()

    # 分析模式
    if args.verify:
        print("验证模式: 检查未修复的导入路径")
        print("-" * 80)

        files_with_issues = []
        for test_file in test_files:
            imports = analyze_imports(test_file)
            if imports:
                files_with_issues.append({
                    'file': test_file,
                    'imports': imports,
                })

        if files_with_issues:
            print(f"\n发现 {len(files_with_issues)} 个文件仍有未修复的导入:\n")
            for item in files_with_issues[:20]:  # 只显示前20个
                rel_path = item['file'].relative_to(project_root)
                print(f"  {rel_path}")
                for line_no, imports_list in item['imports'].items():
                    for imp in imports_list:
                        print(f"    行 {line_no}: {imp['line'][:80]}")
            print()

            if len(files_with_issues) > 20:
                print(f"  ... 还有 {len(files_with_issues) - 20} 个文件未显示")
            print()

            sys.exit(1)
        else:
            print("✅ 所有测试文件的导入路径已正确!")
            sys.exit(0)

    # 修复模式
    elif args.dry_run:
        print("预览模式: 显示将要修复的文件")
        print("-" * 80)
        print()

        results = []
        for test_file in test_files:
            result = fix_imports(test_file, dry_run=True)
            if result['changes']:
                results.append(result)

        if results:
            print(f"将修复 {len(results)} 个文件:\n")
            for result in results[:10]:
                print(f"  {result['file']} ({len(result['changes'])} 处修改)")
            if len(results) > 10:
                print(f"  ... 还有 {len(results) - 10} 个文件")
            print()

            # 生成报告
            if args.report:
                report_path = project_root / 'docs' / 'reports' / 'test_import_fix_report.json'
                report_path.parent.mkdir(parents=True, exist_ok=True)

                import json
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'dry_run': True,
                    'total_files': len(test_files),
                    'files_to_fix': len(results),
                    'changes': results,
                }

                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)

                print(f"详细报告已保存: {report_path}")
        else:
            print("✅ 没有需要修复的文件!")

    else:
        print("执行模式: 开始修复导入路径")
        print("-" * 80)
        print()

        results = []
        fixed_count = 0
        skipped_count = 0

        for i, test_file in enumerate(test_files, 1):
            result = fix_imports(test_file, dry_run=False)
            results.append(result)

            if result['status'] == 'fixed':
                fixed_count += 1
                print(f"[{i}/{len(test_files)}] ✓ {result['file']} ({len(result['changes'])} 处修改)")
            elif result['status'] == 'skipped':
                skipped_count += 1

        print()
        print("=" * 80)
        print("修复完成!")
        print(f"  总文件数: {len(test_files)}")
        print(f"  已修复: {fixed_count}")
        print(f"  已跳过: {skipped_count}")
        print("=" * 80)
        print()

        # 生成报告
        if args.report:
            report_path = project_root / 'docs' / 'reports' / 'test_import_fix_report.json'
            report_path.parent.mkdir(parents=True, exist_ok=True)

            import json
            report = {
                'timestamp': datetime.now().isoformat(),
                'dry_run': False,
                'total_files': len(test_files),
                'fixed_files': fixed_count,
                'skipped_files': skipped_count,
                'results': results,
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"详细报告已保存: {report_path}")
            print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
