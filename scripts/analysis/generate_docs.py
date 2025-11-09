#!/usr/bin/env python3
"""
文档生成器 - 生成功能分类手册文档

从扫描的模块清单生成完整的分类手册文档。

作者: MyStocks Team
日期: 2025-10-19

使用方法:
    python scripts/analysis/generate_docs.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    ModuleInventory,
    ModuleMetadata,
    ClassMetadata,
    FunctionMetadata,
    ParameterMetadata,
    CategoryEnum,
    ManualMetadata,
    DataFlow,
)
from src.utils.markdown_writer import MarkdownWriter


def load_inventory(json_path: str) -> ModuleInventory:
    """
    从 JSON 文件加载清单

    Args:
        json_path: JSON 文件路径

    Returns:
        ModuleInventory 对象
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 重建对象
    modules = []

    for module_data in data["modules"]:
        # 重建函数
        functions = []
        for func_data in module_data["functions"]:
            parameters = [
                ParameterMetadata(
                    name=p["name"],
                    type_annotation=p.get("type_annotation"),
                    default_value=p.get("default_value"),
                    is_required=p.get("is_required", True),
                )
                for p in func_data.get("parameters", [])
            ]

            func = FunctionMetadata(
                name=func_data["name"],
                line_number=func_data["line_number"],
                parameters=parameters,
                return_type=func_data.get("return_type"),
                docstring=func_data.get("docstring"),
                is_async=func_data.get("is_async", False),
                decorators=func_data.get("decorators", []),
                body_lines=func_data.get("body_lines", 0),
                complexity=func_data.get("complexity", 0),
            )
            functions.append(func)

        # 重建类
        classes = []
        for class_data in module_data["classes"]:
            # 重建方法
            methods = []
            for method_data in class_data["methods"]:
                parameters = [
                    ParameterMetadata(
                        name=p["name"],
                        type_annotation=p.get("type_annotation"),
                        default_value=p.get("default_value"),
                        is_required=p.get("is_required", True),
                    )
                    for p in method_data.get("parameters", [])
                ]

                method = FunctionMetadata(
                    name=method_data["name"],
                    line_number=method_data["line_number"],
                    parameters=parameters,
                    return_type=method_data.get("return_type"),
                    docstring=method_data.get("docstring"),
                    is_async=method_data.get("is_async", False),
                    decorators=method_data.get("decorators", []),
                    body_lines=method_data.get("body_lines", 0),
                    complexity=method_data.get("complexity", 0),
                )
                methods.append(method)

            cls = ClassMetadata(
                name=class_data["name"],
                line_number=class_data["line_number"],
                base_classes=class_data.get("base_classes", []),
                methods=methods,
                docstring=class_data.get("docstring"),
                decorators=class_data.get("decorators", []),
                is_abstract=class_data.get("is_abstract", False),
            )
            classes.append(cls)

        # 重建模块
        module = ModuleMetadata(
            file_path=module_data["file_path"],
            module_name=module_data["module_name"],
            category=CategoryEnum(module_data["category"]),
            classes=classes,
            functions=functions,
            imports=module_data.get("imports", []),
            docstring=module_data.get("docstring"),
            lines_of_code=module_data["lines_of_code"],
            blank_lines=module_data.get("blank_lines", 0),
            comment_lines=module_data.get("comment_lines", 0),
            last_modified=(
                datetime.fromisoformat(module_data["last_modified"])
                if module_data.get("last_modified")
                else None
            ),
        )
        modules.append(module)

    # 重建元数据
    meta_data = data["metadata"]
    metadata = ManualMetadata(
        version=meta_data["version"],
        generation_date=datetime.fromisoformat(meta_data["generation_date"]),
        total_modules=meta_data["total_modules"],
        total_classes=meta_data["total_classes"],
        total_functions=meta_data["total_functions"],
        total_lines=meta_data["total_lines"],
        avg_function_complexity=meta_data.get("avg_function_complexity", 0.0),
        max_function_complexity=meta_data.get("max_function_complexity", 0),
        category_stats=meta_data.get("category_stats", {}),
    )

    inventory = ModuleInventory(modules=modules, metadata=metadata)
    return inventory


