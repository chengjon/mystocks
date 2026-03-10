"""
Fundamental analysis data models.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FinancialRatios:
    profitability: Dict[str, float] = None
    solvency: Dict[str, float] = None
    operation: Dict[str, float] = None
    growth: Dict[str, float] = None
    cashflow: Dict[str, float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FundamentalScore:
    overall_score: float
    dimension_scores: Dict[str, float]
    rating: str
    industry_percentile: float
    red_flags: List[str]
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class ValuationMetrics:
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    dividend_yield: Optional[float] = None
    pe_percentile: Optional[float] = None
    pb_percentile: Optional[float] = None
    pe_vs_industry: Optional[float] = None
    pb_vs_industry: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
