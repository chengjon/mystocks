"""
分析模块API

提供情感分析、回测和压力测试功能

子模块:
- sentiment.py: 情感分析
- backtest.py: 高级回测
- stress_test.py: 压力测试
- kronos.py: Kronos 外部服务集成
"""

from .backtest import router as backtest_router
from .kronos import router as kronos_router
from .sentiment import router as sentiment_router
from .stress_test import router as stress_test_router

__all__ = ["sentiment_router", "backtest_router", "stress_test_router", "kronos_router"]
