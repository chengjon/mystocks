#!/usr/bin/env python3
"""
修复GPU迁移中的语法错误
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class GPUMigrationFixer:
    """GPU迁移语法修复器"""

    def __init__(self):
        self.project_root = Path(".")
        self.fixes_log = []

    def fix_migration_syntax_errors(self) -> Dict[str, Any]:
        """修复迁移语法错误"""
        print("🔧 修复GPU迁移语法错误...")

        # 需要修复的文件
        files_to_fix = [
            "src/gpu/api_system/utils/gpu_acceleration_engine.py",
            "src/gpu/api_system/services/realtime_service.py",
            "src/gpu/api_system/utils/gpu_utils.py",
        ]

        results = []
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                result = self._fix_single_file(file_path)
                results.append(result)
            else:
                print(f"   ⚠️ 文件不存在: {file_path}")

        return self._generate_fix_report(results)

    def _fix_single_file(self, file_path: str) -> Dict[str, Any]:
        """修复单个文件"""
        file_name = os.path.basename(file_path)
        print(f"   🔧 修复: {file_name}")

        try:
            # 读取原文件
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 应用修复规则
            fixed_content, fixes = self._apply_fix_rules(file_path, content)

            # 写入修复后的内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            return {
                "file_path": file_path,
                "file_name": file_name,
                "success": True,
                "fixes": fixes,
                "original_lines": len(content.split("\n")),
                "fixed_lines": len(fixed_content.split("\n")),
            }

        except Exception as e:
            return {
                "file_path": file_path,
                "file_name": file_name,
                "success": False,
                "error": str(e),
                "fixes": [],
            }

    def _apply_fix_rules(self, file_path: str, content: str) -> Tuple[str, List[str]]:
        """应用修复规则"""
        fixed_content = content
        fixes = []

        # 规则1: 修复缩进问题 (gpu_acceleration_engine.py)
        if "gpu_acceleration_engine.py" in file_path:
            fixed_content, indent_fixes = self._fix_indentation_issues(fixed_content)
            fixes.extend(indent_fixes)

        # 规则2: 修复代码插入问题 (realtime_service.py)
        if "realtime_service.py" in file_path:
            fixed_content, code_fixes = self._fix_code_insertion_issues(fixed_content)
            fixes.extend(code_fixes)

        # 规则3: 修复try/except块问题 (gpu_utils.py)
        if "gpu_utils.py" in file_path:
            fixed_content, try_fixes = self._fix_try_except_issues(fixed_content)
            fixes.extend(try_fixes)

        # 规则4: 确保导入语句位置正确
        fixed_content, import_fixes = self._fix_import_placement(fixed_content)
        fixes.extend(import_fixes)

        return fixed_content, fixes

    def _fix_indentation_issues(self, content: str) -> Tuple[str, List[str]]:
        """修复缩进问题"""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # 修复第1009行的缩进问题
            if line_num == 1009 and line.strip().startswith("params = {}"):
                # 检查上下文缩进
                if i > 0:
                    prev_line = lines[i - 1]
                    if prev_line.strip().startswith("from src.gpu.core"):
                        # 这是导入语句后，应该没有缩进
                        fixed_lines.append("params = {}")
                        fixes.append(
                            f"Line {line_num}: Fixed indentation for params assignment"
                        )
                        continue

            # 修复其他缩进问题
            if line.strip().startswith("from src.gpu.core.") and not line.startswith(
                "from "
            ):
                # 导入语句不应该有缩进
                fixed_lines.append(line.strip())
                fixes.append(f"Line {line_num}: Fixed import statement indentation")
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), fixes

    def _fix_code_insertion_issues(self, content: str) -> Tuple[str, List[str]]:
        """修复代码插入问题"""
        fixes = []

        # 修复第64行的破损代码
        broken_pattern = r"self\.processing_thread = await kernel_executor\.execute_transform_operation\(threading, transpose_config\)hread\("
        fixed_pattern = "self.processing_thread = threading.Thread("

        if re.search(broken_pattern, content):
            content = re.sub(broken_pattern, fixed_pattern, content)
            fixes.append("Fixed broken threading.Thread call")

        return content, fixes

    def _fix_try_except_issues(self, content: str) -> Tuple[str, List[str]]:
        """修复try/except块问题"""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []
        in_try_block = False

        for i, line in enumerate(lines):
            # 检查是否有未完成的try块
            if line.strip().startswith("try:") or line.strip().startswith("try "):
                in_try_block = True

            # 检查是否需要添加except块
            if in_try_block and (
                "from src.gpu.core.hardware_abstraction" in line
                or "from src.gpu.core.kernels" in line
            ):
                # 这看起来是插入在try块中间的导入语句
                # 需要完成try/except结构
                fixed_lines.append(line)

                # 检查下一行是否有except
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not (
                        next_line.strip().startswith("except")
                        or next_line.strip().startswith("finally")
                    ):
                        # 需要添加except块
                        fixed_lines.append("except ImportError:")
                        fixed_lines.append("    pass")
                        fixes.append(f"Added missing except block after line {i + 1}")
                        in_try_block = False
                continue

            fixed_lines.append(line)

            # 重置状态
            if line.strip().startswith("except") or line.strip().startswith("finally"):
                in_try_block = False

        return "\n".join(fixed_lines), fixes

    def _fix_import_placement(self, content: str) -> Tuple[str, List[str]]:
        """修复导入语句位置"""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []
        gpu_imports = []
        other_imports = []
        import_section_ended = False

        # 分离导入语句
        for line in lines:
            if "from src.gpu.core" in line or "import src.gpu.core" in line:
                gpu_imports.append(line)
                fixes.append("Moved GPU import to proper location")
            elif (
                line.strip().startswith("import ") or line.strip().startswith("from ")
            ) and not import_section_ended:
                other_imports.append(line)
            elif line.strip() == "" and len(other_imports) > 0:
                # 导入段还在继续
                other_imports.append(line)
            else:
                import_section_ended = True
                break

        # 重组文件内容
        # 1. 其他导入
        fixed_lines.extend(other_imports)
        # 2. GPU导入
        fixed_lines.extend(gpu_imports)
        # 3. 空行分隔
        if gpu_imports:
            fixed_lines.append("")
        # 4. 剩余内容
        fixed_lines.extend(lines[fixed_lines.__len__() :])

        return "\n".join(fixed_lines), fixes

    def _generate_fix_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成修复报告"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.get("success", False))
        failed_files = total_files - successful_files

        total_fixes = sum(len(r.get("fixes", [])) for r in results)

        return {
            "summary": {
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "success_rate": (successful_files / total_files * 100)
                if total_files > 0
                else 0,
                "total_fixes": total_fixes,
            },
            "files": results,
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印摘要"""
        print("\n" + "=" * 50)
        print("📊 GPU迁移语法修复摘要")
        print("=" * 50)

        summary = report["summary"]
        print(f"📁 总文件数: {summary['total_files']}")
        print(f"✅ 成功修复: {summary['successful_files']}")
        print(f"❌ 修复失败: {summary['failed_files']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        print(f"🔧 总修复数: {summary['total_fixes']}")

        print("\n📋 详细结果:")
        for result in report["files"]:
            status = "✅" if result.get("success", False) else "❌"
            file_name = result.get("file_name", "Unknown")
            fixes_count = len(result.get("fixes", []))
            error = result.get("error", "")
            if error:
                print(f"   {status} {file_name}: {error}")
            else:
                print(f"   {status} {file_name} ({fixes_count} 修复)")

        if summary["success_rate"] == 100:
            print("\n🎉 语法修复成功完成！")
        else:
            print("\n⚠️ 部分修复失败，请检查错误。")

        print("=" * 50)


def main():
    """主函数"""
    fixer = GPUMigrationFixer()

    print("🚀 开始GPU迁移语法修复...")

    # 执行修复
    report = fixer.fix_migration_syntax_errors()

    # 打印摘要
    fixer.print_summary(report)

    return report


if __name__ == "__main__":
    main()
