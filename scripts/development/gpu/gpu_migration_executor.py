#!/usr/bin/env python3
"""
Phase 6.2.4 GPU迁移执行器
执行GPU债务文件的迁移，将直接GPU调用替换为HAL和内核接口
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class MigrationResult:
    """迁移结果"""

    success: bool
    file_path: str
    original_lines: int
    modified_lines: int
    changes_made: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    backup_path: str = ""


class GPUMigrationExecutor:
    """GPU迁移执行器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(".")
        self.migration_results: List[MigrationResult] = []
        self.backup_dir = self.project_root / "gpu_migration_backups"

    def execute_migration(self, target_files: List[str] = None) -> Dict[str, Any]:
        """执行GPU迁移"""
        print("🚀 开始GPU迁移执行...")

        # 创建备份目录
        self._create_backup_directory()

        # 确定目标文件
        if target_files is None:
            target_files = self._get_high_priority_files()

        print(f"📋 目标文件数量: {len(target_files)}")

        # 执行迁移
        results = []
        for file_path in target_files:
            result = self._migrate_file(file_path)
            results.append(result)

            if result.success:
                print(
                    f"   ✅ {os.path.basename(file_path)}: {len(result.changes_made)}处修改"
                )
            else:
                print(
                    f"   ❌ {os.path.basename(file_path)}: {', '.join(result.errors)}"
                )

        self.migration_results = results

        # 生成迁移报告
        report = self._generate_migration_report(results)

        return report

    def _create_backup_directory(self):
        """创建备份目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / f"gpu_migration_backups_{timestamp}"
        self.backup_dir.mkdir(exist_ok=True)
        print(f"📁 备份目录: {self.backup_dir}")

    def _get_high_priority_files(self) -> List[str]:
        """获取高优先级文件"""
        # 基于分析结果，选择关键基础设施文件
        key_files = [
            "src/gpu/api_system/utils/gpu_acceleration_engine.py",
            "src/gpu/api_system/utils/resource_scheduler.py",
            "src/gpu/api_system/services/resource_manager.py",
            "src/gpu/api_system/services/realtime_service.py",
            "src/gpu/api_system/utils/gpu_utils.py",
        ]

        # 过滤存在的文件
        existing_files = []
        for file_path in key_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                print(f"   ⚠️ 文件不存在: {file_path}")

        return existing_files

    def _migrate_file(self, file_path: str) -> MigrationResult:
        """迁移单个文件"""
        print(f"   🔧 迁移: {os.path.basename(file_path)}")

        try:
            # 读取原文件
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 创建备份
            backup_path = self._create_backup(file_path, original_content)

            # 执行迁移转换
            migrated_content, changes, errors = self._perform_migration(
                file_path, original_content
            )

            # 写入迁移后的文件
            if changes or errors:  # 有变更才写入
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(migrated_content)

            return MigrationResult(
                success=len(errors) == 0,
                file_path=file_path,
                original_lines=len(original_content.split("\n")),
                modified_lines=len(migrated_content.split("\n")),
                changes_made=changes,
                errors=errors,
                backup_path=backup_path,
            )

        except Exception as e:
            return MigrationResult(
                success=False,
                file_path=file_path,
                original_lines=0,
                modified_lines=0,
                errors=[f"Migration failed: {str(e)}"],
            )

    def _create_backup(self, file_path: str, content: str) -> str:
        """创建文件备份"""
        relative_path = Path(file_path).relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path

        # 创建目录结构
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入备份
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(backup_path)

    def _perform_migration(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """执行迁移转换"""
        migrated_content = content
        changes = []
        errors = []

        # 迁移规则
        migration_rules = [
            # 1. 导入替换规则
            self._migrate_imports,
            # 2. GPU分配规则
            self._migrate_gpu_allocation,
            # 3. 矩阵运算规则
            self._migrate_matrix_operations,
            # 4. 内存管理规则
            self._migrate_memory_management,
            # 5. 设备管理规则
            self._migrate_device_management,
        ]

        for rule_func in migration_rules:
            try:
                new_content, rule_changes, rule_errors = rule_func(
                    file_path, migrated_content
                )
                migrated_content = new_content
                changes.extend(rule_changes)
                errors.extend(rule_errors)
            except Exception as e:
                errors.append(f"Rule {rule_func.__name__} failed: {str(e)}")

        return migrated_content, changes, errors

    def _migrate_imports(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """迁移导入语句"""
        migrated_content = content
        changes = []
        errors = []

        # 导入替换规则
        import_replacements = [
            # CuPy导入
            (
                r"import\s+cupy\s+as\s+cp",
                "from src.gpu.core.hardware_abstraction import get_gpu_resource_manager",
                "Replace CuPy import with HAL manager",
            ),
            (
                r"from\s+cupy\s+import\s+(\w+)",
                "from src.gpu.core.kernels import get_kernel_executor",
                "Replace CuPy import with kernel executor",
            ),
            # PyTorch导入
            (
                r"import\s+torch",
                "from src.gpu.core.hardware_abstraction import get_gpu_resource_manager",
                "Replace PyTorch import with HAL manager",
            ),
            # CUDA直接导入
            (
                r"import\s+cuda",
                "from src.gpu.core.hardware_abstraction import get_gpu_resource_manager",
                "Replace CUDA import with HAL manager",
            ),
        ]

        for pattern, replacement, description in import_replacements:
            if re.search(pattern, migrated_content):
                # 检查是否已经有HAL导入
                hal_pattern = r"from\s+src\.gpu\.core\.hardware_abstraction\s+import"
                if re.search(hal_pattern, migrated_content):
                    continue

                # 在文件开头添加导入
                lines = migrated_content.split("\n")
                import_line = "from src.gpu.core.hardware_abstraction import get_gpu_resource_manager"

                # 找到最后一个import语句后插入
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        insert_index = i + 1

                lines.insert(insert_index, import_line)
                migrated_content = "\n".join(lines)
                changes.append(description)

        return migrated_content, changes, errors

    def _migrate_gpu_allocation(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """迁移GPU分配"""
        migrated_content = content
        changes = []
        errors = []

        # GPU分配替换规则
        allocation_replacements = [
            # CuPy数组创建
            (
                r"cp\.array\(([^)]+)\)",
                r"await gpu_manager.allocate_array(\1)",
                "Replace CuPy array creation with HAL allocation",
            ),
            # PyTorch张量创建
            (
                r"torch\.tensor\(([^)]+),\s*device\s*=\s*['\"]cuda",
                r"await gpu_manager.allocate_tensor(\1)",
                "Replace PyTorch tensor creation with HAL allocation",
            ),
            # CUDA设备选择
            (
                r"cp\.cuda\.Device\((\d+)\)\.use\(\)",
                r"await gpu_manager.set_device(\1)",
                "Replace CUDA device selection with HAL device management",
            ),
        ]

        for pattern, replacement, description in allocation_replacements:
            old_content = migrated_content
            migrated_content = re.sub(pattern, replacement, migrated_content)

            if old_content != migrated_content:
                changes.append(description)

        return migrated_content, changes, errors

    def _migrate_matrix_operations(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """迁移矩阵运算"""
        migrated_content = content
        changes = []
        errors = []

        # 矩阵运算替换规则
        matrix_replacements = [
            # 矩阵乘法
            (
                r"(\w+)\s*@\s*(\w+)",
                r"await kernel_executor.execute_matrix_operation(\1, \2, matrix_config)",
                "Replace direct matrix multiplication with kernel executor",
            ),
            # 矩阵转置
            (
                r"(\w+)\.T",
                r"await kernel_executor.execute_transform_operation(\1, transpose_config)",
                "Replace direct matrix transpose with kernel executor",
            ),
            # 矩阵求逆
            (
                r"cp\.linalg\.inv\(([^)]+)\)",
                r"await kernel_executor.execute_matrix_operation(\1, None, inverse_config)",
                "Replace direct matrix inverse with kernel executor",
            ),
        ]

        for pattern, replacement, description in matrix_replacements:
            old_content = migrated_content
            migrated_content = re.sub(pattern, replacement, migrated_content)

            if old_content != migrated_content:
                changes.append(description)

        return migrated_content, changes, errors

    def _migrate_memory_management(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """迁移内存管理"""
        migrated_content = content
        changes = []
        errors = []

        # 内存管理替换规则
        memory_replacements = [
            # 手动内存删除
            (
                r"del\s+(gpu_\w+)",
                r"await gpu_manager.deallocate_array(\1)",
                "Replace manual memory deletion with HAL deallocation",
            ),
            # CUDA内存缓存清理
            (
                r"cp\.cuda\.empty_cache\(\)",
                r"await gpu_manager.clear_cache()",
                "Replace CUDA cache clearing with HAL cache management",
            ),
            # CUDA同步
            (
                r"cp\.cuda\.Stream\.null\.synchronize\(\)",
                r"await gpu_manager.synchronize()",
                "Replace CUDA synchronization with HAL synchronization",
            ),
        ]

        for pattern, replacement, description in memory_replacements:
            old_content = migrated_content
            migrated_content = re.sub(pattern, replacement, migrated_content)

            if old_content != migrated_content:
                changes.append(description)

        return migrated_content, changes, errors

    def _migrate_device_management(
        self, file_path: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """迁移设备管理"""
        migrated_content = content
        changes = []
        errors = []

        # 设备管理替换规则
        device_replacements = [
            # 设备检查
            (
                r"cp\.cuda\.is_available\(\)",
                r"await gpu_manager.is_gpu_available()",
                "Replace CUDA availability check with HAL check",
            ),
            # 设备数量
            (
                r"len\(cp\.cuda\.get_devices\(\))",
                r"await gpu_manager.get_device_count()",
                "Replace CUDA device count with HAL device count",
            ),
            # 当前设备
            (
                r"cp\.cuda\.get_device_id\(\)",
                r"await gpu_manager.get_current_device_id()",
                "Replace CUDA device ID with HAL device ID",
            ),
        ]

        for pattern, replacement, description in device_replacements:
            old_content = migrated_content
            migrated_content = re.sub(pattern, replacement, migrated_content)

            if old_content != migrated_content:
                changes.append(description)

        return migrated_content, changes, errors

    def _generate_migration_report(
        self, results: List[MigrationResult]
    ) -> Dict[str, Any]:
        """生成迁移报告"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.success)
        failed_files = total_files - successful_files

        total_changes = sum(len(r.changes_made) for r in results)
        total_errors = sum(len(r.errors) for r in results)

        # 文件大小变化统计
        total_original_lines = sum(r.original_lines for r in results)
        total_modified_lines = sum(r.modified_lines for r in results)

        return {
            "summary": {
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "success_rate": (successful_files / total_files * 100)
                if total_files > 0
                else 0,
                "total_changes": total_changes,
                "total_errors": total_errors,
            },
            "statistics": {
                "total_original_lines": total_original_lines,
                "total_modified_lines": total_modified_lines,
                "line_change_rate": (
                    (total_modified_lines - total_original_lines)
                    / total_original_lines
                    * 100
                )
                if total_original_lines > 0
                else 0,
            },
            "files": [
                {
                    "path": r.file_path,
                    "name": os.path.basename(r.file_path),
                    "success": r.success,
                    "changes_count": len(r.changes_made),
                    "errors_count": len(r.errors),
                    "backup_path": r.backup_path,
                }
                for r in results
            ],
        }

    def print_migration_summary(self, report: Dict[str, Any]):
        """打印迁移摘要"""
        print("\n" + "=" * 60)
        print("📊 GPU迁移执行摘要")
        print("=" * 60)

        summary = report["summary"]
        stats = report["statistics"]

        # 基本统计
        print(f"📁 总文件数: {summary['total_files']}")
        print(f"✅ 成功迁移: {summary['successful_files']}")
        print(f"❌ 失败迁移: {summary['failed_files']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        print(f"🔧 总修改数: {summary['total_changes']}")
        print(f"⚠️ 总错误数: {summary['total_errors']}")

        # 代码行数变化
        print("\n📝 代码行数变化:")
        print(f"   原始总行数: {stats['total_original_lines']:,}")
        print(f"   迁移后行数: {stats['total_modified_lines']:,}")
        print(f"   变化率: {stats['line_change_rate']:+.1f}%")

        # 详细文件结果
        print("\n📋 详细结果:")
        for file_info in report["files"]:
            status = "✅" if file_info["success"] else "❌"
            print(f"   {status} {file_info['name']}")
            print(
                f"      修改: {file_info['changes_count']} | 错误: {file_info['errors_count']}"
            )

        print("\n" + "=" * 60)

        if summary["total_errors"] == 0:
            print("🎉 迁移成功完成！所有文件都已成功迁移。")
        else:
            print("⚠️ 迁移过程中遇到错误，请检查失败文件。")


def main():
    """主函数"""
    executor = GPUMigrationExecutor()

    print("🚀 开始Phase 6.2.4 GPU迁移执行...")

    # 执行迁移
    report = executor.execute_migration()

    # 保存迁移报告
    report_path = "gpu_migration_report.json"
    try:
        import json

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ 迁移报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")

    # 打印摘要
    executor.print_migration_summary(report)

    return report


if __name__ == "__main__":
    main()
