#!/usr/bin/env python3
"""
优化路线图生成器 - 识别优化机会

分析代码质量、性能和架构，提供优化建议。

作者: MyStocks Team
日期: 2025-10-19

使用方法:
    python scripts/analysis/generate_optimization_roadmap.py
"""

import sys
import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    OptimizationOpportunity,
    OptimizationRoadmap,
    PriorityEnum,
    ModuleInventory,
)
from generate_docs import load_inventory


def analyze_complexity(inventory: ModuleInventory) -> List[OptimizationOpportunity]:
    """
    分析函数复杂度，找出需要重构的高复杂度函数

    Args:
        inventory: 模块清单

    Returns:
        优化机会列表
    """
    print("\n正在分析函数复杂度...")

    opportunities = []
    high_complexity_funcs = []

    # 收集所有函数
    for module in inventory.modules:
        for func in module.functions:
            if func.complexity > 10:
                high_complexity_funcs.append((module, func, None))

        for cls in module.classes:
            for method in cls.methods:
                if method.complexity > 10:
                    high_complexity_funcs.append((module, method, cls.name))

    print(f"  发现 {len(high_complexity_funcs)} 个高复杂度函数（复杂度 > 10）")

    # 按复杂度排序
    high_complexity_funcs.sort(key=lambda x: x[1].complexity, reverse=True)

    # 生成优化建议
    for module, func, cls_name in high_complexity_funcs[:20]:  # Top 20
        func_name = f"{cls_name}.{func.name}" if cls_name else func.name

        priority = (
            PriorityEnum.P0
            if func.complexity > 20
            else PriorityEnum.P1 if func.complexity > 15 else PriorityEnum.P2
        )

        effort = (
            "2-3 天"
            if func.complexity > 20
            else "1-2 天" if func.complexity > 15 else "4-8 小时"
        )

        opp = OptimizationOpportunity(
            id=f"OPT-COMPLEXITY-{len(opportunities)+1:03d}",
            title=f"重构高复杂度函数 {func_name}",
            category="code_quality",
            priority=priority,
            current_state=f"函数 `{func_name}` 圈复杂度为 {func.complexity}，超过建议阈值（10）。"
            f"位置：`{module.file_path}:{func.line_number}`",
            proposed_change=f"建议重构步骤：\n"
            f"1. 提取独立的辅助函数减少嵌套\n"
            f"2. 使用策略模式替代复杂的条件分支\n"
            f"3. 考虑拆分为多个职责单一的函数\n"
            f"4. 添加单元测试确保重构正确性",
            expected_impact=f"- 提高代码可读性和可维护性\n"
            f"- 降低缺陷率约 30-40%\n"
            f"- 简化未来的功能扩展\n"
            f"- 提高测试覆盖率",
            effort_estimate=effort,
            affected_modules=[module.file_path],
        )
        opportunities.append(opp)

    return opportunities


def analyze_long_functions(inventory: ModuleInventory) -> List[OptimizationOpportunity]:
    """
    分析过长的函数

    Args:
        inventory: 模块清单

    Returns:
        优化机会列表
    """
    print("\n正在分析函数长度...")

    opportunities = []
    long_funcs = []

    for module in inventory.modules:
        for func in module.functions:
            if func.body_lines > 50:
                long_funcs.append((module, func, None))

        for cls in module.classes:
            for method in cls.methods:
                if method.body_lines > 50:
                    long_funcs.append((module, method, cls.name))

    print(f"  发现 {len(long_funcs)} 个过长函数（> 50 行）")

    # 按长度排序
    long_funcs.sort(key=lambda x: x[1].body_lines, reverse=True)

    for module, func, cls_name in long_funcs[:10]:  # Top 10
        func_name = f"{cls_name}.{func.name}" if cls_name else func.name

        opp = OptimizationOpportunity(
            id=f"OPT-LENGTH-{len(opportunities)+1:03d}",
            title=f"拆分过长函数 {func_name}",
            category="code_quality",
            priority=PriorityEnum.P2,
            current_state=f"函数 `{func_name}` 有 {func.body_lines} 行代码，超过建议长度（50 行）。"
            f"位置：`{module.file_path}:{func.line_number}`",
            proposed_change=f"建议重构步骤：\n"
            f"1. 识别函数中的逻辑块\n"
            f"2. 将每个逻辑块提取为独立函数\n"
            f"3. 使用清晰的函数名描述每个步骤\n"
            f"4. 保持原函数作为高层次的协调者",
            expected_impact=f"- 提高代码可读性\n"
            f"- 便于单元测试\n"
            f"- 提高代码复用性",
            effort_estimate="1-2 天",
            affected_modules=[module.file_path],
        )
        opportunities.append(opp)

    return opportunities


