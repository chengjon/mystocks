#!/usr/bin/env python3
"""
模块依赖关系分析脚本
使用AST分析源代码，生成依赖图和测试顺序推荐
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

# 计算项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class ModuleDependencyAnalyzer:
    """模块依赖关系分析器"""

    def __init__(self, source_dirs: List[str]):
        """初始化分析器

        Args:
            source_dirs: 要分析的源代码目录列表
        """
        self.source_dirs = [Path(d) for d in source_dirs]
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.modules: Set[str] = set()

    def analyze(self):
        """分析所有模块的依赖关系"""
        print("🔍 正在分析模块依赖关系...")

        for source_dir in self.source_dirs:
            if not source_dir.exists():
                print(f"⚠️  目录不存在: {source_dir}")
                continue

            # 遍历所有Python文件
            for py_file in source_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue

                module_name = self._get_module_name(py_file, source_dir)
                self.modules.add(module_name)

                # 分析导入
                imports = self._extract_imports(py_file)
                for imp in imports:
                    # 只记录项目内部的导入
                    if imp.startswith("src.") or imp.startswith("web.backend.app."):
                        self.dependencies[module_name].add(imp)
                        self.reverse_dependencies[imp].add(module_name)

        print(f"✅ 分析完成：发现 {len(self.modules)} 个模块")
        print(f"   - 依赖关系数: {sum(len(deps) for deps in self.dependencies.values())}")

    def _get_module_name(self, file_path: Path, base_dir: Path) -> str:
        """获取模块名称

        Args:
            file_path: 文件路径
            base_dir: 基础目录

        Returns:
            模块名称（如 src.core.config）
        """
        relative = file_path.relative_to(base_dir.parent)
        parts = list(relative.parts[:-1]) + [relative.stem]

        # 移除 __init__
        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """提取文件中的导入语句

        Args:
            file_path: Python文件路径

        Returns:
            导入的模块名称集合
        """
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

        except Exception as e:
            print(f"⚠️  解析错误 {file_path}: {e}")

        return imports

    def topological_sort(self) -> List[str]:
        """拓扑排序模块（依赖项优先）

        Returns:
            排序后的模块列表
        """
        # 计算入度
        in_degree = {module: 0 for module in self.modules}
        for module in self.modules:
            for dep in self.dependencies.get(module, []):
                if dep in self.modules:
                    in_degree[module] += 1

        # BFS拓扑排序
        queue = deque([m for m in self.modules if in_degree[m] == 0])
        sorted_modules = []

        while queue:
            module = queue.popleft()
            sorted_modules.append(module)

            # 更新依赖此模块的其他模块
            for dependent in self.reverse_dependencies.get(module, []):
                if dependent in self.modules:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        return sorted_modules

    def get_test_layers(self) -> List[List[str]]:
        """获取测试层级（每层可以并行测试）

        Returns:
            分层的模块列表
        """
        layers = []
        remaining = set(self.modules)

        while remaining:
            # 找出当前层：没有未测试依赖的模块
            current_layer = []
            for module in remaining:
                deps = self.dependencies.get(module, set())
                if not deps.intersection(remaining):
                    current_layer.append(module)

            if not current_layer:
                # 有循环依赖或孤立模块
                current_layer = list(remaining)

            layers.append(sorted(current_layer))
            remaining -= set(current_layer)

        return layers

    def categorize_modules(self) -> Dict[str, List[str]]:
        """按功能分类模块

        Returns:
            分类字典
        """
        categories = {
            "core": [],
            "data_access": [],
            "adapters": [],
            "api": [],
            "services": [],
            "monitoring": [],
            "storage": [],
            "other": []
        }

        for module in sorted(self.modules):
            if "core" in module:
                categories["core"].append(module)
            elif "data_access" in module:
                categories["data_access"].append(module)
            elif "adapter" in module or "interfaces.adapters" in module:
                categories["adapters"].append(module)
            elif "web.backend.app.api" in module:
                categories["api"].append(module)
            elif "services" in module:
                categories["services"].append(module)
            elif "monitoring" in module:
                categories["monitoring"].append(module)
            elif "storage" in module:
                categories["storage"].append(module)
            else:
                categories["other"].append(module)

        return categories

    def generate_report(self, output_path: str):
        """生成测试顺序推荐报告

        Args:
            output_path: 输出文件路径
        """
        print("\n📝 正在生成测试顺序推荐报告...")

        # 获取分层和分类
        layers = self.get_test_layers()
        categories = self.categorize_modules()

        # 生成报告
        report = []
        report.append("# 模块依赖分析与测试顺序推荐")
        report.append("")
        report.append(f"**生成时间**: {self._get_timestamp()}")
        report.append(f"**分析模块数**: {len(self.modules)}")
        report.append(f"**依赖关系数**: {sum(len(deps) for deps in self.dependencies.values())}")
        report.append("")

        # 1. 概览统计
        report.append("## 📊 模块分类统计")
        report.append("")
        report.append("| 分类 | 模块数 | 说明 |")
        report.append("|------|--------|------|")

        category_descriptions = {
            "core": "核心业务逻辑",
            "data_access": "数据访问层",
            "adapters": "数据源适配器",
            "api": "API端点",
            "services": "业务服务",
            "monitoring": "监控系统",
            "storage": "存储层",
            "other": "其他模块"
        }

        for cat, desc in category_descriptions.items():
            count = len(categories[cat])
            if count > 0:
                report.append(f"| {cat.capitalize()} | {count} | {desc} |")

        report.append("")

        # 2. 循环依赖检查
        report.append("## 🔍 循环依赖检查")
        report.append("")

        sorted_modules = self.topological_sort()
        if len(sorted_modules) == len(self.modules):
            report.append("✅ **未检测到循环依赖** - 项目架构良好！")
        else:
            missing = set(self.modules) - set(sorted_modules)
            report.append(f"⚠️ **检测到可能的循环依赖**")
            report.append("")
            report.append(f"未能排序的模块 ({len(missing)}个):")
            for m in sorted(missing):
                report.append(f"- `{m}`")

        report.append("")

        # 3. 测试层级推荐
        report.append("## 🎯 测试层级推荐")
        report.append("")
        report.append("以下层级中的模块可以**并行测试**，但必须按层级顺序执行：")
        report.append("")

        for idx, layer in enumerate(layers, 1):
            report.append(f"### Layer {idx} ({len(layer)}个模块)")
            report.append("")
            report.append("**可并行测试的模块**:")
            report.append("")
            for module in layer:
                report.append(f"- `{module}`")
            report.append("")

        # 4. 按功能分类的测试顺序
        report.append("## 📋 按功能分类的测试顺序")
        report.append("")

        priority_order = ["core", "storage", "data_access", "adapters", "services", "api", "monitoring", "other"]

        for priority, cat in enumerate(priority_order, 1):
            modules = categories.get(cat, [])
            if modules:
                report.append(f"### Priority {priority}: {cat.capitalize()} ({len(modules)}个模块)")
                report.append("")
                report.append(f"**{category_descriptions.get(cat, '其他')}**")
                report.append("")

                # 显示前10个模块
                for module in modules[:10]:
                    deps = self.dependencies.get(module, set())
                    internal_deps = [d for d in deps if d in self.modules]
                    if internal_deps:
                        report.append(f"- `{module}` (依赖 {len(internal_deps)}个模块)")
                    else:
                        report.append(f"- `{module}` (无内部依赖)")

                if len(modules) > 10:
                    report.append(f"- ... 还有 {len(modules) - 10} 个模块")

                report.append("")

        # 5. 测试实施建议
        report.append("## 🚀 测试实施建议")
        report.append("")
        report.append("### Phase 1: 核心模块测试 (Week 2)")
        report.append("")
        report.append("**优先测试核心模块**，因为它们是其他模块的依赖基础：")
        report.append("")
        for module in categories["core"][:5]:
            report.append(f"- `{module}`")
        report.append("")

        report.append("### Phase 2: 数据访问层测试 (Week 3)")
        report.append("")
        report.append("**测试数据访问层**，验证与数据库的交互：")
        report.append("")
        for module in categories["data_access"][:5]:
            report.append(f"- `{module}`")
        report.append("")

        report.append("### Phase 3: 适配器测试 (Week 4)")
        report.append("")
        report.append("**测试数据源适配器**，使用Mock避免外部API调用：")
        report.append("")
        for module in categories["adapters"][:5]:
            report.append(f"- `{module}`")
        report.append("")

        report.append("### Phase 4: API端点测试 (Week 5)")
        report.append("")
        report.append("**测试API端点**，验证完整的请求/响应周期：")
        report.append("")
        for module in categories["api"][:5]:
            report.append(f"- `{module}`")
        report.append("")

        # 6. 关键注意事项
        report.append("## ⚠️ 测试注意事项")
        report.append("")
        report.append("1. **依赖优先**: 先测试依赖项，再测试依赖它的模块")
        report.append("2. **并行执行**: 同一层级的模块可以并行测试以提高效率")
        report.append("3. **Mock外部依赖**: 对外部API和数据库使用Mock以提高测试速度")
        report.append("4. **增量覆盖**: 每个模块目标覆盖率80%+")
        report.append("5. **持续监控**: 使用覆盖率工具跟踪进度")
        report.append("")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        print(f"✅ 报告已保存到: {output_path}")

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    print("=" * 60)
    print("模块依赖关系分析工具")
    print("=" * 60)

    # 分析src/和web/backend/app/目录
    analyzer = ModuleDependencyAnalyzer([
        os.path.join(project_root, "src"),
        os.path.join(project_root, "web/backend/app")
    ])

    # 执行分析
    analyzer.analyze()

    # 生成报告
    output_path = os.path.join(project_root, "docs/reports/TEST_ORDER_RECOMMENDATION.md")
    analyzer.generate_report(output_path)

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📄 查看报告: {output_path}")
    print(f"📊 总模块数: {len(analyzer.modules)}")
    print(f"🔗 总依赖数: {sum(len(deps) for deps in analyzer.dependencies.values())}")
    print()


if __name__ == '__main__':
    main()
