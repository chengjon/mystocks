"""
止损引擎实现
Stop Loss Engine Implementation

实现波动率自适应止损和跟踪止损策略。
复用现有的监控和交易基础设施。
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np

from src.governance.risk_management.core import IStopLossEngine
from .stop_loss_engine import StopLossEngine

# 复用现有的数据源和监控基础设施
try:
    from src.monitoring.signal_recorder import get_signal_recorder

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)

def get_stop_loss_engine() -> StopLossEngine:
    """获取止损引擎实例（单例模式）"""
    global _stop_loss_engine_instance
    if _stop_loss_engine_instance is None:
        _stop_loss_engine_instance = StopLossEngine()
    return _stop_loss_engine_instance


