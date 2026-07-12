"""技术负债分析器 - 向后兼容入口

实际实现已拆分至 debt_analyzer/ 包。
"""

from debt_analyzer import TechnicalDebtAnalyzer  # noqa: F401
from debt_analyzer.cli import main, main_async  # noqa: F401


if __name__ == "__main__":
    main()
