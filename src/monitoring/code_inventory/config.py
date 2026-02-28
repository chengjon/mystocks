"""扫描配置"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ScanConfig:
    """扫描配置"""

    # 需要扫描的目录
    scan_dirs: List[str] = field(default_factory=lambda: [
        "src",
        "scripts",
        "web/backend/app",
    ])

    # 需要扫描的文件类型（按编码规则判断是否有必要拆分）
    file_extensions: List[str] = field(default_factory=lambda: [
        ".py",      # Python 文件
        ".vue",     # Vue 组件
        ".ts",      # TypeScript
        ".tsx",     # React TypeScript
        ".js",      # JavaScript
        ".jsx",     # React
    ])

    # 排除的目录
    exclude_dirs: List[str] = field(default_factory=lambda: [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "archived",
        ".archive",
        "archive",
        "tests/legacy",
        ".venv",
        "venv",
        ".env",
    ])

    # 超过此行数进行标记
    line_threshold: int = 1000

    # Mock 检测模式 - import 导入
    mock_import_patterns: List[str] = field(default_factory=lambda: [
        # 直接导入 mock 模块
        r"from\s+src\.mock\.",
        r"from\s+src\.data_sources\.mock",
        r"from\s+src\.data_sources\.mock_data_source",
        r"import\s+mock_",
        r"from\s+.*mock\s+import",
    ])

    # Mock 函数调用模式
    mock_call_patterns: List[str] = field(default_factory=lambda: [
        r"get_\w+_source\s*\(\s*['\"]mock['\"]\s*\)",
        r"MockDataSource\s*\(",
        r"Mock\w+DataSource\s*\(",
        r"USE_MOCK_DATA\s*=\s*['\"]?true",
    ])

    # 扫描结果存储目录
    output_dir: str = "data/code_inventory"

    # 项目根目录
    project_root: str = "."

