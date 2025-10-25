"""
Extended Risk Metrics

Provides VaR, CVaR, Beta, and other industry-standard risk measures.
Complements existing PerformanceMetrics with additional risk analysis.

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
Dependencies: numpy, pandas (existing)

Usage:
    >>> from mystocks.analysis import ExtendedRiskMetrics
    >>> var = ExtendedRiskMetrics.value_at_risk(returns)
    >>> print(f"95% VaR: {var:.2%}")
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ExtendedRiskMetrics:
    """
    Extended risk analysis metrics

    Provides Value at Risk (VaR), Conditional VaR, Beta, and correlation-adjusted
    position sizing algorithms.

    Example:
        >>> returns = pd.Series([0.01, -0.02, 0.015, ...])
        >>> metrics = ExtendedRiskMetrics.calculate_all(returns)
        >>> print(f"VaR (95%): {metrics['var_95_hist']:.2%}")
    """

    @staticmethod
    def value_at_risk(
        returns: pd.Series,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Value at Risk (VaR)

        VaR estimates the maximum loss over a given time period at a specific
        confidence level.

        Args:
            returns: Daily return series
            confidence_level: Confidence level (0.95 = 95%, 0.99 = 99%)
            method: 'historical' or 'parametric'
                - historical: Uses actual return distribution
                - parametric: Assumes normal distribution

        Returns:
            VaR value (negative indicates potential loss)

        Example:
            >>> returns = pd.Series([-0.02, 0.01, -0.01, 0.015])
            >>> var = ExtendedRiskMetrics.value_at_risk(returns, 0.95)
            >>> print(f"95% VaR: {var:.2%}")  # e.g., -3.2%
        """
        if len(returns) == 0:
            logger.warning("Empty returns series provided to VaR calculation")
            return 0.0

        if method == 'historical':
            # Use empirical percentile
            return float(np.percentile(returns, (1 - confidence_level) * 100))

        elif method == 'parametric':
            # Assume normal distribution
            mean = returns.mean()
            std = returns.std()

            # Z-scores for common confidence levels
            z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
            z_score = z_scores.get(confidence_level, 1.645)

            return float(mean - z_score * std)

        else:
            raise ValueError(
                f"Unknown method '{method}'. Use 'historical' or 'parametric'"
            )

    @staticmethod
    def conditional_var(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Conditional VaR (CVaR / Expected Shortfall)

        CVaR is the expected loss given that loss exceeds VaR.
        More conservative than VaR as it considers tail risk.

        Args:
            returns: Daily return series
            confidence_level: Confidence level (0.95 = 95%)

        Returns:
            CVaR value (average loss in worst (1-confidence)% scenarios)

        Example:
            >>> returns = pd.Series([...])
            >>> cvar = ExtendedRiskMetrics.conditional_var(returns, 0.95)
            >>> print(f"Expected loss in worst 5% cases: {cvar:.2%}")
        """
        if len(returns) == 0:
            return 0.0

        var = ExtendedRiskMetrics.value_at_risk(
            returns, confidence_level, 'historical'
        )
        worst_returns = returns[returns <= var]

        if len(worst_returns) == 0:
            return var

        return float(worst_returns.mean())

    @staticmethod
    def beta(
        asset_returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """
        Calculate Beta (market sensitivity)

        Beta measures how much an asset moves relative to the market.
        - Beta = 1: Moves with market
        - Beta > 1: More volatile than market
        - Beta < 1: Less volatile than market
        - Beta < 0: Moves opposite to market

        Args:
            asset_returns: Asset return series
            market_returns: Market return series (e.g., S&P 500)

        Returns:
            Beta coefficient

        Example:
            >>> stock_returns = pd.Series([...])
            >>> market_returns = pd.Series([...])
            >>> beta = ExtendedRiskMetrics.beta(stock_returns, market_returns)
            >>> print(f"Stock beta: {beta:.2f}")
        """
        if len(asset_returns) == 0 or len(market_returns) == 0:
            return 0.0

        # Align series
        aligned_data = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()

        if len(aligned_data) < 2:
            return 0.0

        covariance = np.cov(
            aligned_data['asset'],
            aligned_data['market']
        )[0][1]

        market_variance = np.var(aligned_data['market'])

        if market_variance == 0:
            return 0.0

        return float(covariance / market_variance)

    @staticmethod
    def calculate_all(
        returns: pd.Series,
        market_returns: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        Calculate all extended risk metrics

        Args:
            returns: Asset return series
            market_returns: Optional market return series for beta calculation

        Returns:
            Dictionary with all risk metrics

        Example:
            >>> returns = pd.Series([...])
            >>> market = pd.Series([...])
            >>> metrics = ExtendedRiskMetrics.calculate_all(returns, market)
            >>> print(f"VaR 95%: {metrics['var_95_hist']:.2%}")
            >>> print(f"CVaR 95%: {metrics['cvar_95']:.2%}")
            >>> print(f"Beta: {metrics['beta']:.2f}")
        """
        metrics = {
            'var_95_hist': ExtendedRiskMetrics.value_at_risk(
                returns, 0.95, 'historical'
            ),
            'var_95_param': ExtendedRiskMetrics.value_at_risk(
                returns, 0.95, 'parametric'
            ),
            'var_99_hist': ExtendedRiskMetrics.value_at_risk(
                returns, 0.99, 'historical'
            ),
            'cvar_95': ExtendedRiskMetrics.conditional_var(returns, 0.95),
            'cvar_99': ExtendedRiskMetrics.conditional_var(returns, 0.99)
        }

        if market_returns is not None and len(market_returns) > 0:
            metrics['beta'] = ExtendedRiskMetrics.beta(returns, market_returns)

        return metrics