def analyze_god_objects(inventory: ModuleInventory) -> List[OptimizationOpportunity]:
    """
    识别 God Objects（职责过多的类）

    Args:
        inventory: 模块清单

    Returns:
        优化机会列表
    """
    print("\n正在识别 God Objects...")

    opportunities = []
    large_classes = []

    for module in inventory.modules:
        for cls in module.classes:
            method_count = len(cls.methods)
            if method_count > 20:  # 超过 20 个方法
                large_classes.append((module, cls, method_count))

    print(f"  发现 {len(large_classes)} 个大型类（> 20 个方法）")

    large_classes.sort(key=lambda x: x[2], reverse=True)

    for module, cls, method_count in large_classes[:5]:  # Top 5
        opp = OptimizationOpportunity(
            id=f"OPT-GOD-{len(opportunities)+1:03d}",
            title=f"重构 God Object: {cls.name}",
            category="architecture",
            priority=PriorityEnum.P1,
            current_state=f"类 `{cls.name}` 有 {method_count} 个方法，可能违反单一职责原则。"
            f"位置：`{module.file_path}:{cls.line_number}`",
            proposed_change=f"建议重构步骤：\n"
            f"1. 分析类的职责，识别不同的关注点\n"
            f"2. 将相关方法分组\n"
            f"3. 提取为独立的类（如 Manager, Helper, Strategy）\n"
            f"4. 使用组合或委托模式连接拆分后的类\n"
            f"5. 渐进式重构，保持向后兼容",
            expected_impact=f"- 提高类的内聚性\n"
            f"- 降低类之间的耦合\n"
            f"- 提高代码可测试性\n"
            f"- 简化未来的维护工作",
            effort_estimate="3-5 天",
            affected_modules=[module.file_path],
        )
        opportunities.append(opp)

    return opportunities


def analyze_missing_docstrings(
    inventory: ModuleInventory,
) -> List[OptimizationOpportunity]:
    """
    找出缺少文档的模块和函数

    Args:
        inventory: 模块清单

    Returns:
        优化机会列表
    """
    print("\n正在分析文档覆盖率...")

    undocumented_modules = []
    undocumented_functions = 0

    for module in inventory.modules:
        if not module.docstring:
            undocumented_modules.append(module)

        for func in module.functions:
            if not func.docstring and not func.name.startswith("_"):
                undocumented_functions += 1

        for cls in module.classes:
            for method in cls.methods:
                if not method.docstring and not method.name.startswith("_"):
                    undocumented_functions += 1

    print(f"  未文档化模块: {len(undocumented_modules)}")
    print(f"  未文档化函数: {undocumented_functions}")

    opportunities = []

    if len(undocumented_modules) > 20:
        opp = OptimizationOpportunity(
            id="OPT-DOC-001",
            title="提高模块文档覆盖率",
            category="code_quality",
            priority=PriorityEnum.P2,
            current_state=f"{len(undocumented_modules)} 个模块缺少 docstring，"
            f"约占总模块的 {len(undocumented_modules)/len(inventory.modules)*100:.1f}%",
            proposed_change=f"建议行动：\n"
            f"1. 为每个模块添加顶部 docstring\n"
            f"2. 说明模块用途、主要类和函数\n"
            f"3. 添加作者和日期信息\n"
            f"4. 包含使用示例（如适用）",
            expected_impact=f"- 提高代码可读性\n"
            f"- 降低新开发者学习曲线\n"
            f"- 支持自动文档生成",
            effort_estimate="2-3 天",
            affected_modules=[m.file_path for m in undocumented_modules[:10]],
        )
        opportunities.append(opp)

    if undocumented_functions > 100:
        opp = OptimizationOpportunity(
            id="OPT-DOC-002",
            title="提高函数文档覆盖率",
            category="code_quality",
            priority=PriorityEnum.P3,
            current_state=f"约 {undocumented_functions} 个公共函数缺少 docstring",
            proposed_change=f"建议行动：\n"
            f"1. 优先为公共 API 函数添加文档\n"
            f"2. 使用标准格式（Google/NumPy style）\n"
            f"3. 说明参数、返回值和可能的异常\n"
            f"4. 添加使用示例",
            expected_impact=f"- 提高 API 易用性\n"
            f"- 减少使用错误\n"
            f"- 支持 IDE 自动补全",
            effort_estimate="5-7 天",
            affected_modules=[],
        )
        opportunities.append(opp)

    return opportunities


