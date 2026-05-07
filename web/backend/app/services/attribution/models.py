from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioConstituentSnapshot:
    analysis_date: str
    symbol: str
    weight: float
    market_value: float
    return_rate: float
    industry: str


@dataclass(frozen=True)
class BenchmarkConstituentSnapshot:
    analysis_date: str
    symbol: str
    weight: float
    return_rate: float
    industry: str


@dataclass(frozen=True)
class FactorExposureSnapshot:
    analysis_date: str
    portfolio: dict[str, float]
    benchmark: dict[str, float]


@dataclass(frozen=True)
class FactorExposureDetail:
    portfolio_exposure: float
    benchmark_exposure: float
    active_exposure: float


@dataclass(frozen=True)
class BrinsonBreakdown:
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    industry_breakdown: dict[str, dict[str, float]]


@dataclass(frozen=True)
class FactorAttributionPayload:
    factor_exposures: dict[str, FactorExposureDetail]
    factor_contributions: dict[str, float]
    specific_return: float


@dataclass(frozen=True)
class ContributionRow:
    symbol: str
    industry: str
    weight: float
    return_rate: float
    contribution_value: float


@dataclass(frozen=True)
class AttributionAnalysisResult:
    analysis_date: str
    brinson: BrinsonBreakdown
    factor_attribution: FactorAttributionPayload
    top_contributors: list[ContributionRow]
    top_detractors: list[ContributionRow]
