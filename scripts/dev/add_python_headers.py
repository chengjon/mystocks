#!/usr/bin/env python3
"""# 功能：批量为Python核心文件添加规范化头注释
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 自动检测已有头注释，避免重复添加
#   - 支持7组件Python头注释标准
#   - 备份原文件到.backup
# 版权：MyStocks Project © 2025
"""

import os
import re
from typing import Tuple


# Python头注释模板
PYTHON_HEADER_TEMPLATE = """'''
# 功能：{description}
# 作者：{author}
# 创建日期：{created_date}
# 版本：{version}
# 依赖：{dependencies}
# 注意事项：
#   {notes}
# 版权：{copyright}
'''
"""


class PythonHeaderAdder:
    """批量添加Python头注释的工具类"""

    def __init__(self):
        self.added_count = 0
        self.skipped_count = 0
        self.failed_count = 0

    def has_standard_header(self, content: str) -> bool:
        """检查文件是否已有标准头注释"""
        # 检查是否有 "# 功能：" 或 "# 作者：" 标记
        patterns = [
            r"#\s*功能[：:]\s*.+",
            r"#\s*作者[：:]\s*.+",
            r"MyStocks\s*(统一|量化|.*系统)",
            r"@author",
        ]

        for pattern in patterns:
            if re.search(pattern, content[:500]):  # 只检查前500字符
                return True
        return False

    def extract_shebang_and_encoding(self, content: str) -> Tuple[str, str]:
        """提取文件的shebang和编码声明"""
        lines = content.split("\n", 3)
        shebang = ""
        encoding = ""
        start_index = 0

        # 检查shebang (#!/usr/bin/env python3)
        if lines and lines[0].startswith("#!"):
            shebang = lines[0]
            start_index = 1

        # 检查编码声明 (# -*- coding: utf-8 -*-)
        if len(lines) > start_index and "coding" in lines[start_index]:
            encoding = lines[start_index]
            start_index += 1

        # 剩余内容
        remaining = "\n".join(lines[start_index:])

        return shebang, encoding, remaining

    def add_header_to_file(
        self,
        file_path: str,
        description: str,
        author: str = "JohnC (ninjas@sina.com) & Claude",
        created_date: str = "2025-10-16",
        version: str = "2.1.0",
        dependencies: str = "详见requirements.txt或导入部分",
        notes: str = "本文件是MyStocks v2.1核心组件",
        copyright: str = "MyStocks Project © 2025",
    ) -> bool:
        """为单个Python文件添加头注释"""
        try:
            # 读取文件
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 检查是否已有标准头注释
            if self.has_standard_header(content):
                print(f"⏭️  跳过 (已有头注释): {file_path}")
                self.skipped_count += 1
                return False

            # 备份原文件
            backup_path = file_path + ".backup"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            # 提取shebang和编码声明
            shebang, encoding, remaining = self.extract_shebang_and_encoding(content)

            # 移除已有的docstring (如果是简单的)
            remaining = self._remove_simple_docstring(remaining)

            # 构建新内容
            header = PYTHON_HEADER_TEMPLATE.format(
                description=description,
                author=author,
                created_date=created_date,
                version=version,
                dependencies=dependencies,
                notes=notes,
                copyright=copyright,
            )

            new_content_parts = []
            if shebang:
                new_content_parts.append(shebang)
            if encoding:
                new_content_parts.append(encoding)
            new_content_parts.append(header)
            new_content_parts.append(remaining)

            new_content = "\n".join(new_content_parts)

            # 写入新内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"✅ 已添加头注释: {file_path}")
            self.added_count += 1
            return True

        except Exception as e:
            print(f"❌ 处理失败: {file_path} - {e}")
            self.failed_count += 1
            return False

    def _remove_simple_docstring(self, content: str) -> str:
        """移除简单的docstring，保留复杂的类/函数说明"""
        # 只移除文件开头的简单docstring（不超过20行）
        lines = content.lstrip().split("\n")

        # 检查是否以 """ 或 ''' 开头
        if not lines:
            return content

        first_line = lines[0].strip()
        if not (first_line.startswith('"""') or first_line.startswith("'''")):
            return content

        # 查找结束的引号
        quote = '"""' if first_line.startswith('"""') else "'''"

        # 单行docstring
        if first_line.endswith(quote) and len(first_line) > 6:
            return "\n".join(lines[1:])

        # 多行docstring (最多检查20行)
        for i in range(1, min(len(lines), 20)):
            if quote in lines[i]:
                # 找到结束位置
                return "\n".join(lines[i + 1 :])

        # 没找到结束引号，保留原内容
        return content


