#!/usr/bin/env python3
"""
简化的GPU迁移器
专注于基本的HAL集成，替换直接GPU调用
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SimpleGPUMigrator:
    """简化的GPU迁移器"""

    def __init__(self):
        self.project_root = Path(".")
        self.migration_log = []
        self.backup_dir = self.project_root / "gpu_simple_backups"

    def migrate_gpu_files(self) -> Dict[str, Any]:
        """迁移GPU文件"""
        print("🚀 开始简化GPU迁移...")

        # 创建备份目录
        self._create_backup_dir()

        # 选择要迁移的文件
        target_files = self._select_target_files()

        results = []
        for file_path in target_files:
            result = self._migrate_single_file(file_path)
            results.append(result)

        # 生成报告
        report = self._generate_report(results)

        return report

    def _create_backup_dir(self):
        """创建备份目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / f"gpu_simple_backups_{timestamp}"
        self.backup_dir.mkdir(exist_ok=True)

    def _select_target_files(self) -> List[str]:
        """选择目标文件"""
        # 选择关键GPU文件进行迁移
        target_files = [
            "src/gpu/api_system/utils/gpu_acceleration_engine.py",
            "src/gpu/api_system/services/realtime_service.py",
            "src/gpu/api_system/utils/gpu_utils.py",
        ]

        # 过滤存在的文件
        existing_files = []
        for file_path in target_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
                print(f"   📋 目标文件: {os.path.basename(file_path)}")

        return existing_files

    def _migrate_single_file(self, file_path: str) -> Dict[str, Any]:
        """迁移单个文件"""
        file_name = os.path.basename(file_path)
        print(f"   🔧 迁移: {file_name}")

        try:
            # 读取原文件
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 创建备份
            backup_path = self._create_backup(file_path, original_content)

            # 执行基本迁移
            migrated_content, changes = self._perform_basic_migration(
                file_path, original_content
            )

            # 写入迁移后的内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(migrated_content)

            return {
                "file_path": file_path,
                "file_name": file_name,
                "success": True,
                "changes": changes,
                "backup_path": str(backup_path),
                "original_lines": len(original_content.split("\n")),
                "modified_lines": len(migrated_content.split("\n")),
            }

        except Exception as e:
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "success": False,
                "error": str(e),
                "changes": [],
            }

    def _create_backup(self, file_path: str, content: str) -> str:
        """创建备份"""
        relative_path = Path(file_path).relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(backup_path)

    def _perform_basic_migration(
        self, file_path: str, content: str
    ) -> tuple[str, List[str]]:
        """执行基本迁移"""
        migrated_content = content
        changes = []

        # 1. 添加HAL导入
        if "from src.gpu.core.hardware_abstraction" not in migrated_content:
            migrated_content, import_change = self._add_hal_import(migrated_content)
            if import_change:
                changes.extend(import_change)

        # 2. 添加内核执行器导入
        if "from src.gpu.core.kernels" not in migrated_content:
            migrated_content, kernel_change = self._add_kernel_import(migrated_content)
            if kernel_change:
                changes.extend(kernel_change)

        # 3. 替换简单的GPU调用
        migrated_content, call_changes = self._replace_simple_gpu_calls(
            migrated_content
        )
        changes.extend(call_changes)

        return migrated_content, changes

    def _add_hal_import(self, content: str) -> tuple[str, List[str]]:
        """添加HAL导入"""
        lines = content.split("\n")
        changes = []

        # 找到最后一个import语句
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                insert_index = i + 1

        # 添加HAL导入
        hal_import = (
            "from src.gpu.core.hardware_abstraction import get_gpu_resource_manager"
        )
        lines.insert(insert_index, hal_import)
        changes.append(f"Added HAL import: {hal_import}")

        return "\n".join(lines), changes

    def _add_kernel_import(self, content: str) -> tuple[str, List[str]]:
        """添加内核导入"""
        lines = content.split("\n")
        changes = []

        # 找到HAL导入后的位置
        insert_index = 0
        for i, line in enumerate(lines):
            if "from src.gpu.core.hardware_abstraction import" in line:
                insert_index = i + 1
                break

        # 添加内核执行器导入
        kernel_import = "from src.gpu.core.kernels import get_kernel_executor"
        lines.insert(insert_index, kernel_import)
        changes.append(f"Added kernel import: {kernel_import}")

        return "\n".join(lines), changes

    def _replace_simple_gpu_calls(self, content: str) -> tuple[str, List[str]]:
        """替换简单的GPU调用"""
        migrated_content = content
        changes = []

        # 简单替换规则
        replacements = [
            # CuPy使用
            ("cp.", "gpu_manager.", "Replace cp. with gpu_manager."),
            # PyTorch CUDA
            (
                ".cuda()",
                "await gpu_manager.to_device()",
                "Replace .cuda() with HAL device transfer",
            ),
            # 直接数组创建
            (
                "cupy.array",
                "await gpu_manager.create_array",
                "Replace cupy.array with HAL creation",
            ),
        ]

        for old, new, description in replacements:
            if old in migrated_content and new not in migrated_content:
                migrated_content = migrated_content.replace(old, new)
                changes.append(description)

        # 添加初始化代码（如果有GPU调用）
        if any(old in migrated_content for old, _, _ in replacements):
            init_code = """
# 初始化GPU资源管理器
gpu_manager = get_gpu_resource_manager()
await gpu_manager.initialize()

# 初始化内核执行器
kernel_executor = get_kernel_executor()
await kernel_executor.initialize()
"""
            if "async def main(" in migrated_content:
                # 在main函数开头添加初始化
                lines = migrated_content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith("async def main("):
                        lines.insert(i + 1, init_code.strip())
                        break
                migrated_content = "\n".join(lines)
                changes.append("Added GPU initialization code")

        return migrated_content, changes

    def _generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成迁移报告"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.get("success", False))
        failed_files = total_files - successful_files

        total_changes = sum(len(r.get("changes", [])) for r in results)

        return {
            "summary": {
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "success_rate": (successful_files / total_files * 100)
                if total_files > 0
                else 0,
                "total_changes": total_changes,
            },
            "files": results,
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印摘要"""
        print("\n" + "=" * 50)
        print("📊 简化GPU迁移摘要")
        print("=" * 50)

        summary = report["summary"]
        print(f"📁 总文件数: {summary['total_files']}")
        print(f"✅ 成功迁移: {summary['successful_files']}")
        print(f"❌ 失败迁移: {summary['failed_files']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        print(f"🔧 总修改数: {summary['total_changes']}")

        print("\n📋 详细结果:")
        for result in report["files"]:
            status = "✅" if result.get("success", False) else "❌"
            file_name = result.get("file_name", "Unknown")
            changes_count = len(result.get("changes", []))
            print(f"   {status} {file_name} ({changes_count} 修改)")

        if summary["success_rate"] == 100:
            print("\n🎉 迁移成功完成！")
        else:
            print("\n⚠️ 部分迁移失败，请检查错误。")

        print("=" * 50)


def main():
    """主函数"""
    migrator = SimpleGPUMigrator()

    print("🚀 Phase 6.2.4 简化GPU迁移执行...")

    # 执行迁移
    report = migrator.migrate_gpu_files()

    # 保存报告
    report_path = "simple_gpu_migration_report.json"
    try:
        import json

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ 报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")

    # 打印摘要
    migrator.print_summary(report)

    return report


if __name__ == "__main__":
    main()
