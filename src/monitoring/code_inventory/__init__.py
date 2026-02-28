"""代码监控和登记模块

功能：
1. 扫描并登记代码行数超过1000行的代码文件
2. 扫描并登记使用了Mock数据的Python文件
3. 检查.env配置，确保REAL模式下不使用MOCK数据源

目录结构：
    src/monitoring/code_inventory/
    ├── __init__.py       # 模块入口
    ├── config.py         # 扫描配置
    ├── models.py         # 数据模型
    ├── line_counter.py   # 行数统计
    ├── mock_detector.py # Mock检测器
    ├── env_checker.py    # .env配置检查
    ├── scanner.py        # 核心扫描器
    ├── storage.py        # 结果存储
    ├── reporter.py       # 报告生成
    └── cli.py           # CLI入口
"""

from .config import ScanConfig
from .models import (
    FileInventoryRecord,
    MockDetectionResult,
    ScanSummary,
    EnvConfigInfo,
    ValidationResult,
)
from .scanner import CodeInventoryScanner
from .env_checker import EnvConfigChecker

__all__ = [
    "ScanConfig",
    "FileInventoryRecord",
    "MockDetectionResult",
    "ScanSummary",
    "EnvConfigInfo",
    "ValidationResult",
    "CodeInventoryScanner",
    "EnvConfigChecker",
]
