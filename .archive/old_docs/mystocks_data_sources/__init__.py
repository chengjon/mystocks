"""
Data Sources Module

External data source integrations for MyStocks.

Author: JohnC & Claude
Version: 1.0.0
"""

from .sec_fetcher import SECFetcher

__all__ = ["SECFetcher"]
