"""Markdown 文档生成器 - 生成手册文档

生成格式良好的 Markdown 文档，包括：
- 模块分类文档
- 重复分析报告
- 优化路线图
- 合并指南
- 数据流图

作者: MyStocks Team
日期: 2025-10-19
"""

import sys
from pathlib import Path
from typing import List


sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    CategoryEnum,
    ConsolidationGuide,
    DataFlow,
    DuplicationCase,
    DuplicationIndex,
    MergeRecommendation,
    ModuleMetadata,
    OptimizationOpportunity,
    OptimizationRoadmap,
)


DEFAULT_OUTPUT_DIR = "/opt/claude/mystocks_spec/docs/references/function-classification-manual"


class MarkdownWriter:
    """Markdown 文档生成器"""

    def __init__(self, output_dir: str):
        """初始化文档生成器

        Args:
            output_dir: 输出目录路径

        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_category_document(
        self,
        category: CategoryEnum,
        modules: List[ModuleMetadata],
        category_name_cn: str,
        category_description: str,
    ) -> str:
        """生成功能类别文档

        Args:
            category: 类别枚举
            modules: 该类别的模块列表
            category_name_cn: 中文类别名称
            category_description: 类别描述

        Returns:
            文档文件路径

        """
        category_files = {
            CategoryEnum.CORE: "01-core-functions.md",
            CategoryEnum.AUXILIARY: "02-auxiliary-functions.md",
            CategoryEnum.INFRASTRUCTURE: "03-infrastructure-functions.md",
            CategoryEnum.MONITORING: "04-monitoring-functions.md",
            CategoryEnum.UTILITY: "05-utility-functions.md",
        }

        filename = category_files.get(category, f"{category.value}-functions.md")
        filepath = self.output_dir / filename

        lines = []

        # 标题
        lines.append(f"# {category_name_cn}\n")
        lines.append(f"**类别**: {category.value}")
        lines.append(f"**模块数**: {len(modules)}")

        # 统计
        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) + sum(len(c.methods) for c in m.classes) for m in modules)
        total_lines = sum(m.lines_of_code for m in modules)

        lines.append(f"**类数**: {total_classes}")
        lines.append(f"**函数数**: {total_functions}")
        lines.append(f"**代码行数**: {total_lines}\n")

        # 描述
        lines.append("## 概述\n")
        lines.append(f"{category_description}\n")

        # 模块列表
        lines.append("## 模块列表\n")

        for module in sorted(modules, key=lambda m: m.file_path):
            lines.append(f"### {module.module_name}\n")
            lines.append(f"**文件**: `{module.file_path}`\n")

            if module.docstring:
                lines.append("**说明**:\n")
                lines.append(f"{module.docstring}\n")

            # 类列表
            if module.classes:
                lines.append("#### 类\n")
                for cls in module.classes:
                    lines.append(f"##### `{cls.name}`\n")

                    if cls.docstring:
                        lines.append(f"{cls.docstring}\n")

                    if cls.base_classes:
                        lines.append(
                            f"**继承**: {', '.join(f'`{b}`' for b in cls.base_classes)}\n",
                        )

                    # 方法列表
                    if cls.methods:
                        lines.append("**方法**:\n")
                        for method in cls.methods:
                            params = self._format_parameters(method.parameters)
                            return_type = method.return_type or "None"
                            lines.append(
                                f"- `{method.name}({params})` → `{return_type}` "
                                f"[{module.file_path}:{method.line_number}]",
                            )

                            if method.docstring:
                                first_line = method.docstring.split("\n")[0]
                                lines.append(f"  - {first_line}")

                        lines.append("")

            # 函数列表
            if module.functions:
                lines.append("#### 函数\n")
                for func in module.functions:
                    params = self._format_parameters(func.parameters)
                    return_type = func.return_type or "None"
                    lines.append(f"##### `{func.name}({params})` → `{return_type}`\n")
                    lines.append(f"**位置**: [{module.file_path}:{func.line_number}]\n")

                    if func.docstring:
                        lines.append(f"{func.docstring}\n")

                    if func.decorators:
                        lines.append(
                            f"**装饰器**: {', '.join(f'`@{d}`' for d in func.decorators)}\n",
                        )

            lines.append("---\n")

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(filepath)

    def generate_duplication_analysis(self, duplication_index: DuplicationIndex) -> str:
        """生成重复分析文档

        Args:
            duplication_index: 重复索引

        Returns:
            文档文件路径

        """
        filepath = self.output_dir / "06-duplication-analysis.md"
        lines = []

        lines.append("# 代码重复分析\n")
        lines.append(f"**总重复案例数**: {duplication_index.total_cases}\n")

        # 统计表
        lines.append("## 严重性分布\n")
        lines.append("| 严重性 | 案例数 | 描述 |")
        lines.append("|--------|--------|------|")
        lines.append(
            f"| CRITICAL | {len(duplication_index.critical)} | 几乎完全相同，需立即处理 |",
        )
        lines.append(
            f"| HIGH | {len(duplication_index.high)} | 高度相似，建议优先处理 |",
        )
        lines.append(
            f"| MEDIUM | {len(duplication_index.medium)} | 显著相似，建议考虑合并 |",
        )
        lines.append(f"| LOW | {len(duplication_index.low)} | 部分相似，可选优化 |\n")

        # CRITICAL 案例
        if duplication_index.critical:
            lines.append("## CRITICAL - 立即处理\n")
            for dup in duplication_index.critical:
                lines.extend(self._format_duplication(dup))

        # HIGH 案例
        if duplication_index.high:
            lines.append("## HIGH - 优先处理\n")
            for dup in duplication_index.high:
                lines.extend(self._format_duplication(dup))

        # MEDIUM 案例
        if duplication_index.medium:
            lines.append("## MEDIUM - 建议处理\n")
            for dup in duplication_index.medium:
                lines.extend(self._format_duplication(dup))

        # LOW 案例（折叠）
        if duplication_index.low:
            lines.append("## LOW - 可选优化\n")
            lines.append("<details>")
            lines.append("<summary>点击展开 LOW 优先级案例</summary>\n")
            for dup in duplication_index.low:
                lines.extend(self._format_duplication(dup))
            lines.append("</details>\n")

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(filepath)

    def generate_optimization_roadmap(self, roadmap: OptimizationRoadmap) -> str:
        """生成优化路线图文档

        Args:
            roadmap: 优化路线图

        Returns:
            文档文件路径

        """
        filepath = self.output_dir / "07-optimization-roadmap.md"
        lines = []

        lines.append("# 优化路线图\n")
        lines.append(f"**总优化机会数**: {len(roadmap.opportunities)}\n")

        # 快速胜利
        quick_wins = roadmap.get_quick_wins()
        if quick_wins:
            lines.append("## 快速胜利 ⚡\n")
            lines.append("*高优先级 + 低工作量*\n")
            for opp in quick_wins:
                lines.extend(self._format_optimization(opp))

        # 性能优化
        if roadmap.performance:
            lines.append("## 性能优化 🚀\n")
            for opp in sorted(roadmap.performance, key=lambda o: o.priority.value):
                lines.extend(self._format_optimization(opp))

        # 架构优化
        if roadmap.architecture:
            lines.append("## 架构优化 🏗️\n")
            for opp in sorted(roadmap.architecture, key=lambda o: o.priority.value):
                lines.extend(self._format_optimization(opp))

        # 代码质量
        if roadmap.code_quality:
            lines.append("## 代码质量 ✨\n")
            for opp in sorted(roadmap.code_quality, key=lambda o: o.priority.value):
                lines.extend(self._format_optimization(opp))

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(filepath)

    def generate_consolidation_guide(self, guide: ConsolidationGuide) -> str:
        """生成合并指南文档

        Args:
            guide: 合并指南

        Returns:
            文档文件路径

        """
        filepath = self.output_dir / "08-consolidation-guide.md"
        lines = []

        lines.append("# 模块合并指南\n")
        lines.append(f"**总合并建议数**: {len(guide.recommendations)}\n")

        # 高影响合并
        high_impact = guide.get_high_impact()
        if high_impact:
            lines.append("## 高影响合并 💥\n")
            lines.append("*合并 3+ 模块*\n")
            for rec in high_impact:
                lines.extend(self._format_merge_recommendation(rec))

        # 按风险级别分组
        for risk_level in ["low", "medium", "high"]:
            recs = guide.get_by_risk_level(risk_level)
            if recs:
                risk_name = {"low": "低风险", "medium": "中风险", "high": "高风险"}[risk_level]
                lines.append(f"## {risk_name}合并\n")
                for rec in recs:
                    lines.extend(self._format_merge_recommendation(rec))

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(filepath)

    def generate_data_flow_maps(self, data_flows: List[DataFlow]) -> str:
        """生成数据流图文档

        Args:
            data_flows: 数据流列表

        Returns:
            文档文件路径

        """
        filepath = self.output_dir / "09-data-flow-maps.md"
        lines = []

        lines.append("# 数据流图\n")
        lines.append(f"**数据流数量**: {len(data_flows)}\n")

        lines.append("## 系统概览\n")
        lines.append("```mermaid")
        lines.append("graph TB")
        lines.append("  subgraph 外部数据源")
        lines.append("    AKSHARE[AKShare]")
        lines.append("    BAOSTOCK[Baostock]")
        lines.append("    TDX[通达信]")
        lines.append("  end")
        lines.append("")
        lines.append("  subgraph 适配器层")
        lines.append("    AK_ADAPTER[AKShare Adapter]")
        lines.append("    BS_ADAPTER[Baostock Adapter]")
        lines.append("    TDX_ADAPTER[TDX Adapter]")
        lines.append("  end")
        lines.append("")
        lines.append("  subgraph 核心层")
        lines.append("    UNIFIED[Unified Manager]")
        lines.append("    ROUTER[Data Router]")
        lines.append("  end")
        lines.append("")
        lines.append("  subgraph 数据库层")
        lines.append("    TDENGINE[(TDengine<br/>市场数据)]")
        lines.append("    POSTGRES[(PostgreSQL<br/>衍生数据)]")
        lines.append("    MYSQL[(MySQL<br/>参考数据)]")
        lines.append("    REDIS[(Redis<br/>交易数据)]")
        lines.append("  end")
        lines.append("")
        lines.append("  AKSHARE --> AK_ADAPTER")
        lines.append("  BAOSTOCK --> BS_ADAPTER")
        lines.append("  TDX --> TDX_ADAPTER")
        lines.append("")
        lines.append("  AK_ADAPTER --> UNIFIED")
        lines.append("  BS_ADAPTER --> UNIFIED")
        lines.append("  TDX_ADAPTER --> UNIFIED")
        lines.append("")
        lines.append("  UNIFIED --> ROUTER")
        lines.append("")
        lines.append("  ROUTER --> TDENGINE")
        lines.append("  ROUTER --> POSTGRES")
        lines.append("  ROUTER --> MYSQL")
        lines.append("  ROUTER --> REDIS")
        lines.append("```\n")

        # 详细数据流
        for flow in data_flows:
            lines.append(f"## {flow.name}\n")
            lines.append(f"**ID**: {flow.id}")
            lines.append(f"**描述**: {flow.description}\n")

            if flow.data_classification:
                lines.append(f"**数据分类**: {flow.data_classification}")

            if flow.database_target:
                lines.append(f"**目标数据库**: {flow.database_target}\n")

            lines.append("### 流程步骤\n")
            for i, step in enumerate(flow.steps, 1):
                module = step.get("module", "Unknown")
                function = step.get("function", "Unknown")
                action = step.get("action", "")
                lines.append(f"{i}. **{module}**.`{function}()` - {action}")

            lines.append("\n---\n")

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(filepath)

    def _format_parameters(self, parameters: List) -> str:
        """格式化参数列表"""
        if not parameters:
            return ""

        param_strs = []
        for param in parameters:
            if hasattr(param, "name"):
                if param.type_annotation:
                    if param.default_value:
                        param_strs.append(
                            f"{param.name}: {param.type_annotation} = {param.default_value}",
                        )
                    else:
                        param_strs.append(f"{param.name}: {param.type_annotation}")
                elif param.default_value:
                    param_strs.append(f"{param.name}={param.default_value}")
                else:
                    param_strs.append(param.name)

        return ", ".join(param_strs)

    def _format_duplication(self, dup: DuplicationCase) -> List[str]:
        """格式化重复案例"""
        lines = []

        lines.append(f"### {dup.id}\n")
        lines.append(f"**描述**: {dup.description}")
        lines.append(f"**Token 相似度**: {dup.token_similarity:.1%}")
        lines.append(f"**AST 相似度**: {dup.ast_similarity:.1%}\n")

        lines.append("**重复位置**:\n")
        for block in dup.blocks:
            lines.append(f"- `{block.file_path}:{block.start_line}-{block.end_line}`")

        lines.append("")
        lines.append("**合并建议**:\n")
        lines.append(f"{dup.merge_suggestion}\n")
        lines.append("---\n")

        return lines

    def _format_optimization(self, opp: OptimizationOpportunity) -> List[str]:
        """格式化优化机会"""
        lines = []

        priority_emoji = {"p0": "🔴", "p1": "🟠", "p2": "🟡", "p3": "🟢"}
        emoji = priority_emoji.get(opp.priority.value, "⚪")

        lines.append(f"### {emoji} {opp.title}\n")
        lines.append(f"**ID**: {opp.id}")
        lines.append(f"**优先级**: {opp.priority.value.upper()}")
        lines.append(f"**工作量**: {opp.effort_estimate}\n")

        lines.append(f"**当前状态**:\n{opp.current_state}\n")
        lines.append(f"**建议改进**:\n{opp.proposed_change}\n")
        lines.append(f"**预期影响**:\n{opp.expected_impact}\n")

        if opp.affected_modules:
            lines.append("**受影响模块**:")
            for module in opp.affected_modules:
                lines.append(f"- `{module}`")
            lines.append("")

        lines.append("---\n")

        return lines

    def _format_merge_recommendation(self, rec: MergeRecommendation) -> List[str]:
        """格式化合并建议"""
        lines = []

        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        emoji = risk_emoji.get(rec.risk_level, "⚪")

        lines.append(f"### {emoji} {rec.title}\n")
        lines.append(f"**ID**: {rec.id}")
        lines.append(f"**风险级别**: {rec.risk_level.upper()}")
        lines.append(f"**工作量**: {rec.effort_estimate}\n")

        lines.append("**待合并模块**:")
        for module in rec.modules_to_merge:
            lines.append(f"- `{module}`")
        lines.append("")

        if rec.new_module_name:
            lines.append(f"**新模块名**: `{rec.new_module_name}`\n")

        lines.append(f"**通用功能**:\n{rec.common_functionality}\n")
        lines.append(f"**合并策略**:\n{rec.merge_strategy}\n")

        if rec.migration_steps:
            lines.append("**迁移步骤**:")
            for i, step in enumerate(rec.migration_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")

        lines.append("---\n")

        return lines


if __name__ == "__main__":
    # 测试
    output_dir = DEFAULT_OUTPUT_DIR
    writer = MarkdownWriter(output_dir)
    print(f"Markdown writer initialized with output dir: {output_dir}")
