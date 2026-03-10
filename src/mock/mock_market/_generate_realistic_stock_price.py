"""
Mock数据文件: Market
提供接口:
1. get_market_heatmap() -> List[Dict] - 获取市场热力图数据
2. get_real_time_quotes() -> List[Dict] - 获取实时行情
3. get_fund_flow() -> List[Dict] - 获取资金流向数据
4. get_etf_list() -> List[Dict] - 获取ETF列表
5. get_chip_race() -> List[Dict] - 获取竞价抢筹数据
6. get_lhb_detail() -> List[Dict] - 获取龙虎榜数据
7. get_stock_list() -> List[Dict] - 获取股票列表
8. get_kline_data() -> List[Dict] - 获取K线数据
"""

from ._market_heatmap import get_market_heatmap
from ._market_helpers import (
    _generate_correlated_change,
    _generate_realistic_stock_price,
    _generate_realistic_volume,
)
from ._market_quotes import get_fund_flow, get_real_time_quotes
from ._market_rankings import get_chip_race, get_lhb_detail
from ._market_reference import get_etf_list, get_stock_list

__all__ = [
    "_generate_correlated_change",
    "_generate_realistic_stock_price",
    "_generate_realistic_volume",
    "get_chip_race",
    "get_etf_list",
    "get_fund_flow",
    "get_lhb_detail",
    "get_market_heatmap",
    "get_real_time_quotes",
    "get_stock_list",
]
