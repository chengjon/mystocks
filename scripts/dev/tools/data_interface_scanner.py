#!/usr/bin/env python3
"""数据接口扫描工具 - Data Interface Scanner

功能：
1. 扫描 config/data_sources_registry.yaml 文件
2. 生成所有已注册数据接口的明细表
3. 按数据分类分组显示
4. 提供数据源统计信息
5. 支持多种输出格式（表格、JSON、CSV）

使用示例：
    # 基本扫描
    python scripts/tools/data_interface_scanner.py

    # 生成详细报告
    python scripts/tools/data_interface_scanner.py --detailed

    # 导出JSON格式
    python scripts/tools/data_interface_scanner.py --output-format json --output-file interfaces.json

    # 按数据源类型过滤
    python scripts/tools/data_interface_scanner.py --filter-source akshare

作者：Claude Code
版本：v1.0
创建时间：2026-01-09
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tabulate import tabulate
except ImportError:
    print("警告: 未安装 tabulate 库，使用简单文本输出")
    tabulate = None


class DataInterfaceScanner:
    """数据接口扫描器"""

    def __init__(self):
        self.config_file = project_root / "config" / "data_sources_registry.yaml"
        self.data_sources = {}
        self.scan_timestamp = datetime.now()

    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                print(f"错误: 配置文件不存在: {self.config_file}")
                return False

            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            self.data_sources = config.get("data_sources", {})
            print(f"✅ 成功加载 {len(self.data_sources)} 个数据接口配置")
            return True

        except Exception as e:
            print(f"错误: 加载配置文件失败: {e}")
            return False

    def scan_interfaces(self) -> Dict[str, Any]:
        """扫描所有数据接口"""
        interfaces = []
        stats = {
            "total_interfaces": 0,
            "by_source_type": {},
            "by_data_category": {},
            "by_target_db": {},
            "quality_score_distribution": {"high": 0, "medium": 0, "low": 0},
            "priority_distribution": {},
        }

        for endpoint_name, config in self.data_sources.items():
            interface_info = self._parse_interface_info(endpoint_name, config)
            interfaces.append(interface_info)

            stats["total_interfaces"] += 1

            source_type = config.get("source_type", "unknown")
            stats["by_source_type"][source_type] = stats["by_source_type"].get(source_type, 0) + 1

            data_category = config.get("data_category", "unknown")
            stats["by_data_category"][data_category] = stats["by_data_category"].get(data_category, 0) + 1

            target_db = config.get("target_db", "unknown")
            stats["by_target_db"][target_db] = stats["by_target_db"].get(target_db, 0) + 1

            quality_score = config.get("data_quality_score", 0)
            if quality_score >= 9.0:
                stats["quality_score_distribution"]["high"] += 1
            elif quality_score >= 7.0:
                stats["quality_score_distribution"]["medium"] += 1
            else:
                stats["quality_score_distribution"]["low"] += 1

            priority = config.get("priority", 999)
            priority_level = "high" if priority <= 2 else "medium" if priority <= 5 else "low"
            stats["priority_distribution"][priority_level] = stats["priority_distribution"].get(priority_level, 0) + 1

        return {
            "interfaces": interfaces,
            "stats": stats,
            "scan_info": {
                "timestamp": self.scan_timestamp.isoformat(),
                "config_file": str(self.config_file),
                "total_interfaces": len(interfaces),
            },
        }

    def _parse_interface_info(self, endpoint_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个接口信息"""
        # 参数信息
        parameters = config.get("parameters", {})
        param_count = len(parameters)
        required_params = sum(1 for p in parameters.values() if p.get("required", False))

        # 测试参数
        test_params = config.get("test_parameters", {})

        return {
            "endpoint_name": endpoint_name,
            "source_name": config.get("source_name", "unknown"),
            "source_type": config.get("source_type", "unknown"),
            "data_category": config.get("data_category", "unknown"),
            "data_classification": config.get("data_classification", "unknown"),
            "classification_level": config.get("classification_level", 0),
            "target_db": config.get("target_db", "unknown"),
            "table_name": config.get("table_name", "unknown"),
            "description": config.get("description", ""),
            "update_frequency": config.get("update_frequency", "unknown"),
            "data_quality_score": config.get("data_quality_score", 0.0),
            "priority": config.get("priority", 999),
            "status": config.get("status", "unknown"),
            "parameters": {
                "total": param_count,
                "required": required_params,
                "optional": param_count - required_params,
            },
            "has_test_params": len(test_params) > 0,
            "tags": config.get("tags", []),
        }

    def generate_table_report(self, scan_result: Dict[str, Any], detailed: bool = False) -> str:
        """生成表格报告"""
        interfaces = scan_result["interfaces"]
        stats = scan_result["stats"]

        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("📊 MyStocks 数据接口扫描报告")
        report_lines.append("=" * 100)
        report_lines.append(f"扫描时间: {self.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"配置文件: {self.config_file}")
        report_lines.append(f"总接口数: {stats['total_interfaces']}")
        report_lines.append("")

        # 统计信息
        report_lines.append("📈 统计概览:")
        report_lines.append(f"  • 按数据源类型: {stats['by_source_type']}")
        report_lines.append(f"  • 按数据分类: {stats['by_data_category']}")
        report_lines.append(f"  • 按目标数据库: {stats['by_target_db']}")
        report_lines.append(f"  • 质量评分分布: {stats['quality_score_distribution']}")
        report_lines.append(f"  • 优先级分布: {stats['priority_distribution']}")
        report_lines.append("")

        # 数据接口明细表
        if tabulate:
            # 简要表格
            table_data = []
            for interface in interfaces:
                row = [
                    interface["endpoint_name"],
                    interface["source_name"],
                    interface["source_type"],
                    interface["data_category"],
                    interface["target_db"],
                    f"{interface['data_quality_score']:.1f}",
                    interface["priority"],
                    interface["status"],
                ]
                table_data.append(row)

            headers = ["端点名称", "数据源", "类型", "数据分类", "目标库", "质量分", "优先级", "状态"]
            table = tabulate(table_data, headers=headers, tablefmt="grid")
            report_lines.append("📋 数据接口明细表:")
            report_lines.append(table)
        else:
            # 简单文本表格
            report_lines.append("📋 数据接口明细表:")
            report_lines.append("-" * 100)
            report_lines.append("<8")
            report_lines.append("-" * 100)
            for interface in interfaces:
                report_lines.append("<8")
        if detailed:
            report_lines.append("")
            report_lines.append("🔍 详细接口信息:")
            for interface in interfaces:
                report_lines.append(f"• {interface['endpoint_name']}")
                report_lines.append(f"  数据源: {interface['source_name']} ({interface['source_type']})")
                report_lines.append(
                    f"  数据分类: {interface['data_category']} (级别{interface['classification_level']})",
                )
                report_lines.append(f"  存储位置: {interface['target_db']} -> {interface['table_name']}")
                report_lines.append(
                    f"  质量评分: {interface['data_quality_score']:.1f}, 优先级: {interface['priority']}",
                )
                report_lines.append(f"  更新频率: {interface['update_frequency']}, 状态: {interface['status']}")
                report_lines.append(
                    f"  参数: {interface['parameters']['total']}个 (必需{interface['parameters']['required']}个)",
                )
                report_lines.append(f"  测试参数: {'✅' if interface['has_test_params'] else '❌'}")
                report_lines.append(f"  描述: {interface['description']}")
                if interface["tags"]:
                    report_lines.append(f"  标签: {', '.join(interface['tags'])}")
                report_lines.append("")

        return "\n".join(report_lines)

    def filter_interfaces(
        self,
        interfaces: List[Dict[str, Any]],
        filter_source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """按条件过滤接口"""
        if not filter_source:
            return interfaces

        return [
            i
            for i in interfaces
            if filter_source.lower() in i["source_name"].lower() or filter_source.lower() in i["source_type"].lower()
        ]

    def export_data(self, scan_result: Dict[str, Any], output_format: str, output_file: Optional[str] = None):
        """导出数据"""
        if output_format == "json":
            data = scan_result
        elif output_format == "csv":
            # 转换为CSV格式
            import csv

            data = []
            for interface in scan_result["interfaces"]:
                row = {
                    "endpoint_name": interface["endpoint_name"],
                    "source_name": interface["source_name"],
                    "source_type": interface["source_type"],
                    "data_category": interface["data_category"],
                    "target_db": interface["target_db"],
                    "table_name": interface["table_name"],
                    "data_quality_score": interface["data_quality_score"],
                    "priority": interface["priority"],
                    "status": interface["status"],
                    "description": interface["description"],
                }
                data.append(row)
        else:
            print(f"不支持的输出格式: {output_format}")
            return

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                if output_format == "json":
                    json.dump(data, f, indent=2, ensure_ascii=False)
                elif output_format == "csv":
                    if data:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            print(f"✅ 数据已导出到: {output_file}")
        elif output_format == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("CSV格式需要指定输出文件")


def main():
    parser = argparse.ArgumentParser(description="数据接口扫描工具")
    parser.add_argument("--detailed", "-d", action="store_true", help="生成详细报告")
    parser.add_argument("--filter-source", "-f", help="按数据源名称或类型过滤")
    parser.add_argument("--output-format", "-o", choices=["table", "json", "csv"], default="table", help="输出格式")
    parser.add_argument("--output-file", help="输出文件路径")

    args = parser.parse_args()

    scanner = DataInterfaceScanner()

    # 加载配置
    if not scanner.load_config():
        sys.exit(1)

    # 扫描接口
    scan_result = scanner.scan_interfaces()

    # 过滤接口
    if args.filter_source:
        scan_result["interfaces"] = scanner.filter_interfaces(scan_result["interfaces"], args.filter_source)
        scan_result["stats"]["total_interfaces"] = len(scan_result["interfaces"])

    # 生成报告
    if args.output_format == "table":
        report = scanner.generate_table_report(scan_result, args.detailed)
        print(report)
    else:
        scanner.export_data(scan_result, args.output_format, args.output_file)


if __name__ == "__main__":
    main()