def analyze_performance_opportunities(
    inventory: ModuleInventory,
) -> List[OptimizationOpportunity]:
    """
    识别性能优化机会

    Args:
        inventory: 模块清单

    Returns:
        优化机会列表
    """
    print("\n正在识别性能优化机会...")

    opportunities = []

    # 检查数据库连接管理
    db_modules = [
        m
        for m in inventory.modules
        if "database" in m.file_path.lower() or "db_manager" in m.file_path.lower()
    ]

    if db_modules:
        # 检查是否有连接池
        has_pool = False
        for module in db_modules:
            for cls in module.classes:
                if "pool" in cls.name.lower():
                    has_pool = True
                    break

        if not has_pool:
            opp = OptimizationOpportunity(
                id="OPT-PERF-001",
                title="实现数据库连接池",
                category="performance",
                priority=PriorityEnum.P1,
                current_state="数据库连接未使用连接池，每次查询都创建新连接，导致性能开销",
                proposed_change=f"建议实现：\n"
                f"1. 使用 SQLAlchemy 连接池或自定义实现\n"
                f"2. 配置合理的池大小（如 5-20 连接）\n"
                f"3. 设置连接超时和回收策略\n"
                f"4. 添加连接健康检查",
                expected_impact=f"- 减少连接建立时间 80-90%\n"
                f"- 提高并发处理能力 3-5 倍\n"
                f"- 降低数据库服务器负载",
                effort_estimate="2-3 天",
                affected_modules=[m.file_path for m in db_modules],
            )
            opportunities.append(opp)

    # 检查缓存使用
    cache_modules = [
        m
        for m in inventory.modules
        if "cache" in m.file_path.lower() or "redis" in m.file_path.lower()
    ]

    if len(cache_modules) < 3:  # 缓存使用不足
        opp = OptimizationOpportunity(
            id="OPT-PERF-002",
            title="增加数据缓存层",
            category="performance",
            priority=PriorityEnum.P2,
            current_state="系统缓存使用不足，频繁查询数据库可能导致性能瓶颈",
            proposed_change=f"建议实现：\n"
            f"1. 为热点数据添加 Redis 缓存\n"
            f"2. 实现缓存失效策略（TTL、LRU）\n"
            f"3. 添加缓存预热机制\n"
            f"4. 监控缓存命中率",
            expected_impact=f"- 减少数据库查询 50-70%\n"
            f"- 提高响应速度 2-3 倍\n"
            f"- 提高系统可扩展性",
            effort_estimate="3-5 天",
            affected_modules=[],
        )
        opportunities.append(opp)

    # 检查批量操作
    opp = OptimizationOpportunity(
        id="OPT-PERF-003",
        title="优化数据批量处理",
        category="performance",
        priority=PriorityEnum.P2,
        current_state="部分数据插入和更新使用逐条操作，效率较低",
        proposed_change=f"建议优化：\n"
        f"1. 使用批量插入（batch insert）\n"
        f"2. 实现事务批处理\n"
        f"3. 使用 COPY 命令（PostgreSQL）或 LOAD DATA（MySQL）\n"
        f"4. 设置合理的批次大小（如 1000-5000 条）",
        expected_impact=f"- 提高数据写入速度 10-50 倍\n"
        f"- 减少网络往返次数\n"
        f"- 降低数据库锁竞争",
        effort_estimate="1-2 天",
        affected_modules=[],
    )
    opportunities.append(opp)

    return opportunities


