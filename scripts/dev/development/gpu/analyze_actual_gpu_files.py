#!/usr/bin/env python3
"""
分析实际的GPU文件
识别需要迁移的关键文件，制定具体的迁移计划
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class GPUFileInfo:
    """GPU文件信息"""

    path: str
    name: str
    size: int
    has_direct_gpu: bool = False
    gpu_libraries: List[str] = field(default_factory=list)
    migration_complexity: str = "MEDIUM"
    migration_priority: str = "MEDIUM"
    recommended_action: str = ""


class GPUFileAnalyzer:
    """GPU文件分析器"""

    def __init__(self):
        self.gpu_files: List[GPUFileInfo] = []
        self.analysis_results = {}

    def analyze_gpu_files(self) -> Dict[str, Any]:
        """分析GPU文件"""
        print("🔍 分析实际GPU文件...")

        # 1. 查找所有GPU相关文件
        gpu_files = self._find_gpu_files()

        if not gpu_files:
            print("   未找到GPU文件")
            return {}

        # 2. 分析每个文件
        analyzed_files = []
        for file_path in gpu_files:
            file_info = self._analyze_gpu_file(file_path)
            analyzed_files.append(file_info)
            print(f"   📁 分析: {file_info.name} ({file_info.size:,} bytes)")

        self.gpu_files = analyzed_files

        # 3. 生成分析结果
        results = self._generate_analysis_results()

        self.analysis_results = results
        return results

    def _find_gpu_files(self) -> List[str]:
        """查找GPU文件"""
        gpu_files = []
        project_root = Path("src")

        # 递归查找Python文件
        for py_file in project_root.rglob("*.py"):
            if "gpu" in str(py_file).lower():
                gpu_files.append(str(py_file))

        # 按大小排序
        gpu_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
        return gpu_files

    def _analyze_gpu_file(self, file_path: str) -> GPUFileInfo:
        """分析单个GPU文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"   ⚠️  无法读取 {file_path}: {e}")
            return GPUFileInfo(
                path=file_path,
                name=os.path.basename(file_path),
                size=0,
                migration_complexity="HIGH",
                recommended_action="File read error - manual review required",
            )

        file_size = len(content)
        file_name = os.path.basename(file_path)

        # 检测GPU库使用
        gpu_libraries = self._detect_gpu_libraries(content)

        # 检测直接GPU调用
        has_direct_gpu = self._detect_direct_gpu_calls(content)

        # 确定迁移复杂度和优先级
        complexity, priority = self._assess_migration_complexity(
            file_path, content, has_direct_gpu, gpu_libraries
        )

        # 推荐行动
        recommended_action = self._recommend_action(
            file_path, content, has_direct_gpu, gpu_libraries
        )

        return GPUFileInfo(
            path=file_path,
            name=file_name,
            size=file_size,
            has_direct_gpu=has_direct_gpu,
            gpu_libraries=gpu_libraries,
            migration_complexity=complexity,
            migration_priority=priority,
            recommended_action=recommended_action,
        )

    def _detect_gpu_libraries(self, content: str) -> List[str]:
        """检测GPU库使用"""
        gpu_libs = []

        # GPU库模式
        gpu_patterns = [
            (r"import\s+cupy", "CuPy"),
            (r"import\s+torch", "PyTorch"),
            (r"import\s+numba", "Numba"),
            (r"import\s+pycuda", "PyCUDA"),
            (r"from\s+cupy", "CuPy"),
            (r"from\s+torch", "PyTorch"),
            (r"from\s+numba", "Numba"),
            (r"cuda\.", "CUDA Direct"),
            (r"\.cuda\(\)", "PyTorch CUDA"),
            (r"\.to\(['\"]cuda", "PyTorch CUDA"),
        ]

        for pattern, lib_name in gpu_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                gpu_libs.append(lib_name)

        return list(set(gpu_libs))

    def _detect_direct_gpu_calls(self, content: str) -> bool:
        """检测直接GPU调用"""
        direct_patterns = [
            r"cp\.array\(",
            r"cp\.zeros\(",
            r"cp\.ones\(",
            r"torch\.tensor\(",
            r"torch\.zeros\(",
            r"torch\.ones\(",
            r"cuda\.Device\(",
            r"torch\.cuda\.device\(",
            r"\.cuda\(\)",
            r"\.to\(['\"]cuda",
            r"torch\.no_grad\(\)",
        ]

        for pattern in direct_patterns:
            if re.search(pattern, content):
                return True

        return False

    def _assess_migration_complexity(
        self,
        file_path: str,
        content: str,
        has_direct_gpu: bool,
        gpu_libraries: List[str],
    ) -> Tuple[str, str]:
        """评估迁移复杂度和优先级"""
        file_size = len(content)
        file_name = os.path.basename(file_path).lower()

        # 复杂度评估
        complexity = "MEDIUM"  # 默认

        if file_size > 2000:  # 大文件
            complexity = "HIGH"
        elif has_direct_gpu and len(gpu_libraries) > 2:  # 多GPU库
            complexity = "HIGH"
        elif not has_direct_gpu and not gpu_libraries:
            complexity = "LOW"

        # 优先级评估
        priority = "MEDIUM"  # 默认

        if file_name.startswith("gpu_") and (
            "manager" in file_name or "resource" in file_name
        ):
            priority = "HIGH"
        elif file_name.startswith("gpu_") and (
            "api" in file_name or "server" in file_name
        ):
            priority = "HIGH"
        elif file_name.startswith("gpu_") and (
            "accelerated" in file_name or "engine" in file_name
        ):
            priority = "HIGH"
        elif "test" in file_name:
            priority = "LOW"

        return complexity, priority

    def _recommend_action(
        self,
        file_path: str,
        content: str,
        has_direct_gpu: bool,
        gpu_libraries: List[str],
    ) -> str:
        """推荐行动"""
        file_name = os.path.basename(file_path).lower()

        if not has_direct_gpu and not gpu_libraries:
            return "No GPU usage - no migration needed"

        if "api_system" in file_path or "server" in file_name:
            return "High priority - replace GPU calls with HAL API"

        if "test" in file_name:
            return "Low priority - update test to use HAL interfaces"

        if "manager" in file_name or "resource" in file_name:
            return "High priority - migrate to GPUResourceManager"

        if "accelerated" in file_name or "engine" in file_name:
            return "High priority - migrate to kernel engines"

        if has_direct_gpu:
            return "Medium priority - replace direct GPU calls with HAL layer"

        return "Review for HAL integration opportunities"

    def _generate_analysis_results(self) -> Dict[str, Any]:
        """生成分析结果"""
        total_files = len(self.gpu_files)
        total_size = sum(f.size for f in self.gpu_files)
        files_with_gpu = sum(1 for f in self.gpu_files if f.has_direct_gpu)

        # HAL层分布统计
        hal_layer_stats = defaultdict(int)
        for file_info in self.gpu_files:
            if (
                "manager" in file_info.name.lower()
                or "resource" in file_info.name.lower()
            ):
                hal_layer_stats["GPUResourceManager"] += 1
            elif (
                "accelerated" in file_info.name.lower()
                or "engine" in file_info.name.lower()
            ):
                hal_layer_stats["AcceleratedEngine"] += 1
            elif "api" in file_info.name.lower() or "server" in file_info.name.lower():
                hal_layer_stats["APIServer"] += 1
            else:
                hal_layer_stats["General"] += 1

        # 优先级分布
        priority_stats = defaultdict(int)
        for file_info in self.gpu_files:
            priority_stats[file_info.migration_priority] += 1

        # 复杂度分布
        complexity_stats = defaultdict(int)
        for file_info in self.gpu_files:
            complexity_stats[file_info.migration_complexity] += 1

        # GPU库使用统计
        gpu_lib_stats = defaultdict(int)
        for file_info in self.gpu_files:
            for lib in file_info.gpu_libraries:
                gpu_lib_stats[lib] += 1

        # 生成迁移计划
        migration_plan = self._create_migration_plan()

        return {
            "summary": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "files_with_direct_gpu": files_with_gpu,
                "gpu_usage_percentage": (files_with_gpu / total_files * 100)
                if total_files > 0
                else 0,
            },
            "statistics": {
                "priority_distribution": dict(priority_stats),
                "complexity_distribution": dict(complexity_stats),
                "hal_layer_distribution": dict(hal_layer_stats),
                "gpu_library_distribution": dict(gpu_lib_stats),
            },
            "files": [
                {
                    "path": f.path,
                    "name": f.name,
                    "size": f.size,
                    "has_direct_gpu": f.has_direct_gpu,
                    "gpu_libraries": f.gpu_libraries,
                    "complexity": f.migration_complexity,
                    "priority": f.migration_priority,
                    "recommended_action": f.recommended_action,
                }
                for f in self.gpu_files
            ],
            "migration_plan": migration_plan,
        }

    def _create_migration_plan(self) -> Dict[str, Any]:
        """创建迁移计划"""
        # 按优先级分组
        high_priority = [f for f in self.gpu_files if f.migration_priority == "HIGH"]
        medium_priority = [
            f for f in self.gpu_files if f.migration_priority == "MEDIUM"
        ]
        low_priority = [f for f in self.gpu_files if f.migration_priority == "LOW"]

        # 关键文件识别
        key_files = []
        for f in self.gpu_files:
            if any(
                keyword in f.name.lower()
                for keyword in [
                    "gpu_acceleration_engine",
                    "gpu_resource_manager",
                    "main_server",
                    "integrated_services",
                    "acceleration_engine",
                ]
            ):
                key_files.append(f)

        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Key Infrastructure Files",
                    "files": key_files,
                    "count": len(key_files),
                    "description": "Critical GPU infrastructure files",
                    "estimated_days": 3,
                },
                {
                    "phase": 2,
                    "name": "High Priority Files",
                    "files": high_priority,
                    "count": len(high_priority),
                    "description": "High priority GPU files",
                    "estimated_days": 2,
                },
                {
                    "phase": 3,
                    "name": "Medium Priority Files",
                    "files": medium_priority,
                    "count": len(medium_priority),
                    "description": "Standard priority GPU files",
                    "estimated_days": 3,
                },
                {
                    "phase": 4,
                    "name": "Low Priority Files",
                    "files": low_priority,
                    "count": len(low_priority),
                    "description": "Low priority files including tests",
                    "estimated_days": 2,
                },
            ],
            "total_files": len(self.gpu_files),
            "total_estimated_days": 10,
            "success_criteria": [
                "All direct GPU calls replaced with HAL interfaces",
                "GPU resource management centralized",
                "Proper error handling and fallback mechanisms",
                "Performance maintained or improved",
                "All tests updated and passing",
            ],
        }

    def print_summary(self):
        """打印分析摘要"""
        if not self.analysis_results:
            print("❌ 尚未进行分析")
            return

        print("\n" + "=" * 60)
        print("📊 GPU文件分析摘要")
        print("=" * 60)

        summary = self.analysis_results["summary"]
        stats = self.analysis_results["statistics"]

        # 基本信息
        print(f"📁 总文件数: {summary['total_files']}")
        print(f"📝 总代码行数: {summary['total_size_bytes']:,}")
        print(f"🔥 包含GPU调用的文件: {summary['files_with_direct_gpu']}")
        print(f"📊 GPU使用率: {summary['gpu_usage_percentage']:.1f}%")

        # 优先级分布
        print("\n🎯 优先级分布:")
        for priority, count in stats["priority_distribution"].items():
            print(f"   {priority}: {count} 文件")

        # 复杂度分布
        print("\n⚙️ 复杂度分布:")
        for complexity, count in stats["complexity_distribution"].items():
            print(f"   {complexity}: {count} 文件")

        # HAL层分布
        print("\n🏗️ 推荐HAL层:")
        for hal_layer, count in stats["hal_layer_distribution"].items():
            print(f"   {hal_layer}: {count} 文件")

        # GPU库分布
        print("\n📚 GPU库使用:")
        for lib, count in sorted(stats["gpu_library_distribution"].items()):
            print(f"   {lib}: {count} 文件")

        # 迁移计划
        plan = self.analysis_results["migration_plan"]
        print("\n📋 迁移计划:")
        total_days = 0
        for phase in plan["phases"]:
            print(f"   阶段{phase['phase']}: {phase['name']} ({phase['count']}文件)")
            print(f"      预估: {phase['estimated_days']}天")
            total_days += phase["estimated_days"]

        print(f"\n⏱️ 总预估工作量: {total_days}天")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    analyzer = GPUFileAnalyzer()

    print("🚀 开始分析实际GPU文件...")

    # 执行分析
    results = analyzer.analyze_gpu_files()

    if not results:
        print("❌ 未找到GPU文件或分析失败")
        return

    # 保存分析结果
    report_path = "gpu_files_analysis_report.json"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ 分析报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")

    # 打印摘要
    analyzer.print_summary()

    return results


if __name__ == "__main__":
    main()
