#!/usr/bin/env python3
"""
Pylint报告分析脚本
解析pylint-errors.json，生成优先级分析报告
"""

import json
import sys
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# 计算项目根目录（从scripts/tools/向上2级）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class PylintReportAnalyzer:
    """Pylint报告分析器"""

    # 错误类型优先级（数字越小优先级越高）
    TYPE_PRIORITY = {
        'error': 1,
        'warning': 2,
        'refactor': 3,
        'convention': 4,
        'fatal': 0
    }

    # 错误代码严重性映射
    SEVERITY_MAP = {
        'E': 'CRITICAL',  # Errors - 阻碍功能
        'W': 'HIGH',      # Warnings - 潜在bug
        'R': 'MEDIUM',    # Refactoring - 代码异味
        'C': 'LOW',       # Convention - 风格问题
        'F': 'CRITICAL'   # Fatal - 严重错误
    }

    def __init__(self, json_path: str):
        """初始化分析器

        Args:
            json_path: pylint-errors.json的路径
        """
        self.json_path = json_path
        self.errors: List[Dict[str, Any]] = []
        self.stats = {
            'total': 0,
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int),
            'by_module': defaultdict(int),
            'by_symbol': defaultdict(int),
            'by_message_id': defaultdict(int)
        }

    def load_report(self) -> bool:
        """加载JSON报告

        Returns:
            是否成功加载
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.errors = json.load(f)
            print(f"✅ 成功加载 {len(self.errors)} 个错误/警告/建议")
            return True
        except FileNotFoundError:
            print(f"❌ 错误：找不到文件 {self.json_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 错误：JSON解析失败 - {e}")
            return False

    def analyze(self):
        """分析错误数据，生成统计信息"""
        print("\n📊 正在分析Pylint报告...")

        for error in self.errors:
            error_type = error.get('type', 'unknown')
            message_id = error.get('message-id', 'UNKNOWN')
            symbol = error.get('symbol', 'unknown')
            module = error.get('module', 'unknown')

            # 统计总数
            self.stats['total'] += 1

            # 按类型统计
            self.stats['by_type'][error_type] += 1

            # 按严重性统计（基于message-id前缀）
            severity = self.SEVERITY_MAP.get(message_id[0], 'UNKNOWN')
            self.stats['by_severity'][severity] += 1

            # 按模块统计
            self.stats['by_module'][module] += 1

            # 按符号统计
            self.stats['by_symbol'][symbol] += 1

            # 按消息ID统计
            self.stats['by_message_id'][message_id] += 1

        print(f"✅ 分析完成：共 {self.stats['total']} 个问题")

    def get_top_modules(self, limit: int = 20) -> List[tuple]:
        """获取错误最多的模块

        Args:
            limit: 返回数量限制

        Returns:
            (模块名, 错误数) 列表，按错误数降序
        """
        return sorted(
            self.stats['by_module'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    def get_top_symbols(self, limit: int = 30) -> List[tuple]:
        """获取最常见的错误符号

        Args:
            limit: 返回数量限制

        Returns:
            (符号名, 错误数) 列表，按错误数降序
        """
        return sorted(
            self.stats['by_symbol'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    def get_errors_by_module(self, module_name: str) -> List[Dict[str, Any]]:
        """获取指定模块的所有错误

        Args:
            module_name: 模块名

        Returns:
            该模块的所有错误列表
        """
        return [
            error for error in self.errors
            if error.get('module') == module_name
        ]

    def categorize_by_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        """按优先级分类错误

        Returns:
            优先级字典 {priority_level: [errors]}
        """
        categorized = {
            'P1_CRITICAL_ERRORS': [],      # E****错误
            'P2_HIGH_WARNINGS': [],        # W****警告
            'P3_MEDIUM_REFACTOR': [],      # R****重构
            'P4_LOW_CONVENTION': []        # C****规范
        }

        for error in self.errors:
            message_id = error.get('message-id', 'UNKNOWN')
            error_prefix = message_id[0] if message_id else 'X'

            if error_prefix == 'E' or error_prefix == 'F':
                categorized['P1_CRITICAL_ERRORS'].append(error)
            elif error_prefix == 'W':
                categorized['P2_HIGH_WARNINGS'].append(error)
            elif error_prefix == 'R':
                categorized['P3_MEDIUM_REFACTOR'].append(error)
            elif error_prefix == 'C':
                categorized['P4_LOW_CONVENTION'].append(error)

        return categorized

    def generate_markdown_report(self, output_path: str):
        """生成Markdown格式的分析报告

        Args:
            output_path: 输出文件路径
        """
        print(f"\n📝 正在生成Markdown报告...")

        # 按优先级分类
        categorized = self.categorize_by_priority()

        # 获取TOP模块
        top_modules = self.get_top_modules(20)

        # 获取TOP错误符号
        top_symbols = self.get_top_symbols(30)

        # 生成报告内容
        report = []
        report.append("# Pylint错误分析报告")
        report.append("")
        report.append(f"**生成时间**: {self._get_timestamp()}")
        report.append(f"**总问题数**: {self.stats['total']}")
        report.append("")

        # 1. 概览统计
        report.append("## 📊 概览统计")
        report.append("")
        report.append("### 按错误类型分类")
        report.append("")
        report.append("| 类型 | 数量 | 占比 | 说明 |")
        report.append("|------|------|------|------|")

        for error_type in ['error', 'warning', 'refactor', 'convention']:
            count = self.stats['by_type'].get(error_type, 0)
            percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0

            # 添加emoji和说明
            type_info = {
                'error': ('🔴', '阻碍功能的严重错误'),
                'warning': ('🟠', '潜在的bug和问题'),
                'refactor': ('🟡', '代码异味，需要重构'),
                'convention': ('🟢', '代码风格和规范问题')
            }
            emoji, desc = type_info.get(error_type, ('⚪', '未知'))

            report.append(f"| {emoji} {error_type.capitalize()} | {count} | {percentage:.1f}% | {desc} |")

        report.append("")

        # 2. 按严重性分类
        report.append("### 按严重性分类")
        report.append("")
        report.append("| 严重性 | 数量 | 占比 | 响应时间 |")
        report.append("|--------|------|------|----------|")

        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        response_time = {
            'CRITICAL': '立即修复',
            'HIGH': '4小时内',
            'MEDIUM': '24小时内',
            'LOW': '下迭代'
        }

        for severity in severity_order:
            count = self.stats['by_severity'].get(severity, 0)
            percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            response = response_time.get(severity, '待定')
            report.append(f"| {severity} | {count} | {percentage:.1f}% | {response} |")

        report.append("")

        # 3. TOP 20错误最多的模块
        report.append("## 🎯 错误最多的模块 (TOP 20)")
        report.append("")
        report.append("| 排名 | 模块 | 错误数 | 优先级 |")
        report.append("|------|------|--------|--------|")

        for idx, (module, count) in enumerate(top_modules, 1):
            # 根据错误数确定优先级
            if count >= 100:
                priority = "🔴 P1-极高"
            elif count >= 50:
                priority = "🟠 P2-高"
            elif count >= 20:
                priority = "🟡 P3-中"
            else:
                priority = "🟢 P4-低"

            # 简化模块名显示
            display_module = module.replace('mystocks_spec.', '')
            report.append(f"| {idx} | `{display_module}` | {count} | {priority} |")

        report.append("")

        # 4. TOP 30最常见的错误符号
        report.append("## 🔍 最常见的错误符号 (TOP 30)")
        report.append("")
        report.append("| 排名 | 错误符号 | 数量 | 类型 | 修复难度 |")
        report.append("|------|----------|------|------|----------|")

        for idx, (symbol, count) in enumerate(top_symbols, 1):
            # 根据符号判断类型和难度
            difficulty = self._estimate_fix_difficulty(symbol)
            error_type = self._get_error_category(symbol)

            report.append(f"| {idx} | `{symbol}` | {count} | {error_type} | {difficulty} |")

        report.append("")

        # 5. 优先级修复计划
        report.append("## 📋 优先级修复计划")
        report.append("")

        report.append("### P1 - Critical Errors (立即修复)")
        report.append("")
        p1_count = len(categorized['P1_CRITICAL_ERRORS'])
        report.append(f"**总数**: {p1_count}个")
        report.append("")

        if p1_count > 0:
            report.append("**主要错误类型**:")
            report.append("")
            p1_symbols = self._get_symbol_distribution(categorized['P1_CRITICAL_ERRORS'])
            for symbol, count in list(p1_symbols.items())[:10]:
                report.append(f"- `{symbol}`: {count}个")
            report.append("")

        report.append("### P2 - High Warnings (4小时内)")
        report.append("")
        p2_count = len(categorized['P2_HIGH_WARNINGS'])
        report.append(f"**总数**: {p2_count}个")
        report.append("")

        if p2_count > 0:
            report.append("**主要警告类型**:")
            report.append("")
            p2_symbols = self._get_symbol_distribution(categorized['P2_HIGH_WARNINGS'])
            for symbol, count in list(p2_symbols.items())[:10]:
                report.append(f"- `{symbol}`: {count}个")
            report.append("")

        report.append("### P3 - Medium Refactor (24小时内)")
        report.append("")
        p3_count = len(categorized['P3_MEDIUM_REFACTOR'])
        report.append(f"**总数**: {p3_count}个")
        report.append("")

        report.append("### P4 - Low Convention (下迭代)")
        report.append("")
        p4_count = len(categorized['P4_LOW_CONVENTION'])
        report.append(f"**总数**: {p4_count}个")
        report.append("")

        # 6. 推荐修复顺序
        report.append("## 🚀 推荐修复顺序")
        report.append("")
        report.append("基于错误数量、严重性和依赖关系，推荐按以下顺序修复：")
        report.append("")

        # 按模块错误数和优先级推荐
        report.append("### Phase 1: 核心模块Critical错误修复 (Week 7, Day 1-2)")
        report.append("")
        core_modules = [(m, c) for m, c in top_modules if 'src/core' in m or 'src.core' in m]
        if core_modules:
            for module, count in core_modules[:5]:
                display_module = module.replace('mystocks_spec.', '')
                report.append(f"- `{display_module}` ({count}个错误)")
        report.append("")

        report.append("### Phase 2: 数据访问层修复 (Week 7, Day 3-4)")
        report.append("")
        data_access_modules = [(m, c) for m, c in top_modules if 'data_access' in m]
        if data_access_modules:
            for module, count in data_access_modules[:5]:
                display_module = module.replace('mystocks_spec.', '')
                report.append(f"- `{display_module}` ({count}个错误)")
        report.append("")

        report.append("### Phase 3: 适配器修复 (Week 7, Day 5 - Week 8, Day 2)")
        report.append("")
        adapter_modules = [(m, c) for m, c in top_modules if 'adapter' in m or 'interfaces/adapters' in m]
        if adapter_modules:
            for module, count in adapter_modules[:8]:
                display_module = module.replace('mystocks_spec.', '')
                report.append(f"- `{display_module}` ({count}个错误)")
        report.append("")

        report.append("### Phase 4: API端点修复 (Week 8, Day 3-5)")
        report.append("")
        api_modules = [(m, c) for m, c in top_modules if 'web/backend/app/api' in m]
        if api_modules:
            for module, count in api_modules[:5]:
                display_module = module.replace('mystocks_spec.', '')
                report.append(f"- `{display_module}` ({count}个错误)")
        report.append("")

        # 7. 快速修复建议
        report.append("## ⚡ 快速修复建议")
        report.append("")
        report.append("以下错误类型可以批量快速修复：")
        report.append("")

        quick_fix_symbols = {
            'missing-docstring': '添加文档字符串（可自动化）',
            'line-too-long': '格式化长行（black自动处理）',
            'trailing-whitespace': '删除尾部空格（自动化）',
            'invalid-name': '重命名变量遵循规范',
            'unused-import': '删除未使用的导入（自动化）',
            'unused-variable': '删除或使用_前缀',
            'consider-using-f-string': '使用f-string替代format',
            'too-many-lines': '模块拆分（需手动）'
        }

        for symbol, suggestion in quick_fix_symbols.items():
            count = self.stats['by_symbol'].get(symbol, 0)
            if count > 0:
                report.append(f"- **`{symbol}`** ({count}个): {suggestion}")

        report.append("")

        # 8. 注意事项
        report.append("## ⚠️ 修复注意事项")
        report.append("")
        report.append("1. **最小修改原则**: 只修复类型错误，不改变业务逻辑")
        report.append("2. **测试驱动**: 每次修复后运行完整测试套件")
        report.append("3. **增量提交**: 每种错误类型一个提交")
        report.append("4. **回归预防**: 修复前后对比测试结果")
        report.append("5. **配置优先**: 优先通过配置抑制无意义的规范问题")
        report.append("")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        print(f"✅ 报告已保存到: {output_path}")

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _estimate_fix_difficulty(self, symbol: str) -> str:
        """估算修复难度

        Args:
            symbol: 错误符号

        Returns:
            难度等级字符串
        """
        easy_fixes = {
            'missing-docstring', 'line-too-long', 'trailing-whitespace',
            'invalid-name', 'unused-import', 'unused-variable',
            'consider-using-f-string', 'unnecessary-pass'
        }

        hard_fixes = {
            'too-many-arguments', 'too-many-locals', 'too-many-branches',
            'too-many-statements', 'too-complex', 'too-many-instance-attributes'
        }

        if symbol in easy_fixes:
            return "🟢 简单"
        elif symbol in hard_fixes:
            return "🔴 困难"
        else:
            return "🟡 中等"

    def _get_error_category(self, symbol: str) -> str:
        """获取错误分类

        Args:
            symbol: 错误符号

        Returns:
            分类字符串
        """
        categories = {
            'docstring': ['missing-docstring', 'missing-module-docstring'],
            'naming': ['invalid-name', 'bad-naming'],
            'formatting': ['line-too-long', 'trailing-whitespace', 'consider-using-f-string'],
            'imports': ['unused-import', 'import-error', 'wrong-import-order'],
            'complexity': ['too-many-arguments', 'too-many-locals', 'too-complex'],
            'unused': ['unused-variable', 'unused-argument'],
            'structure': ['too-many-lines', 'too-many-instance-attributes']
        }

        for category, symbols in categories.items():
            if symbol in symbols:
                return category.capitalize()

        return "Other"

    def _get_symbol_distribution(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取错误符号分布

        Args:
            errors: 错误列表

        Returns:
            符号分布字典
        """
        distribution = defaultdict(int)
        for error in errors:
            symbol = error.get('symbol', 'unknown')
            distribution[symbol] += 1

        # 按数量降序排序
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))


def main():
    """主函数"""
    # 确定报告路径
    json_path = os.path.join(project_root, 'docs/reports/pylint-errors.json')
    output_path = os.path.join(project_root, 'docs/reports/PYLINT_ERROR_ANALYSIS.md')

    print("=" * 60)
    print("Pylint报告分析工具")
    print("=" * 60)

    # 创建分析器
    analyzer = PylintReportAnalyzer(json_path)

    # 加载报告
    if not analyzer.load_report():
        sys.exit(1)

    # 分析数据
    analyzer.analyze()

    # 生成Markdown报告
    analyzer.generate_markdown_report(output_path)

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📄 查看详细报告: {output_path}")
    print(f"📊 总问题数: {analyzer.stats['total']}")
    print(f"🔴 Critical (E****): {analyzer.stats['by_severity']['CRITICAL']}")
    print(f"🟠 High (W****): {analyzer.stats['by_severity']['HIGH']}")
    print(f"🟡 Medium (R****): {analyzer.stats['by_severity']['MEDIUM']}")
    print(f"🟢 Low (C****): {analyzer.stats['by_severity']['LOW']}")
    print()


if __name__ == '__main__':
    main()