def save_roadmap(roadmap: OptimizationRoadmap, output_path: str):
    """保存优化路线图到 JSON"""

    data = {
        "total_opportunities": len(roadmap.opportunities),
        "by_category": {
            "performance": len(roadmap.performance),
            "architecture": len(roadmap.architecture),
            "code_quality": len(roadmap.code_quality),
        },
        "by_priority": {
            "p0": len(roadmap.get_by_priority(PriorityEnum.P0)),
            "p1": len(roadmap.get_by_priority(PriorityEnum.P1)),
            "p2": len(roadmap.get_by_priority(PriorityEnum.P2)),
            "p3": len(roadmap.get_by_priority(PriorityEnum.P3)),
        },
        "quick_wins": len(roadmap.get_quick_wins()),
        "opportunities": [
            {
                "id": opp.id,
                "title": opp.title,
                "category": opp.category,
                "priority": opp.priority.value,
                "current_state": opp.current_state,
                "proposed_change": opp.proposed_change,
                "expected_impact": opp.expected_impact,
                "effort_estimate": opp.effort_estimate,
                "affected_modules": opp.affected_modules,
            }
            for opp in roadmap.opportunities
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 优化路线图已保存: {output_path}")


def main():
    """主函数"""
    print("MyStocks 优化路线图生成器")
    print("=" * 60)

    # 加载清单
    inventory_path = (
        PROJECT_ROOT
        / "docs/function-classification-manual/metadata/module-inventory.json"
    )

    if not inventory_path.exists():
        print(f"\n✗ 错误: 清单文件不存在: {inventory_path}")
        return

    print(f"\n加载清单: {inventory_path}")
    inventory = load_inventory(str(inventory_path))
    print(f"✓ 加载完成，共 {len(inventory.modules)} 个模块")

    # 创建路线图
    roadmap = OptimizationRoadmap()

    # 各类分析
    complexity_opps = analyze_complexity(inventory)
    for opp in complexity_opps:
        roadmap.add_opportunity(opp)

    length_opps = analyze_long_functions(inventory)
    for opp in length_opps:
        roadmap.add_opportunity(opp)

    god_opps = analyze_god_objects(inventory)
    for opp in god_opps:
        roadmap.add_opportunity(opp)

    doc_opps = analyze_missing_docstrings(inventory)
    for opp in doc_opps:
        roadmap.add_opportunity(opp)

    perf_opps = analyze_performance_opportunities(inventory)
    for opp in perf_opps:
        roadmap.add_opportunity(opp)

    # 统计
    print("\n" + "=" * 60)
    print("优化路线图生成完成")
    print("=" * 60)
    print(f"\n总优化机会: {len(roadmap.opportunities)}")
    print(f"  性能优化: {len(roadmap.performance)}")
    print(f"  架构优化: {len(roadmap.architecture)}")
    print(f"  代码质量: {len(roadmap.code_quality)}")
    print(f"\n按优先级:")
    print(f"  P0 (紧急): {len(roadmap.get_by_priority(PriorityEnum.P0))}")
    print(f"  P1 (高): {len(roadmap.get_by_priority(PriorityEnum.P1))}")
    print(f"  P2 (中): {len(roadmap.get_by_priority(PriorityEnum.P2))}")
    print(f"  P3 (低): {len(roadmap.get_by_priority(PriorityEnum.P3))}")
    print(f"\n快速胜利: {len(roadmap.get_quick_wins())}")

    # 保存结果
    output_dir = PROJECT_ROOT / "docs/function-classification-manual/metadata"
    output_path = output_dir / "optimization-roadmap.json"
    save_roadmap(roadmap, str(output_path))

    # 生成 Markdown 文档
    from src.utils.markdown_writer import MarkdownWriter

    writer = MarkdownWriter(str(PROJECT_ROOT / "docs/function-classification-manual"))
    doc_path = writer.generate_optimization_roadmap(roadmap)
    print(f"✓ 完整文档已生成: {doc_path}")

    print("\n✓ 优化路线图生成完成!")

    return roadmap


if __name__ == "__main__":
    main()
