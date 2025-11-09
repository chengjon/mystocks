"""
报告生成模块 (Reporting Module)

提供专业的PDF报告生成功能:
- 策略回测报告
- 月度/季度报告
- 性能分析报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

from .pdf_generator import PDFReportGenerator

__all__ = ["PDFReportGenerator"]

__version__ = "1.0.0"
