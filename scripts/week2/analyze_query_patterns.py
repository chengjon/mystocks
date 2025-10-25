#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询模式分析脚本
分析应用的实际数据访问需求

用途: Week 2 Day 1 - 查询模式分析
输出: 控制台输出 + query_patterns_analysis.txt
"""

import os
import sys
import re
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime


class QueryPatternAnalyzer:
    """查询模式分析器"""

    def __init__(self):
        self.patterns = {
            "select": r'(SELECT\s+.*?FROM\s+\w+)',
            "insert": r'(INSERT\s+INTO\s+\w+)',
            "update": r'(UPDATE\s+\w+\s+SET)',
            "delete": r'(DELETE\s+FROM\s+\w+)',
            "create_table": r'(CREATE\s+TABLE\s+\w+)',
            "tdengine_stable": r'(CREATE\s+STABLE\s+\w+)',
            "redis_get": r'(redis\.get\(|client\.get\()',
            "redis_set": r'(redis\.set\(|client\.set\()',
            "redis_hget": r'(redis\.hget\(|client\.hget\()',
        }

        self.queries = defaultdict(list)
        self.table_access = Counter()
        self.file_stats = defaultdict(int)

    def analyze_file(self, file_path: Path):
        """分析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 查找各类查询
                for pattern_name, pattern in self.patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                    if matches:
                        for match in matches:
                            # 清理匹配结果
                            clean_match = ' '.join(match.split())[:200]  # 限制长度
                            self.queries[pattern_name].append({
                                "file": str(file_path),
                                "query": clean_match
                            })
                            self.file_stats[str(file_path)] += 1

                # 提取表名
                from_matches = re.findall(r'FROM\s+`?(\w+)`?', content, re.IGNORECASE)
                for table in from_matches:
                    self.table_access[table] += 1

                into_matches = re.findall(r'INTO\s+`?(\w+)`?', content, re.IGNORECASE)
                for table in into_matches:
                    self.table_access[table] += 1

        except Exception as e:
            pass  # 忽略无法读取的文件

    def scan_project(self, exclude_dirs=None):
        """扫描整个项目"""
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', '.git', 'htmlcov', 'temp', '.pytest_cache', 'node_modules']

        print("="*60)
        print("扫描项目文件...")
        print("="*60)

        py_files = []
        for root, dirs, files in os.walk('.'):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    py_files.append(file_path)

        print(f"找到 {len(py_files)} 个Python文件")
        print("\n分析中...")

        for file_path in py_files:
            self.analyze_file(file_path)

        print("✓ 分析完成\n")

    def generate_report(self):
        """生成分析报告"""
        print("="*60)
        print("查询模式分析报告")
        print("="*60)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        report_lines = []
        report_lines.append("="*60)
        report_lines.append("查询模式分析报告")
        report_lines.append("="*60)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # 1. 查询类型统计
        print("\n1. 查询类型统计")
        print("-" * 60)
        report_lines.append("\n1. 查询类型统计")
        report_lines.append("-" * 60)

        total_queries = sum(len(queries) for queries in self.queries.values())
        print(f"总查询数: {total_queries}")
        report_lines.append(f"总查询数: {total_queries}")

        for query_type, queries in sorted(self.queries.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(queries)
            percentage = (count / total_queries * 100) if total_queries > 0 else 0
            line = f"  {query_type:20s}: {count:4d} 次 ({percentage:5.1f}%)"
            print(line)
            report_lines.append(line)

        # 2. 最常访问的表
        print("\n2. 最常访问的表 (Top 15)")
        print("-" * 60)
        report_lines.append("\n2. 最常访问的表 (Top 15)")
        report_lines.append("-" * 60)

        for table, count in self.table_access.most_common(15):
            line = f"  {table:30s}: {count:4d} 次"
            print(line)
            report_lines.append(line)

        # 3. 数据库操作频繁的文件
        print("\n3. 数据库操作频繁的文件 (Top 10)")
        print("-" * 60)
        report_lines.append("\n3. 数据库操作频繁的文件 (Top 10)")
        report_lines.append("-" * 60)

        for file_path, count in sorted(self.file_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            # 简化路径显示
            short_path = file_path if len(file_path) < 60 else "..." + file_path[-57:]
            line = f"  {short_path:60s}: {count:3d} 次"
            print(line)
            report_lines.append(line)

        # 4. SELECT查询样本
        if self.queries.get('select'):
            print("\n4. SELECT查询样本 (前5个)")
            print("-" * 60)
            report_lines.append("\n4. SELECT查询样本 (前5个)")
            report_lines.append("-" * 60)

            for i, query in enumerate(self.queries['select'][:5], 1):
                print(f"  {i}. {query['query']}")
                print(f"     文件: {query['file']}")
                report_lines.append(f"  {i}. {query['query']}")
                report_lines.append(f"     文件: {query['file']}")

        # 5. 数据库特定操作
        print("\n5. 数据库特定操作统计")
        print("-" * 60)
        report_lines.append("\n5. 数据库特定操作统计")
        report_lines.append("-" * 60)

        tdengine_count = len(self.queries.get('tdengine_stable', []))
        redis_count = sum(len(self.queries.get(k, [])) for k in ['redis_get', 'redis_set', 'redis_hget'])

        line1 = f"  TDengine STABLE操作: {tdengine_count} 次"
        line2 = f"  Redis操作: {redis_count} 次"
        print(line1)
        print(line2)
        report_lines.append(line1)
        report_lines.append(line2)

        # 6. 分析和建议
        print("\n6. 分析和建议")
        print("-" * 60)
        report_lines.append("\n6. 分析和建议")
        report_lines.append("-" * 60)

        suggestions = []

        # 读写比分析
        read_count = len(self.queries.get('select', []))
        write_count = sum(len(self.queries.get(k, [])) for k in ['insert', 'update', 'delete'])

        if read_count + write_count > 0:
            read_ratio = read_count / (read_count + write_count) * 100
            suggestion = f"  • 读写比: {read_ratio:.1f}% 读 / {100-read_ratio:.1f}% 写"
            print(suggestion)
            suggestions.append(suggestion)

            if read_ratio > 80:
                suggestion = "    → 读多写少，适合使用缓存优化"
                print(suggestion)
                suggestions.append(suggestion)

        # TDengine使用分析
        if tdengine_count == 0:
            suggestion = "  • 未发现TDengine特定操作，可能可以用PostgreSQL+TimescaleDB替代"
            print(suggestion)
            suggestions.append(suggestion)
        elif tdengine_count < 5:
            suggestion = f"  • TDengine使用较少({tdengine_count}次)，评估是否必需"
            print(suggestion)
            suggestions.append(suggestion)

        # Redis使用分析
        if redis_count == 0:
            suggestion = "  • 未发现Redis操作，可能可以移除Redis"
            print(suggestion)
            suggestions.append(suggestion)
        elif redis_count < 10:
            suggestion = f"  • Redis使用较少({redis_count}次)，评估是否必需"
            print(suggestion)
            suggestions.append(suggestion)

        # 表访问集中度
        if len(self.table_access) > 0:
            top_5_access = sum(count for _, count in self.table_access.most_common(5))
            total_access = sum(self.table_access.values())
            concentration = top_5_access / total_access * 100

            if concentration > 80:
                suggestion = f"  • 访问高度集中: Top 5表占{concentration:.1f}%，优化这些表即可"
                print(suggestion)
                suggestions.append(suggestion)

        report_lines.extend(suggestions)

        # 保存报告
        report_file = "query_patterns_analysis.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\n详细报告已保存到: {report_file}")
        print("\n下一步:")
        print("  1. 查看完整报告: cat query_patterns_analysis.txt")
        print("  2. 结合database_assessment.json分析数据")
        print("  3. 准备Day 2的数据备份")

        return self.queries


def main():
    """主函数"""
    print("="*60)
    print("MyStocks 查询模式分析工具")
    print("Week 2 Day 1 - 查询模式分析")
    print("="*60)
    print()

    analyzer = QueryPatternAnalyzer()
    analyzer.scan_project()
    analyzer.generate_report()


if __name__ == "__main__":
    main()
