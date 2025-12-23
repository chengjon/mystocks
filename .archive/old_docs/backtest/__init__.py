"""
MyStocks回测系统 - 简化MVP版本

基于first-principles审核，专注核心价值：
- 真实交易成本建模（佣金、印花税、滑点）
- 完整账户追踪
- 简洁实现（250行核心代码）

作者: JohnC & Claude
版本: 3.1.0 (Simplified MVP)
创建日期: 2025-10-24
"""

from .exchange import Exchange
from .account import Account
from .engine import BacktestEngine

__all__ = ["Exchange", "Account", "BacktestEngine"]
