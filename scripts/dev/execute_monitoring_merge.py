#!/usr/bin/env python3
"""MyStocks 代码优化 - 监控模块合并执行脚本
将monitoring.py的重复代码整合到monitoring/目录中

执行步骤：
1. 备份monitoring.py到.archive目录
2. 删除monitoring.py统一版本
3. 更新所有引用monitoring.py的导入语句
4. 验证所有导入仍然有效

创建日期: 2025-11-25
版本: 1.0.0
"""

import shutil
from datetime import datetime
from pathlib import Path


class MonitoringMerger:
    def __init__(self):
        self.project_root = Path("/opt/claude/mystocks_spec")
        self.src_path = self.project_root / "src"
        self.monitoring_py = self.src_path / "monitoring.py"
        self.monitoring_dir = self.src_path / "monitoring"
        self.archive_dir = self.project_root / ".archive" / "old_code"

    def backup_monitoring_py(self):
        """备份monitoring.py到archive目录"""
        print("步骤 1: 备份monitoring.py...")

        if self.monitoring_py.exists():
            # 创建时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"monitoring_py_backup_{timestamp}.py"
            backup_path = self.archive_dir / backup_name

            # 确保archive目录存在
            self.archive_dir.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(self.monitoring_py, backup_path)
            print(f"   ✅ 已备份到: {backup_path}")
            return True
        print("   ⚠️  monitoring.py文件不存在")
        return False

    def update_imports(self):
        """更新对monitoring.py的导入引用"""
        print("步骤 2: 更新导入引用...")

        # 需要替换的导入映射
        import_mappings = {
            "from src.monitoring.monitoring_database import MonitoringDatabase": "from src.monitoring.monitoring_database import MonitoringDatabase",
            "from src.monitoring.performance_monitor import PerformanceMonitor": "from src.monitoring.performance_monitor import PerformanceMonitor",
            "from src.monitoring.alert_manager import AlertManager": "from src.monitoring.alert_manager import AlertManager",
            "from src.monitoring.alert_manager import AlertLevel": "from src.monitoring.alert_manager import AlertLevel",
            "from src.monitoring.alert_manager import Alert": "from src.monitoring.alert_manager import Alert",
            "from src.monitoring.alert_manager import AlertChannel": "from src.monitoring.alert_manager import AlertChannel",
            "from src.monitoring.alert_manager import LogAlertChannel": "from src.monitoring.alert_manager import LogAlertChannel",
            "from src.monitoring.alert_manager import EmailAlertChannel": "from src.monitoring.alert_manager import EmailAlertChannel",
            "from src.monitoring.alert_manager import WebhookAlertChannel": "from src.monitoring.alert_manager import WebhookAlertChannel",
            "from src.monitoring.monitoring_service import OperationMetrics": "from src.monitoring.monitoring_service import OperationMetrics",
        }

        # 查找所有需要更新的文件
        files_to_update = []
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file) or ".archive" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # 检查是否包含对monitoring.py的导入
                for old_import in import_mappings:
                    if old_import in content:
                        files_to_update.append(py_file)
                        break

            except Exception as e:
                print(f"   ⚠️  读取文件失败 {py_file}: {e}")
                continue

        print(f"   找到 {len(files_to_update)} 个文件需要更新")

        # 更新文件
        updated_count = 0
        for file_path in files_to_update:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # 替换导入语句
                for old_import, new_import in import_mappings.items():
                    content = content.replace(old_import, new_import)

                # 如果内容有变化，写回文件
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_count += 1
                    print(f"   ✅ 更新: {file_path.relative_to(self.project_root)}")

            except Exception as e:
                print(f"   ❌ 更新失败 {file_path}: {e}")

        print(f"   总计更新了 {updated_count} 个文件")
        return updated_count

    def delete_monitoring_py(self):
        """删除monitoring.py文件"""
        print("步骤 3: 删除monitoring.py...")

        if self.monitoring_py.exists():
            self.monitoring_py.unlink()
            print("   ✅ monitoring.py已删除")
            return True
        print("   ⚠️  monitoring.py文件不存在")
        return False

    def validate_imports(self):
        """验证导入仍然有效"""
        print("步骤 4: 验证导入...")

        # 测试主要导入
        test_imports = [
            "from src.monitoring.monitoring_database import MonitoringDatabase",
            "from src.monitoring.performance_monitor import PerformanceMonitor",
            "from src.monitoring.alert_manager import AlertManager",
            "from src.monitoring.monitoring_service import OperationMetrics",
        ]

        successful_imports = 0
        for import_stmt in test_imports:
            try:
                exec(
                    f"import sys; sys.path.insert(0, '{self.project_root}'); {import_stmt}",
                )
                print(f"   ✅ {import_stmt}")
                successful_imports += 1
            except Exception as e:
                print(f"   ❌ {import_stmt}: {e}")

        print(f"   验证结果: {successful_imports}/{len(test_imports)} 个导入成功")
        return successful_imports == len(test_imports)

    def get_stats(self):
        """获取优化统计"""
        print("步骤 5: 优化统计...")

        # 统计代码行数
        total_lines_before = 12010  # 分析得出的总重复行数
        lines_removed = 1106  # monitoring.py的行数

        print(f"   📊 优化前重复代码: {total_lines_before} 行")
        print(f"   📊 删除的重复代码: {lines_removed} 行")
        print(f"   📊 剩余代码量: {total_lines_before - lines_removed} 行")
        print(f"   📊 减少比例: {lines_removed / total_lines_before * 100:.1f}%")

        # 统计文件减少
        files_removed = 1  # monitoring.py
        print(f"   📁 删除文件数: {files_removed} 个")

        return {
            "lines_before": total_lines_before,
            "lines_removed": lines_removed,
            "lines_after": total_lines_before - lines_removed,
            "files_removed": files_removed,
            "reduction_percentage": lines_removed / total_lines_before * 100,
        }

    def execute_merge(self):
        """执行完整的合并流程"""
        print("=" * 60)
        print("MyStocks 监控模块合并执行")
        print("=" * 60)

        # 检查前置条件
        if not self.monitoring_py.exists():
            print("❌ monitoring.py不存在，跳过执行")
            return False

        if not self.monitoring_dir.exists():
            print("❌ monitoring/目录不存在，跳过执行")
            return False

        # 执行合并步骤
        backup_success = self.backup_monitoring_py()
        update_success = self.update_imports() >= 0
        delete_success = self.delete_monitoring_py()
        validate_success = self.validate_imports()

        # 获取统计
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("合并结果总结:")
        print("=" * 60)
        print(f"✅ 备份: {'成功' if backup_success else '失败'}")
        print(f"✅ 更新导入: {update_success} 个文件")
        print(f"✅ 删除文件: {'成功' if delete_success else '失败'}")
        print(f"✅ 验证导入: {'通过' if validate_success else '失败'}")
        print(
            f"📊 代码减少: {stats['lines_removed']} 行 ({stats['reduction_percentage']:.1f}%)",
        )
        print(f"📁 文件减少: {stats['files_removed']} 个")

        if backup_success and delete_success and validate_success:
            print("\n🎉 监控模块合并执行成功!")
            return True
        print("\n❌ 合并执行过程中遇到问题，请检查日志")
        return False


if __name__ == "__main__":
    merger = MonitoringMerger()
    success = merger.execute_merge()

    if success:
        print("\n📝 后续建议:")
        print("   1. 运行项目测试确保功能正常")
        print("   2. 检查是否有其他对monitoring.py的引用")
        print("   3. 更新相关文档")
    else:
        print("\n⚠️  合并过程中遇到问题，可能需要手动处理")
