"""
技术负债分析器包

提供代码质量、架构、性能、安全、依赖、覆盖率、文档、配置等维度的技术负债分析。
"""

from .core_analyzer import CoreAnalyzerMixin
from .code_quality_analyzer import CodeQualityMixin
from .architecture_analyzer import ArchitectureMixin
from .performance_security_analyzer import PerformanceSecurityMixin
from .dependency_analyzer import DependencyMixin
from .coverage_docs_analyzer import CoverageDocsMixin
from .report_generator import ReportMixin


class TechnicalDebtAnalyzer(
    CoreAnalyzerMixin,
    CodeQualityMixin,
    ArchitectureMixin,
    PerformanceSecurityMixin,
    DependencyMixin,
    CoverageDocsMixin,
    ReportMixin,
):
    """技术负债分析器 - 组合所有分析维度"""
    pass


__all__ = ["TechnicalDebtAnalyzer"]