def batch_add_headers():
    """批量为核心文件添加头注释"""
    adder = PythonHeaderAdder()

    # 定义要处理的文件及其描述
    files_to_process = [
        # 核心接口和工厂层
        (
            "interfaces/data_source.py",
            "统一数据源接口定义，所有数据源适配器必须实现此接口",
        ),
        (
            "factory/data_source_factory.py",
            "数据源工厂类，负责创建和管理数据源适配器实例",
        ),
        # 核心管理层
        ("core.py", "MyStocks核心数据分类体系、存储策略和配置驱动表管理"),
        ("unified_manager.py", "MyStocks统一数据管理器，提供数据保存/加载的统一入口"),
        ("monitoring.py", "监控系统核心模块，提供操作日志、性能监控和数据质量检查"),
        # 6个数据源适配器
        ("adapters/akshare_adapter.py", "AkShare数据源适配器，提供A股行情和基本面数据"),
        (
            "adapters/baostock_adapter.py",
            "BaoStock数据源适配器，提供历史行情和财务数据",
        ),
        (
            "adapters/tdx_adapter.py",
            "通达信(TDX)数据源适配器，提供实时行情和多周期K线数据",
        ),
        ("adapters/financial_adapter.py", "财务数据适配器，整合多源财务报表和指标数据"),
        ("adapters/customer_adapter.py", "自定义数据源适配器，支持用户扩展数据源"),
        (
            "adapters/data_source_manager.py",
            "数据源管理器，统一管理多个数据源适配器的生命周期",
        ),
        # 4个监控模块
        (
            "monitoring/monitoring_database.py",
            "监控数据库模块，独立记录所有操作日志和指标",
        ),
        (
            "monitoring/performance_monitor.py",
            "性能监控模块，跟踪查询时间、慢查询和性能指标",
        ),
        (
            "monitoring/data_quality_monitor.py",
            "数据质量监控模块，检查完整性、新鲜度和准确性",
        ),
        ("monitoring/alert_manager.py", "告警管理模块，支持多渠道告警和告警升级策略"),
        # 其他核心文件
        (
            "data_access.py",
            "数据访问层，封装4种数据库(TDengine/PostgreSQL/MySQL/Redis)的操作",
        ),
        (
            "db_manager/database_manager.py",
            "数据库管理器，负责连接管理、表创建和结构验证",
        ),
        (
            "utils/failure_recovery_queue.py",
            "故障恢复队列，数据库不可用时缓存操作并自动重试",
        ),
        (
            "utils/tdx_server_config.py",
            "TDX服务器配置模块，管理通达信服务器列表和连接参数",
        ),
    ]

    print("\n" + "=" * 80)
    print("批量添加Python头注释 - MyStocks v2.1")
    print("=" * 80 + "\n")

    print(f"将为 {len(files_to_process)} 个核心文件添加标准头注释\n")

    # 批量处理
    for file_path, description in files_to_process:
        full_path = os.path.join(os.getcwd(), file_path)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            print(f"⚠️  文件不存在: {file_path}")
            adder.failed_count += 1
            continue

        # 添加头注释
        adder.add_header_to_file(
            full_path,
            description=description,
            author="JohnC (ninjas@sina.com) & Claude",
            created_date="2025-10-16",
            version="2.1.0",
            dependencies="详见requirements.txt或文件导入部分",
            notes="本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构",
            copyright="MyStocks Project © 2025",
        )

    # 输出统计结果
    print("\n" + "=" * 80)
    print("处理完成统计")
    print("=" * 80)
    print(f"✅ 成功添加: {adder.added_count} 个文件")
    print(f"⏭️  跳过 (已有): {adder.skipped_count} 个文件")
    print(f"❌ 处理失败: {adder.failed_count} 个文件")
    print(f"📊 总计处理: {len(files_to_process)} 个文件")

    # 计算成功率
    total_processed = adder.added_count + adder.skipped_count
    if len(files_to_process) > 0:
        compliance_rate = (total_processed / len(files_to_process)) * 100
        print(f"\n✅ 头注释覆盖率: {compliance_rate:.1f}%")

    print("\n备份文件说明: 所有修改的文件原内容已保存为 .backup 文件")
    print("=" * 80 + "\n")

    return {
        "added": adder.added_count,
        "skipped": adder.skipped_count,
        "failed": adder.failed_count,
        "total": len(files_to_process),
    }


if __name__ == "__main__":
    result = batch_add_headers()

    # 返回退出码
    if result["failed"] > 0:
        exit(1)
    else:
        exit(0)
