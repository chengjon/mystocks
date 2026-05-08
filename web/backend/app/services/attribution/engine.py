from __future__ import annotations

from .errors import AttributionInputError
from .models import (
    AttributionAnalysisResult,
    BenchmarkConstituentSnapshot,
    BrinsonBreakdown,
    ContributionRow,
    FactorAttributionPayload,
    FactorExposureDetail,
    FactorExposureSnapshot,
    PortfolioConstituentSnapshot,
    SnapshotMeta,
)

FACTOR_PREMIUMS: dict[str, float] = {
    "size": 0.02,
    "value": 0.015,
    "momentum": 0.025,
    "volatility": -0.01,
    "quality": 0.018,
}


class AttributionEngine:
    def analyze(
        self,
        portfolio: list[PortfolioConstituentSnapshot],
        benchmark: list[BenchmarkConstituentSnapshot],
        factors: FactorExposureSnapshot,
    ) -> AttributionAnalysisResult:
        if not portfolio:
            raise AttributionInputError("portfolio must not be empty")
        if not benchmark:
            raise AttributionInputError("benchmark must not be empty")

        contribution_rows = [
            ContributionRow(
                symbol=row.symbol,
                industry=row.industry,
                weight=row.weight,
                return_rate=row.return_rate,
                contribution_value=row.weight * row.return_rate,
            )
            for row in portfolio
        ]
        contribution_rows.sort(key=lambda row: row.contribution_value, reverse=True)

        portfolio_total_return = sum(row.contribution_value for row in contribution_rows)
        benchmark_total_return = sum(row.weight * row.return_rate for row in benchmark)

        brinson = self._build_brinson_breakdown(portfolio=portfolio, benchmark=benchmark)
        factor_attribution = self._build_factor_attribution(
            factors=factors,
            portfolio_total_return=portfolio_total_return,
            benchmark_total_return=benchmark_total_return,
        )

        return AttributionAnalysisResult(
            analysis_date=factors.analysis_date,
            snapshot_meta=SnapshotMeta(
                analysis_date=factors.analysis_date,
                constituent_count=len(portfolio),
                total_weight=sum(row.weight for row in portfolio),
                total_market_value=sum(row.market_value for row in portfolio),
                total_return=portfolio_total_return,
            ),
            benchmark_meta=SnapshotMeta(
                analysis_date=factors.analysis_date,
                constituent_count=len(benchmark),
                total_weight=sum(row.weight for row in benchmark),
                total_market_value=None,
                total_return=benchmark_total_return,
            ),
            brinson=brinson,
            factor_attribution=factor_attribution,
            top_contributors=contribution_rows,
            top_detractors=sorted(contribution_rows, key=lambda row: row.contribution_value),
        )

    def _build_brinson_breakdown(
        self,
        portfolio: list[PortfolioConstituentSnapshot],
        benchmark: list[BenchmarkConstituentSnapshot],
    ) -> BrinsonBreakdown:
        portfolio_industries = self._group_industry_metrics(portfolio)
        benchmark_industries = self._group_industry_metrics(benchmark)

        allocation_total = 0.0
        selection_total = 0.0
        interaction_total = 0.0
        industry_breakdown: dict[str, dict[str, float]] = {}

        for industry in sorted(set(portfolio_industries) | set(benchmark_industries)):
            p_metrics = portfolio_industries.get(industry, {"weight": 0.0, "return": 0.0})
            b_metrics = benchmark_industries.get(industry, {"weight": 0.0, "return": 0.0})

            allocation = (p_metrics["weight"] - b_metrics["weight"]) * b_metrics["return"]
            selection = b_metrics["weight"] * (p_metrics["return"] - b_metrics["return"])
            interaction = (p_metrics["weight"] - b_metrics["weight"]) * (p_metrics["return"] - b_metrics["return"])

            allocation_total += allocation
            selection_total += selection
            interaction_total += interaction
            industry_breakdown[industry] = {
                "portfolio_weight": p_metrics["weight"],
                "benchmark_weight": b_metrics["weight"],
                "portfolio_return": p_metrics["return"],
                "benchmark_return": b_metrics["return"],
                "allocation_effect": allocation,
                "selection_effect": selection,
                "interaction_effect": interaction,
            }

        return BrinsonBreakdown(
            allocation_effect=allocation_total,
            selection_effect=selection_total,
            interaction_effect=interaction_total,
            industry_breakdown=industry_breakdown,
        )

    def _build_factor_attribution(
        self,
        factors: FactorExposureSnapshot,
        portfolio_total_return: float,
        benchmark_total_return: float,
    ) -> FactorAttributionPayload:
        factor_exposures: dict[str, FactorExposureDetail] = {}
        factor_contributions: dict[str, float] = {}

        for factor_name in sorted(set(factors.portfolio) | set(factors.benchmark)):
            portfolio_exposure = factors.portfolio.get(factor_name, 0.0)
            benchmark_exposure = factors.benchmark.get(factor_name, 0.0)
            active_exposure = portfolio_exposure - benchmark_exposure

            factor_exposures[factor_name] = FactorExposureDetail(
                portfolio_exposure=portfolio_exposure,
                benchmark_exposure=benchmark_exposure,
                active_exposure=active_exposure,
            )
            factor_contributions[factor_name] = active_exposure * FACTOR_PREMIUMS.get(factor_name, 0.0)

        specific_return = portfolio_total_return - benchmark_total_return - sum(factor_contributions.values())
        return FactorAttributionPayload(
            factor_exposures=factor_exposures,
            factor_contributions=factor_contributions,
            specific_return=specific_return,
        )

    @staticmethod
    def _group_industry_metrics(
        rows: list[PortfolioConstituentSnapshot] | list[BenchmarkConstituentSnapshot],
    ) -> dict[str, dict[str, float]]:
        grouped: dict[str, dict[str, float]] = {}
        for row in rows:
            metrics = grouped.setdefault(row.industry, {"weight": 0.0, "contribution": 0.0})
            metrics["weight"] += row.weight
            metrics["contribution"] += row.weight * row.return_rate

        for metrics in grouped.values():
            metrics["return"] = metrics["contribution"] / metrics["weight"] if metrics["weight"] else 0.0
            metrics.pop("contribution", None)

        return grouped


AttributionAnalysisEngine = AttributionEngine

__all__ = [
    "AttributionAnalysisEngine",
    "AttributionAnalysisResult",
    "AttributionEngine",
    "BenchmarkConstituentSnapshot",
    "BrinsonBreakdown",
    "ContributionRow",
    "FactorAttributionPayload",
    "FactorExposureDetail",
    "FactorExposureSnapshot",
    "PortfolioConstituentSnapshot",
    "SnapshotMeta",
]
