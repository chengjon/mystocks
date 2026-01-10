"""
Market Data Streaming - Infrastructure Layer Implementation
实时行情流基础设施层实现

提供实时行情流适配器的具体实现，包括 Mock、WebSocket 等。
"""

from .mock_price_stream_adapter import MockPriceStreamAdapter

__all__ = ["MockPriceStreamAdapter"]
