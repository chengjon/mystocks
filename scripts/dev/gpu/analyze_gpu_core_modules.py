#!/usr/bin/env python3
"""分析GPU核心计算模块
Phase 6.3.1 - 分析现有GPU核心计算模块

识别重构目标、优化机会和技术债务
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class GPUCoreAnalyzer:
    """GPU核心模块分析器"""

    def __init__(self):
        self.project_root = Path()
        self.analysis_results = {}

        # GPU核心模块路径
        self.core_module_paths = [
            "src/gpu/accelerated/",
            "src/gpu/core/",
            "src/gpu/api_system/",
        ]

    def analyze_gpu_core_modules(self) -> Dict[str, Any]:
        """分析GPU核心模块"""
        print("🔍 分析GPU核心计算模块...")

        analysis_sections = [
            ("模块规模分析", self.analyze_module_scale),
            ("代码质量分析", self.analyze_code_quality),
            ("性能热点分析", self.analyze_performance_hotspots),
            ("依赖关系分析", self.analyze_dependencies),
            ("重构优先级分析", self.analyze_refactoring_priorities),
        ]

        for section_name, analysis_func in analysis_sections:
            print(f"   📊 {section_name}...")
            try:
                result = analysis_func()
                self.analysis_results[section_name] = result
                print(f"   ✅ {section_name}完成")
            except Exception as e:
                print(f"   ❌ {section_name}失败: {e}")
                self.analysis_results[section_name] = {
                    "success": False,
                    "error": str(e),
                }

        return self.generate_comprehensive_analysis()

    def analyze_module_scale(self) -> Dict[str, Any]:
        """分析模块规模"""
        module_stats = {}
        total_files = 0
        total_lines = 0
        total_size = 0

        for module_path in self.core_module_paths:
            if not os.path.exists(module_path):
                continue

            stats = self._calculate_directory_stats(module_path)
            module_stats[module_path] = stats

            total_files += stats["file_count"]
            total_lines += stats["line_count"]
            total_size += stats["total_size_bytes"]

        return {
            "success": True,
            "module_statistics": module_stats,
            "summary": {
                "total_files": total_files,
                "total_lines": total_lines,
                "total_size_kb": total_size / 1024,
                "average_lines_per_file": total_lines / total_files if total_files > 0 else 0,
            },
        }

    def analyze_code_quality(self) -> Dict[str, Any]:
        """分析代码质量"""
        quality_issues = {
            "complex_functions": [],
            "large_files": [],
            "missing_documentation": [],
            "potential_bugs": [],
            "performance_issues": [],
        }

        total_files_analyzed = 0

        for module_path in self.core_module_paths:
            if not os.path.exists(module_path):
                continue

            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        file_analysis = self._analyze_file_quality(file_path)

                        total_files_analyzed += 1
                        for issue_type, issues in file_analysis.items():
                            if issues:
                                quality_issues[issue_type].extend(issues)

        return {
            "success": True,
            "files_analyzed": total_files_analyzed,
            "quality_issues": quality_issues,
            "total_issues": sum(len(issues) for issues in quality_issues.values()),
        }

    def analyze_performance_hotspots(self) -> Dict[str, Any]:
        """分析性能热点"""
        performance_patterns = {
            "nested_loops": [],
            "large_array_operations": [],
            "synchronous_gpu_calls": [],
            "memory_allocations": [],
            "file_io_operations": [],
        }

        total_files_analyzed = 0

        for module_path in self.core_module_paths:
            if not os.path.exists(module_path):
                continue

            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        file_analysis = self._analyze_performance_patterns(file_path)

                        total_files_analyzed += 1
                        for pattern_type, occurrences in file_analysis.items():
                            if occurrences:
                                performance_patterns[pattern_type].extend(occurrences)

        return {
            "success": True,
            "files_analyzed": total_files_analyzed,
            "performance_hotspots": performance_patterns,
            "total_hotspots": sum(len(occurrences) for occurrences in performance_patterns.values()),
        }

    def analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖关系"""
        dependencies = {
            "external_libraries": set(),
            "internal_dependencies": set(),
            "circular_dependencies": [],
            "missing_dependencies": [],
        }

        total_files_analyzed = 0

        for module_path in self.core_module_paths:
            if not os.path.exists(module_path):
                continue

            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        file_deps = self._analyze_file_dependencies(file_path)

                        total_files_analyzed += 1
                        dependencies["external_libraries"].update(file_deps["external"])
                        dependencies["internal_dependencies"].update(
                            file_deps["internal"],
                        )

        # Convert sets to lists for JSON serialization
        dependencies["external_libraries"] = list(dependencies["external_libraries"])
        dependencies["internal_dependencies"] = list(
            dependencies["internal_dependencies"],
        )

        return {
            "success": True,
            "files_analyzed": total_files_analyzed,
            "dependencies": dependencies,
        }

    def analyze_refactoring_priorities(self) -> Dict[str, Any]:
        """分析重构优先级"""
        priorities = {
            "high_priority": [],  # 性能关键或有严重问题
            "medium_priority": [],  # 代码质量问题
            "low_priority": [],  # 优化机会
        }

        # 基于之前的分析结果确定优先级
        if "代码质量分析" in self.analysis_results:
            quality_issues = self.analysis_results["代码质量分析"]["quality_issues"]

            # 高优先级：潜在bug和性能问题
            priorities["high_priority"].extend(quality_issues.get("potential_bugs", []))
            priorities["high_priority"].extend(
                quality_issues.get("performance_issues", []),
            )

            # 中优先级：复杂函数和大文件
            priorities["medium_priority"].extend(
                quality_issues.get("complex_functions", []),
            )
            priorities["medium_priority"].extend(quality_issues.get("large_files", []))

            # 低优先级：文档问题
            priorities["low_priority"].extend(
                quality_issues.get("missing_documentation", []),
            )

        if "性能热点分析" in self.analysis_results:
            hotspots = self.analysis_results["性能热点分析"]["performance_hotspots"]

            # 高优先级：嵌套循环和同步GPU调用
            priorities["high_priority"].extend(hotspots.get("nested_loops", []))
            priorities["high_priority"].extend(
                hotspots.get("synchronous_gpu_calls", []),
            )

            # 中优先级：大数组操作
            priorities["medium_priority"].extend(
                hotspots.get("large_array_operations", []),
            )

            # 低优先级：内存分配和文件IO
            priorities["low_priority"].extend(hotspots.get("memory_allocations", []))
            priorities["low_priority"].extend(hotspots.get("file_io_operations", []))

        return {
            "success": True,
            "refactoring_priorities": priorities,
            "summary": {
                "high_priority_count": len(priorities["high_priority"]),
                "medium_priority_count": len(priorities["medium_priority"]),
                "low_priority_count": len(priorities["low_priority"]),
            },
        }

    def _calculate_directory_stats(self, directory: str) -> Dict[str, Any]:
        """计算目录统计信息"""
        file_count = 0
        line_count = 0
        total_size = 0

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            lines = f.readlines()
                            file_count += 1
                            line_count += len(lines)
                            total_size += os.path.getsize(file_path)
                    except:
                        continue

        return {
            "file_count": file_count,
            "line_count": line_count,
            "total_size_bytes": total_size,
        }

    def _analyze_file_quality(self, file_path: str) -> Dict[str, List[str]]:
        """分析单个文件的代码质量"""
        issues = {
            "complex_functions": [],
            "large_files": [],
            "missing_documentation": [],
            "potential_bugs": [],
            "performance_issues": [],
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 检查文件大小
            if len(lines) > 500:  # 大于500行认为是大文件
                issues["large_files"].append(f"{file_path}: {len(lines)} lines")

            # 检查函数复杂度
            function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
            functions = re.finditer(function_pattern, content)

            for match in functions:
                func_start = match.start()
                func_name = match.group(1)

                # 简单检查函数长度（基于缩进）
                func_lines = 0
                max_nested_level = 0
                current_nested = 0

                for i in range(match.end(), len(content)):
                    if content[i] == "\n":
                        continue

                    if content[i : i + 4] == "    ":
                        current_nested = 1
                    elif content[i : i + 8] == "        ":
                        current_nested = 2
                    elif content[i : i + 12] == "            ":
                        current_nested = 3

                    max_nested_level = max(max_nested_level, current_nested)

                    if content[i] == "\n":
                        if current_nested == 0 and i > match.end() + 10:
                            break
                        func_lines += 1

                if func_lines > 50:  # 大于50行认为是复杂函数
                    issues["complex_functions"].append(
                        f"{file_path}: {func_name} ({func_lines} lines, nested: {max_nested_level})",
                    )

                # 检查潜在bug
                if "eval(" in content or "exec(" in content:
                    issues["potential_bugs"].append(
                        f"{file_path}: Contains eval/exec usage",
                    )

            # 检查文档
            if not content.startswith('"""') and not content.startswith("'''"):
                issues["missing_documentation"].append(
                    f"{file_path}: Missing module docstring",
                )

            # 检查性能问题
            if content.count("for ") > 10:  # 过多的for循环
                issues["performance_issues"].append(f"{file_path}: High loop count")

            if ".cuda()" in content or ".to(device)" in content:
                issues["performance_issues"].append(
                    f"{file_path}: Direct GPU calls without HAL",
                )

        except Exception as e:
            issues["potential_bugs"].append(f"{file_path}: Analysis failed - {e}")

        return issues

    def _analyze_performance_patterns(self, file_path: str) -> Dict[str, List[str]]:
        """分析性能模式"""
        patterns = {
            "nested_loops": [],
            "large_array_operations": [],
            "synchronous_gpu_calls": [],
            "memory_allocations": [],
            "file_io_operations": [],
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line_content = line.strip()

                # 嵌套循环检测
                if "for " in line_content and i > 1:
                    prev_lines = "".join(lines[max(0, i - 10) : i])
                    if prev_lines.count("for ") >= 1:
                        patterns["nested_loops"].append(
                            f"{file_path}:{i} - Nested loop detected",
                        )

                # 大数组操作
                if any(keyword in line_content for keyword in ["np.zeros(", "np.ones(", "np.empty(", "cupy."]):
                    patterns["large_array_operations"].append(
                        f"{file_path}:{i} - Large array operation",
                    )

                # 同步GPU调用
                if any(keyword in line_content for keyword in [".cuda()", ".to(device)", "cuda.synchronize()"]):
                    patterns["synchronous_gpu_calls"].append(
                        f"{file_path}:{i} - Synchronous GPU call",
                    )

                # 内存分配
                if "allocate" in line_content or "malloc" in line_content:
                    patterns["memory_allocations"].append(
                        f"{file_path}:{i} - Memory allocation",
                    )

                # 文件IO操作
                if any(keyword in line_content for keyword in ["open(", "with open", "read(", "write("]):
                    patterns["file_io_operations"].append(
                        f"{file_path}:{i} - File I/O operation",
                    )

        except Exception:
            pass

        return patterns

    def _analyze_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """分析文件依赖"""
        dependencies = {"external": [], "internal": []}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 查找import语句
            import_patterns = [
                r"import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
                r"from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import",
            ]

            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    module_name = match.group(1)

                    if module_name.startswith("src.") or module_name.startswith(".."):
                        dependencies["internal"].append(f"{file_path}: {module_name}")
                    elif not module_name.startswith("."):
                        dependencies["external"].append(f"{file_path}: {module_name}")

        except Exception:
            pass

        return dependencies

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """生成综合分析报告"""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "analysis_results": self.analysis_results,
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            "total_modules_analyzed": len(
                [p for p in self.core_module_paths if os.path.exists(p)],
            ),
            "key_findings": [],
        }

        if "模块规模分析" in self.analysis_results:
            scale_summary = self.analysis_results["模块规模分析"]["summary"]
            summary["key_findings"].append(
                f"总代码量: {scale_summary['total_lines']:,} 行 ({scale_summary['total_files']} 个文件)",
            )

        if "代码质量分析" in self.analysis_results:
            quality_summary = self.analysis_results["代码质量分析"]
            summary["key_findings"].append(
                f"代码质量问题: {quality_summary['total_issues']} 个问题在 {quality_summary['files_analyzed']} 个文件中",
            )

        if "性能热点分析" in self.analysis_results:
            perf_summary = self.analysis_results["性能热点分析"]
            summary["key_findings"].append(
                f"性能热点: {perf_summary['total_hotspots']} 个热点需要优化",
            )

        if "重构优先级分析" in self.analysis_results:
            priority_summary = self.analysis_results["重构优先级分析"]["summary"]
            summary["key_findings"].append(
                f"重构优先级: {priority_summary['high_priority_count']} 高优先级, {priority_summary['medium_priority_count']} 中优先级",
            )

        return summary

    def _generate_recommendations(self) -> List[str]:
        """生成重构建议"""
        recommendations = []

        recommendations.extend(
            [
                "Phase 6.3.2: 优化TransformKernelEngine实现 - 修复数据变换内核的性能问题",
                "Phase 6.3.3: 优化MemoryPool内存管理 - 提高内存分配和释放性能",
                "Phase 6.3.4: GPU核心算法优化 - 针对大矩阵操作进行算法优化",
                "Phase 6.3.5: 核心功能重构测试验证 - 确保重构后的性能提升和稳定性",
            ],
        )

        if "重构优先级分析" in self.analysis_results:
            priority_data = self.analysis_results["重构优先级分析"]
            if "summary" in priority_data:
                high_priority_count = priority_data["summary"].get(
                    "high_priority_count",
                    0,
                )
                if high_priority_count > 5:
                    recommendations.append("优先处理高优先级重构项目，减少技术债务")

        return recommendations


def main():
    """主函数"""
    print("🚀 Phase 6.3.1 GPU核心计算模块分析")
    print("=" * 60)

    analyzer = GPUCoreAnalyzer()

    # 执行分析
    analysis = analyzer.analyze_gpu_core_modules()

    # 保存分析报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"gpu_core_modules_analysis_{timestamp}.json"

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n📄 分析报告已保存: {report_path}")
    except Exception as e:
        print(f"\n❌ 保存报告失败: {e}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("📊 GPU核心模块分析摘要")
    print("=" * 60)

    if "summary" in analysis:
        for finding in analysis["summary"]["key_findings"]:
            print(f"🔍 {finding}")

    if "recommendations" in analysis:
        print("\n💡 重构建议:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {rec}")

    print("\n" + "=" * 60)

    return analysis


if __name__ == "__main__":
    analysis = main()