def generate_category_documents(inventory: ModuleInventory, writer: MarkdownWriter):
    """生成所有类别文档"""
    print("\n生成功能类别文档...")

    category_info = {
        CategoryEnum.CORE: {
            "name": "核心功能",
            "description": """
核心功能模块实现系统的主要业务逻辑和数据编排。这些模块是系统的核心，
负责统一数据访问、数据分类路由、以及系统初始化和配置。

**关键特性**:
- 系统主入口点和编排逻辑
- 统一数据访问接口（Unified Manager）
- 5 层数据分类系统实现
- 智能数据路由策略
- 多数据库协调管理

**设计模式**: Manager Pattern, Strategy Pattern, Facade Pattern
""",
        },
        CategoryEnum.AUXILIARY: {
            "name": "辅助功能",
            "description": """
辅助功能模块为核心功能提供扩展和支持，主要包括各种数据源适配器、
工厂模式实现、交易策略、回测引擎等可插拔组件。

**关键特性**:
- 外部数据源适配器（AKShare, Baostock, 通达信等）
- 数据源工厂模式
- 量化交易策略实现
- 回测引擎
- 机器学习策略
- 实时数据处理

**设计模式**: Adapter Pattern, Factory Pattern, Strategy Pattern
""",
        },
        CategoryEnum.INFRASTRUCTURE: {
            "name": "基础设施功能",
            "description": """
基础设施模块提供底层数据库连接管理、表结构定义、配置管理等基础服务。
这些模块确保系统的稳定运行和数据持久化。

**关键特性**:
- 多数据库连接管理（TDengine, PostgreSQL, MySQL, Redis）
- 配置驱动的表结构管理
- 数据库连接池
- ORM 模型定义
- 数据迁移工具

**设计模式**: Singleton Pattern, Connection Pool, Repository Pattern
""",
        },
        CategoryEnum.MONITORING: {
            "name": "监控功能",
            "description": """
监控功能模块提供系统运行状态监控、性能跟踪、数据质量检查和告警管理。
确保系统健康运行和数据质量。

**关键特性**:
- 操作日志记录
- 性能指标跟踪
- 数据质量监控
- 多渠道告警（邮件、Webhook、日志）
- Grafana/Prometheus 集成

**设计模式**: Observer Pattern, Strategy Pattern
""",
        },
        CategoryEnum.UTILITY: {
            "name": "工具功能",
            "description": """
工具功能模块提供各种通用辅助功能，包括日期处理、股票代码转换、
列名映射、重试装饰器等。这些工具被其他模块广泛使用。

**关键特性**:
- 日期和时间处理工具
- 股票代码格式转换
- 列名映射和标准化
- 重试和错误处理装饰器
- 数据验证工具

**设计模式**: Decorator Pattern, Utility Pattern
""",
        },
    }

    for category in [
        CategoryEnum.CORE,
        CategoryEnum.AUXILIARY,
        CategoryEnum.INFRASTRUCTURE,
        CategoryEnum.MONITORING,
        CategoryEnum.UTILITY,
    ]:

        modules = inventory.get_modules_by_category(category)

        if not modules and category != CategoryEnum.CORE:
            continue

        info = category_info[category]
        filepath = writer.generate_category_document(
            category, modules, info["name"], info["description"]
        )
        print(f"  ✓ {info['name']}: {filepath}")


def generate_data_flows(inventory: ModuleInventory, writer: MarkdownWriter):
    """生成数据流文档"""
    print("\n生成数据流图...")

    # 定义关键数据流
    data_flows = [
        DataFlow(
            id="FLOW-001",
            name="市场数据获取与存储",
            description="从外部数据源获取市场数据并存储到 TDengine",
            data_classification="Market Data",
            database_target="TDengine",
            steps=[
                {
                    "module": "adapters/akshare_adapter",
                    "function": "fetch_realtime_data",
                    "action": "从 AKShare 获取实时行情数据",
                },
                {
                    "module": "unified_manager",
                    "function": "save_data_by_classification",
                    "action": "根据数据分类自动路由",
                },
                {
                    "module": "core",
                    "function": "DataStorageStrategy.get_target_database",
                    "action": "确定目标数据库为 TDengine",
                },
                {
                    "module": "data_access",
                    "function": "TDengineDataAccess.save_market_data",
                    "action": "保存到 TDengine 时序数据库",
                },
            ],
        ),
        DataFlow(
            id="FLOW-002",
            name="参考数据管理",
            description="管理股票列表、交易日历等参考数据",
            data_classification="Reference Data",
            database_target="MySQL",
            steps=[
                {
                    "module": "adapters/akshare_adapter",
                    "function": "fetch_stock_list",
                    "action": "获取股票列表",
                },
                {
                    "module": "unified_manager",
                    "function": "save_data_by_classification",
                    "action": "分类为参考数据",
                },
                {
                    "module": "data_access",
                    "function": "MySQLDataAccess.save_reference_data",
                    "action": "保存到 MySQL",
                },
            ],
        ),
        DataFlow(
            id="FLOW-003",
            name="技术指标计算",
            description="计算技术指标并存储到 PostgreSQL",
            data_classification="Derived Data",
            database_target="PostgreSQL",
            steps=[
                {
                    "module": "data_access",
                    "function": "TDengineDataAccess.load_market_data",
                    "action": "从 TDengine 加载原始市场数据",
                },
                {
                    "module": "indicators",
                    "function": "calculate_indicators",
                    "action": "计算技术指标（MA, MACD, RSI 等）",
                },
                {
                    "module": "unified_manager",
                    "function": "save_data_by_classification",
                    "action": "分类为衍生数据",
                },
                {
                    "module": "data_access",
                    "function": "PostgreSQLDataAccess.save_derived_data",
                    "action": "保存到 PostgreSQL",
                },
            ],
        ),
        DataFlow(
            id="FLOW-004",
            name="实时交易数据",
            description="管理实时持仓和交易数据的热冷分离",
            data_classification="Transaction Data",
            database_target="Redis + PostgreSQL",
            steps=[
                {
                    "module": "strategy",
                    "function": "execute_trade",
                    "action": "执行交易策略",
                },
                {
                    "module": "data_access",
                    "function": "RedisDataAccess.save_hot_data",
                    "action": "保存活跃持仓到 Redis",
                },
                {
                    "module": "automation",
                    "function": "archive_cold_data",
                    "action": "定时归档冷数据",
                },
                {
                    "module": "data_access",
                    "function": "PostgreSQLDataAccess.save_transaction_history",
                    "action": "保存历史交易到 PostgreSQL",
                },
            ],
        ),
    ]

    filepath = writer.generate_data_flow_maps(data_flows)
    print(f"  ✓ 数据流图: {filepath}")


