"""UsageFeedbackAnalyzer 方法级拆分包"""

from .part1 import UsageFeedbackAnalyzerCoreMixin
from .part2 import UsageFeedbackAnalyzerGenerateUsageReportMixin


class UsageFeedbackAnalyzer(
    UsageFeedbackAnalyzerCoreMixin,
    UsageFeedbackAnalyzerGenerateUsageReportMixin,
):
    """UsageFeedbackAnalyzer - 组合所有方法集"""


__all__ = ["UsageFeedbackAnalyzer"]
