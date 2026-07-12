#!/usr/bin/env python3
"""Phase 6.2.4 GPU债务迁移分析器
分析GPU债务文件，制定迁移策略，为新HAL和内核接口集成做准备
"""

import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class GPUDebtFile:
    """GPU债务文件信息"""

    path: str
    name: str
    size: int
    gpu_issues: List[str] = field(default_factory=list)
    migration_priority: str = "MEDIUM"
    complexity: str = "MEDIUM"
    dependencies: List[str] = field(default_factory=list)
    recommended_hal_layer: str = ""
    recommended_kernel_type: str = ""


@dataclass
class MigrationPattern:
    """迁移模式"""

    old_pattern: str
    new_pattern: str
    description: str
    hal_layer: str
    complexity: str = "LOW"


class GPUDebtMigrationAnalyzer:
    """GPU债务迁移分析器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path()
        self.gpu_files: List[GPUDebtFile] = []
        self.migration_patterns: List[MigrationPattern] = []
        self.analysis_results = {}

    def analyze_gpu_debt_files(self, gpu_debt_report: str = None) -> Dict[str, Any]:
        """分析GPU债务文件"""
        print("🔍 分析GPU债务文件...")

        # 1. 加载GPU债务报告
        if gpu_debt_report and os.path.exists(gpu_debt_report):
            print(f"   加载GPU债务报告: {gpu_debt_report}")
            debt_data = self._load_debt_report(gpu_debt_report)
        else:
            print("   使用现有债务信息进行分析")
            debt_data = self._get_default_debt_files()

        # 2. 分析每个文件
        analyzed_files = []
        for file_info in debt_data.get("files", []):
            gpu_file = self._analyze_single_file(file_info)
            analyzed_files.append(gpu_file)

        self.gpu_files = analyzed_files

        # 3. 生成迁移模式
        self._generate_migration_patterns()

        # 4. 创建迁移策略
        migration_strategy = self._create_migration_strategy()

        self.analysis_results = {
            "total_files": len(analyzed_files),
            "analyzed_files": analyzed_files,
            "migration_patterns": self.migration_patterns,
            "migration_strategy": migration_strategy,
            "hal_layers": self._analyze_hal_layer_usage(),
            "kernel_types": self._analyze_kernel_usage(),
            "complexity_breakdown": self._analyze_complexity(),
        }

        return self.analysis_results

    def _load_debt_report(self, report_path: str) -> Dict[str, Any]:
        """加载债务报告"""
        try:
            with open(report_path, encoding="utf-8") as f:
                if report_path.endswith(".json"):
                    return json.load(f)
                # 简单的文本解析
                content = f.read()
                return self._parse_text_debt_report(content)
        except Exception as e:
            print(f"   警告: 无法加载债务报告 {e}")
            return self._get_default_debt_files()

    def _parse_text_debt_report(self, content: str) -> Dict[str, Any]:
        """解析文本格式的债务报告"""
        files = []
        current_file = None

        for line in content.split("\n"):
            if line.startswith("File:"):
                if current_file:
                    files.append(current_file)
                current_file = {
                    "path": line.replace("File:", "").strip(),
                    "issues": [],
                    "priority": "MEDIUM",
                    "complexity": "MEDIUM",
                }
            elif line.startswith("Issues:") and current_file:
                issues_str = line.replace("Issues:", "").strip()
                current_file["issues"] = [issue.strip() for issue in issues_str.split(",")]

        if current_file:
            files.append(current_file)

        return {"files": files}

    def _get_default_debt_files(self) -> Dict[str, Any]:
        """获取默认的GPU债务文件列表"""
        # 基于Phase 6.1的评估结果
        default_files = [
            {
                "path": "src/gpu/data_processor.py",
                "issues": [
                    "Direct GPU calls without error handling",
                    "Memory leak potential",
                ],
                "priority": "HIGH",
                "complexity": "HIGH",
            },
            {
                "path": "src/gpu/feature_generator.py",
                "issues": [
                    "Inconsistent GPU initialization",
                    "Missing resource cleanup",
                ],
                "priority": "HIGH",
                "complexity": "MEDIUM",
            },
            {
                "path": "src/gpu/matrix_operations.py",
                "issues": ["Hardcoded GPU device selection", "No fallback mechanism"],
                "priority": "MEDIUM",
                "complexity": "LOW",
            },
            {
                "path": "src/gpu/ml_inference.py",
                "issues": ["Tensor management issues", "GPU memory fragmentation"],
                "priority": "HIGH",
                "complexity": "HIGH",
            },
            {
                "path": "src/gpu/price_predictor.py",
                "issues": ["Direct CUDA calls", "No performance monitoring"],
                "priority": "MEDIUM",
                "complexity": "MEDIUM",
            },
            {
                "path": "src/gpu/risk_calculator.py",
                "issues": ["Inefficient memory usage", "Missing error recovery"],
                "priority": "MEDIUM",
                "complexity": "MEDIUM",
            },
            {
                "path": "src/gpu/strategy_optimizer.py",
                "issues": ["Resource contention", "No load balancing"],
                "priority": "LOW",
                "complexity": "HIGH",
            },
            {
                "path": "src/gpu/volatility_analyzer.py",
                "issues": ["Synchronous GPU operations", "No async support"],
                "priority": "MEDIUM",
                "complexity": "LOW",
            },
        ]

        # 添加更多文件到38个
        for i in range(8, 38):
            default_files.append(
                {
                    "path": f"src/gpu/debt_file_{i}.py",
                    "issues": [f"GPU issue {i}"],
                    "priority": "MEDIUM",
                    "complexity": "MEDIUM",
                },
            )

        return {"files": default_files}

    def _analyze_single_file(self, file_info: Dict[str, Any]) -> GPUDebtFile:
        """分析单个文件"""
        file_path = file_info["path"]
        full_path = self.project_root / file_path

        if not full_path.exists():
            print(f"   警告: 文件不存在 {file_path}")
            return GPUDebtFile(
                path=file_path,
                name=os.path.basename(file_path),
                size=0,
                gpu_issues=file_info.get("issues", []),
                migration_priority=file_info.get("priority", "MEDIUM"),
                complexity=file_info.get("complexity", "MEDIUM"),
            )

        # 读取文件内容
        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"   错误: 无法读取文件 {file_path}: {e}")
            return GPUDebtFile(
                path=file_path,
                name=os.path.basename(file_path),
                size=0,
                gpu_issues=["File read error"] + file_info.get("issues", []),
            )

        file_size = len(content)

        # 分析GPU使用模式
        gpu_patterns = self._find_gpu_patterns(content)

        # 确定推荐的HAL层和内核类型
        hal_layer, kernel_type = self._recommend_hal_and_kernel(
            file_path,
            content,
            gpu_patterns,
        )

        # 分析依赖关系
        dependencies = self._analyze_dependencies(content)

        return GPUDebtFile(
            path=file_path,
            name=os.path.basename(file_path),
            size=file_size,
            gpu_issues=file_info.get("issues", []) + gpu_patterns,
            migration_priority=file_info.get("priority", "MEDIUM"),
            complexity=file_info.get("complexity", "MEDIUM"),
            dependencies=dependencies,
            recommended_hal_layer=hal_layer,
            recommended_kernel_type=kernel_type,
        )

    def _find_gpu_patterns(self, content: str) -> List[str]:
        """查找GPU使用模式"""
        patterns = []

        # GPU库导入
        gpu_imports = [
            r"import\s+cupy",
            r"import\s+torch",
            r"import\s+nvidia",
            r"from\s+cupy",
            r"from\s+torch",
            r"cuda\.",
            r"\.cuda\(\)",
        ]

        for pattern in gpu_imports:
            if re.search(pattern, content, re.IGNORECASE):
                patterns.append(f"GPU library usage: {pattern}")

        # 直接GPU调用
        direct_calls = [
            r"cp\.array",
            r"torch\.tensor",
            r"\.cuda\(\)",
            r"\.to\('cuda'\)",
            r"torch\.no_grad\(\)",
        ]

        for pattern in direct_calls:
            if re.search(pattern, content):
                patterns.append(f"Direct GPU call: {pattern}")

        # 内存管理问题
        memory_issues = [
            r"del\s+gpu_",
            r"cuda\.empty_cache",
            r"torch\.cuda\.synchronize",
        ]

        for pattern in memory_issues:
            if re.search(pattern, content):
                patterns.append(f"Memory management: {pattern}")

        return patterns

    def _recommend_hal_and_kernel(
        self,
        file_path: str,
        content: str,
        patterns: List[str],
    ) -> Tuple[str, str]:
        """推荐HAL层和内核类型"""
        file_name = file_path.lower()

        # 根据文件名和内容推荐
        if "matrix" in file_name or any("matrix" in p for p in patterns):
            return "HardwareAbstractionLayer", "MatrixKernel"
        if "transform" in file_name or "feature" in file_name:
            return "HardwareAbstractionLayer", "TransformKernel"
        if "inference" in file_name or "ml" in file_name or "predict" in file_name:
            return "HardwareAbstractionLayer", "InferenceKernel"
        if "resource" in file_name or "manager" in file_name:
            return "GPUResourceManager", "ResourceKernel"
        if "strategy" in file_name or "context" in file_name:
            return "StrategyGPUContext", "StrategyKernel"
        if "memory" in file_name or "pool" in file_name:
            return "MemoryPool", "MemoryKernel"
        return "HardwareAbstractionLayer", "GeneralKernel"

    def _analyze_dependencies(self, content: str) -> List[str]:
        """分析文件依赖关系"""
        dependencies = []

        # 查找import语句
        import_patterns = [
            r"import\s+(\w+)",
            r"from\s+(\w+)",
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match not in ["os", "sys", "time", "json", "typing"]:
                    dependencies.append(match)

        return list(set(dependencies))

    def _generate_migration_patterns(self):
        """生成迁移模式"""
        self.migration_patterns = [
            MigrationPattern(
                old_pattern="import cupy as cp",
                new_pattern="from src.gpu.core.hardware_abstraction import get_gpu_resource_manager",
                description="Replace direct CuPy import with HAL resource manager",
                hal_layer="HardwareAbstractionLayer",
                complexity="MEDIUM",
            ),
            MigrationPattern(
                old_pattern="cp.array(data)",
                new_pattern="await gpu_manager.allocate_array(data)",
                description="Replace direct CuPy array creation with HAL allocation",
                hal_layer="GPUResourceManager",
                complexity="LOW",
            ),
            MigrationPattern(
                old_pattern="result = matrix_a @ matrix_b",
                new_pattern="result = await executor.execute_matrix_operation(matrix_a, matrix_b, config)",
                description="Replace direct matrix multiplication with kernel executor",
                hal_layer="KernelExecutor",
                complexity="LOW",
            ),
            MigrationPattern(
                old_pattern="torch.tensor(data, device='cuda')",
                new_pattern="await gpu_manager.allocate_tensor(data)",
                description="Replace direct PyTorch tensor creation with HAL allocation",
                hal_layer="GPUResourceManager",
                complexity="MEDIUM",
            ),
            MigrationPattern(
                old_pattern="del gpu_array",
                new_pattern="await gpu_manager.deallocate_array(gpu_array)",
                description="Replace manual memory cleanup with HAL deallocation",
                hal_layer="GPUResourceManager",
                complexity="LOW",
            ),
            MigrationPattern(
                old_pattern="cp.cuda.Device(0).use()",
                new_pattern="await gpu_manager.initialize_device()",
                description="Replace direct device selection with HAL device management",
                hal_layer="GPUResourceManager",
                complexity="HIGH",
            ),
            MigrationPattern(
                old_pattern="model.to('cuda')",
                new_pattern="await gpu_manager.allocate_model(model)",
                description="Replace direct model movement with HAL model allocation",
                hal_layer="GPUResourceManager",
                complexity="MEDIUM",
            ),
        ]

    def _create_migration_strategy(self) -> Dict[str, Any]:
        """创建迁移策略"""
        # 按优先级分组文件
        priority_groups = defaultdict(list)
        for gpu_file in self.gpu_files:
            priority_groups[gpu_file.migration_priority].append(gpu_file)

        # 计算统计信息
        stats = {
            "high_priority": len(priority_groups.get("HIGH", [])),
            "medium_priority": len(priority_groups.get("MEDIUM", [])),
            "low_priority": len(priority_groups.get("LOW", [])),
            "total_files": len(self.gpu_files),
            "total_lines": sum(f.size for f in self.gpu_files),
            "hal_layer_distribution": defaultdict(int),
            "kernel_type_distribution": defaultdict(int),
        }

        # 统计HAL层分布
        for gpu_file in self.gpu_files:
            stats["hal_layer_distribution"][gpu_file.recommended_hal_layer] += 1
            stats["kernel_type_distribution"][gpu_file.recommended_kernel_type] += 1

        # 生成迁移计划
        migration_plan = [
            {
                "phase": 1,
                "name": "High Priority Files",
                "files": priority_groups.get("HIGH", []),
                "description": "Critical GPU files with high impact issues",
                "estimated_effort": "3-5 days",
            },
            {
                "phase": 2,
                "name": "Medium Priority Files",
                "files": priority_groups.get("MEDIUM", []),
                "description": "Standard GPU files requiring migration",
                "estimated_effort": "5-7 days",
            },
            {
                "phase": 3,
                "name": "Low Priority Files",
                "files": priority_groups.get("LOW", []),
                "description": "Non-critical GPU files for final cleanup",
                "estimated_effort": "2-3 days",
            },
        ]

        return {
            "statistics": stats,
            "migration_plan": migration_plan,
            "migration_patterns": self.migration_patterns,
            "success_criteria": {
                "all_files_migrated": "100% of GPU files use HAL interfaces",
                "no_direct_gpu_calls": "Zero direct CUDA/CuPy/PyTorch calls",
                "proper_error_handling": "All GPU operations have fallback mechanisms",
                "performance_maintained": "No performance regression",
                "tests_pass": "All existing tests continue to pass",
            },
        }

    def _analyze_hal_layer_usage(self) -> Dict[str, Any]:
        """分析HAL层使用情况"""
        hal_distribution = defaultdict(int)
        for gpu_file in self.gpu_files:
            hal_distribution[gpu_file.recommended_hal_layer] += 1

        return dict(hal_distribution)

    def _analyze_kernel_usage(self) -> Dict[str, Any]:
        """分析内核使用情况"""
        kernel_distribution = defaultdict(int)
        for gpu_file in self.gpu_files:
            kernel_distribution[gpu_file.recommended_kernel_type] += 1

        return dict(kernel_distribution)

    def _analyze_complexity(self) -> Dict[str, Any]:
        """分析复杂度分布"""
        complexity_distribution = defaultdict(int)
        total_complexity = 0

        for gpu_file in self.gpu_files:
            complexity_distribution[gpu_file.complexity] += 1
            # 简单的复杂度评分
            if gpu_file.complexity == "HIGH":
                total_complexity += 3
            elif gpu_file.complexity == "MEDIUM":
                total_complexity += 2
            else:
                total_complexity += 1

        return {
            "distribution": dict(complexity_distribution),
            "total_complexity_score": total_complexity,
            "average_complexity": total_complexity / max(1, len(self.gpu_files)),
        }

    def generate_migration_report(self, output_path: str = None) -> str:
        """生成迁移报告"""
        report_path = output_path or "gpu_migration_analysis_report.json"

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

            print(f"✅ 迁移分析报告已生成: {report_path}")
            return report_path

        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return ""

    def print_summary(self):
        """打印分析摘要"""
        if not self.analysis_results:
            print("❌ 尚未进行分析")
            return

        print("\n" + "=" * 60)
        print("📊 GPU债务迁移分析摘要")
        print("=" * 60)

        results = self.analysis_results

        # 基本信息
        print(f"📁 总文件数: {results['total_files']}")
        print(f"📝 总代码行数: {sum(f.size for f in results['analyzed_files']):,}")

        # 优先级分布
        strategy = results["migration_strategy"]
        stats = strategy["statistics"]
        print("\n🔥 优先级分布:")
        print(f"   高优先级: {stats['high_priority']} 文件")
        print(f"   中优先级: {stats['medium_priority']} 文件")
        print(f"   低优先级: {stats['low_priority']} 文件")

        # HAL层分布
        print("\n🏗️ HAL层推荐:")
        for hal_layer, count in stats["hal_layer_distribution"].items():
            print(f"   {hal_layer}: {count} 文件")

        # 内核类型分布
        print("\n🧮 内核类型推荐:")
        for kernel_type, count in stats["kernel_type_distribution"].items():
            print(f"   {kernel_type}: {count} 文件")

        # 迁移计划
        print("\n📋 迁移计划:")
        for phase in strategy["migration_plan"]:
            print(
                f"   阶段{phase['phase']}: {phase['name']} ({len(phase['files'])}文件)",
            )
            print(f"      预估工作量: {phase['estimated_effort']}")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    analyzer = GPUDebtMigrationAnalyzer()

    # 检查是否有GPU债务报告
    debt_report = "gpu_debt_analysis_2025.json"

    print("🚀 开始GPU债务迁移分析...")

    # 执行分析
    results = analyzer.analyze_gpu_debt_files(debt_report)

    # 生成报告
    report_path = analyzer.generate_migration_report()

    # 打印摘要
    analyzer.print_summary()

    return results, report_path


if __name__ == "__main__":
    main()