def main():
    """主函数"""
    print("MyStocks 功能分类手册生成器")
    print("=" * 60)

    # 加载清单
    inventory_path = (
        PROJECT_ROOT
        / "docs/function-classification-manual/metadata/module-inventory.json"
    )

    if not inventory_path.exists():
        print(f"\n✗ 错误: 清单文件不存在: {inventory_path}")
        print("  请先运行: python scripts/analysis/scan_codebase.py")
        return

    print(f"\n加载清单: {inventory_path}")
    inventory = load_inventory(str(inventory_path))
    print(f"✓ 加载完成，共 {len(inventory.modules)} 个模块")

    # 创建文档生成器
    output_dir = PROJECT_ROOT / "docs/function-classification-manual"
    writer = MarkdownWriter(str(output_dir))

    # 生成类别文档
    generate_category_documents(inventory, writer)

    # 生成数据流文档
    generate_data_flows(inventory, writer)

    # 更新 README 中的统计数据
    print("\n更新 README 统计数据...")
    update_readme_stats(inventory)

    print("\n" + "=" * 60)
    print("✓ 所有文档生成完成!")
    print("=" * 60)
    print(f"\n文档位置: {output_dir}")
    print("\n生成的文档:")
    print("  - 01-core-functions.md")
    print("  - 02-auxiliary-functions.md")
    print("  - 03-infrastructure-functions.md")
    print("  - 04-monitoring-functions.md")
    print("  - 05-utility-functions.md")
    print("  - 09-data-flow-maps.md")
    print("  - README.md (已更新)")


def update_readme_stats(inventory: ModuleInventory):
    """更新 README 中的统计表"""
    readme_path = PROJECT_ROOT / "docs/function-classification-manual/README.md"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 构建新的统计表
    stats_lines = []
    stats_lines.append("| 类别 | 模块数 | 函数数 | 代码行数 |")
    stats_lines.append("|------|--------|--------|----------|")

    category_names = {
        "core": "核心功能",
        "auxiliary": "辅助功能",
        "infrastructure": "基础设施",
        "monitoring": "监控功能",
        "utility": "工具功能",
    }

    total_modules = 0
    total_functions = 0
    total_lines = 0

    for cat_key, cat_name in category_names.items():
        if cat_key in inventory.metadata.category_stats:
            stats = inventory.metadata.category_stats[cat_key]
            stats_lines.append(
                f"| {cat_name} | {stats['modules']} | {stats['functions']} | {stats['lines']:,} |"
            )
            total_modules += stats["modules"]
            total_functions += stats["functions"]
            total_lines += stats["lines"]

    stats_lines.append(
        f"| **总计** | **{total_modules}** | **{total_functions}** | **{total_lines:,}** |"
    )

    new_stats_table = "\n".join(stats_lines)

    # 替换统计表
    import re

    pattern = r"\| 类别 \| 模块数 \| 函数数 \| 代码行数 \|.*?\| \*\*总计\*\* \|.*?\|"
    content = re.sub(pattern, new_stats_table, content, flags=re.DOTALL)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  ✓ README 统计表已更新")


if __name__ == "__main__":
    main()
