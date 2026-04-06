"""Monitoring test package.

Avoid eager re-export imports here. Pytest imports this package during test
collection, and pulling in every monitoring helper module creates unrelated
collection-time failures for focused tests.
"""

__all__: list[str] = []

# 版本信息
__version__ = "1.0.0"
__author__ = "MyStocks Testing Team"
__description__ = "Test Monitoring and Alerting System"
