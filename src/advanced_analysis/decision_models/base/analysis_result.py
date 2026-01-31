"""
决策模型评分系统 - 结果类

包含模型分析的结果数据结构和序列化方法
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
import json


@dataclass
class AnalysisResult:
    """分析结果基类"""

    success: bool = False
    message: str = ""
    data: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def add_error(self, error: str):
        """添加错误"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)

    def merge(self, other: "AnalysisResult"):
        """合并另一个结果"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.success = self.success and other.success


@dataclass
class ModelAnalysisResult(AnalysisResult):
    """模型分析结果"""

    model_name: str = ""
    model_type: str = ""  # buffett, canslim, fisher, synthesis

    # 分析数据
    analysis_data: Optional[Dict] = None
    score: Optional[float] = None
    rating: Optional[str] = None

    # 综合数据
    valuation_score: Optional[float] = None
    growth_score: Optional[float] = None
    quality_score: Optional[float] = None
    technical_score: Optional[float] = None

    def get_summary(self) -> str:
        """获取分析摘要"""
        summary_parts = []

        if self.model_name:
            summary_parts.append(f"模型: {self.model_name}")

        if self.rating:
            summary_parts.append(f"评级: {self.rating}")

        if self.score is not None:
            summary_parts.append(f"评分: {self.score:.1f}")

        return " | ".join(summary_parts)

    def get_score_breakdown(self) -> Dict:
        """获取评分明细"""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "overall_score": self.score,
            "rating": self.rating,
            "score_breakdown": {
                "valuation": self.valuation_score,
                "growth": self.growth_score,
                "quality": self.quality_score,
                "technical": self.technical_score,
            },
            "analysis_data": self.analysis_data,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class BatchAnalysisResult(AnalysisResult):
    """批量分析结果"""

    total_stocks: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0

    # 分析结果列表
    results: List[ModelAnalysisResult] = field(default_factory=list)

    # 统计数据
    score_distribution: Dict[str, int] = field(default_factory=dict)
    rating_distribution: Dict[str, int] = field(default_factory=dict)

    # 时间统计
    analysis_time: Optional[float] = None
    avg_time_per_stock: Optional[float] = None

    def add_result(self, result: ModelAnalysisResult):
        """添加分析结果"""
        self.results.append(result)
        self.total_stocks += 1

        if result.success:
            self.successful_analyses += 1

            if result.rating:
                self.rating_distribution[result.rating] = self.rating_distribution.get(result.rating, 0) + 1

            if result.score is not None:
                score_range = self._get_score_range(result.score)
                self.score_distribution[score_range] = self.score_distribution.get(score_range, 0) + 1
        else:
            self.failed_analyses += 1

    def _get_score_range(self, score: float) -> str:
        """获取评分范围"""
        if score >= 80:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        else:
            return "D"

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_stocks": self.total_stocks,
            "successful_analyses": self.successful_analyses,
            "failed_analyses": self.failed_analyses,
            "success_rate": (self.successful_analyses / self.total_stocks * 100) if self.total_stocks > 0 else 0,
            "score_distribution": self.score_distribution,
            "rating_distribution": self.rating_distribution,
            "analysis_time": self.analysis_time,
            "avg_time_per_stock": self.avg_time_per_stock,
        }

    def export_results(self, filepath: str):
        """导出结果到文件"""
        results_data = {
            "summary": self.get_statistics(),
            "results": [r.get_score_breakdown() for r in self.results],
            "timestamp": self.timestamp.isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
