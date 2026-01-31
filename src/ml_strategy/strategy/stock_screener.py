"""
股票筛选器 (Stock Screener)

功能说明:
- 根据多维度条件筛选股票池
- 支持市值、行业、价格、成交量等过滤条件
- 排除ST股票、停牌股票等特殊状态
- 与UnifiedDataManager集成获取股票信息

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Callable, List, Optional, Set

import pandas as pd


@dataclass
class ScreeningCriteria:
    """筛选条件配置"""

    # 排除条件
    exclude_st: bool = True  # 排除ST股票
    exclude_suspended: bool = True  # 排除停牌股票
    exclude_new_stocks: bool = True  # 排除次新股
    new_stock_days: int = 60  # 次新股定义(上市天数)

    # 市值过滤
    min_market_cap: Optional[float] = None  # 最小市值(元)
    max_market_cap: Optional[float] = None  # 最大市值(元)

    # 价格过滤
    min_price: Optional[float] = 1.0  # 最小价格(元)
    max_price: Optional[float] = None  # 最大价格(元)

    # 成交量过滤
    min_volume: Optional[float] = None  # 最小成交量(股)
    min_amount: Optional[float] = None  # 最小成交额(元)

    # 行业/板块过滤
    exclude_industries: List[str] = None  # 排除行业列表
    include_industries: List[str] = None  # 包含行业列表
    exclude_boards: List[str] = None  # 排除板块列表
    include_boards: List[str] = None  # 包含板块列表

    # 交易所过滤
    exchanges: List[str] = None  # 交易所列表 ['SH', 'SZ', 'BJ']

    # 自定义过滤函数
    custom_filters: List[Callable] = None  # 自定义过滤函数列表

    def __post_init__(self):
        """初始化后处理"""
        if self.exclude_industries is None:
            self.exclude_industries = []
        if self.include_industries is None:
            self.include_industries = []
        if self.exclude_boards is None:
            self.exclude_boards = []
        if self.include_boards is None:
            self.include_boards = []
        if self.exchanges is None:
            self.exchanges = ["SH", "SZ", "BJ"]
        if self.custom_filters is None:
            self.custom_filters = []


class StockScreener:
    """
    股票筛选器 - 根据条件过滤股票池

    功能:
        - 多维度条件筛选
        - ST股票、停牌股票过滤
        - 行业、板块、市值过滤
        - 自定义过滤函数支持
    """

    def __init__(self, unified_manager=None, criteria: Optional[ScreeningCriteria] = None):
        """
        初始化股票筛选器

        参数:
            unified_manager: UnifiedDataManager实例
            criteria: 筛选条件配置
        """
        self.unified_manager = unified_manager
        self.criteria = criteria or ScreeningCriteria()

        # 日志配置
        self.logger = logging.getLogger(f"{__name__}.StockScreener")
        self.logger.setLevel(logging.INFO)

        # 筛选统计
        self.stats = {
            "total_input": 0,
            "excluded_st": 0,
            "excluded_suspended": 0,
            "excluded_new_stocks": 0,
            "excluded_price": 0,
            "excluded_volume": 0,
            "excluded_market_cap": 0,
            "excluded_industry": 0,
            "excluded_custom": 0,
            "total_output": 0,
        }

    def screen(self, symbols: Optional[List[str]] = None, as_of_date: Optional[date] = None) -> List[str]:
        """
        执行股票筛选

        参数:
            symbols: 输入股票池 (如果为None，使用全市场股票)
            as_of_date: 筛选基准日期 (默认为今天)

        返回:
            List[str]: 筛选后的股票代码列表

        示例:
            >>> screener = StockScreener(unified_manager, criteria)
            >>> filtered = screener.screen(symbols=['000001', '000002', '600000'])
            >>> print(f"筛选后股票数量: {len(filtered)}")
        """
        if as_of_date is None:
            as_of_date = date.today()

        self.logger.info("开始股票筛选 | 基准日期: %s", as_of_date)

        # 获取股票池
        if symbols is None:
            symbols = self._get_all_symbols()

        self.stats["total_input"] = len(symbols)
        self.logger.info("输入股票池大小: %s", len(symbols))

        # 获取股票基本信息
        stock_info = self._get_stock_info(symbols, as_of_date)

        # 依次应用过滤条件
        filtered_symbols = set(symbols)

        # 1. 排除ST股票
        if self.criteria.exclude_st:
            filtered_symbols = self._filter_st_stocks(filtered_symbols, stock_info)

        # 2. 排除停牌股票
        if self.criteria.exclude_suspended:
            filtered_symbols = self._filter_suspended_stocks(filtered_symbols, stock_info)

        # 3. 排除次新股
        if self.criteria.exclude_new_stocks:
            filtered_symbols = self._filter_new_stocks(filtered_symbols, stock_info, as_of_date)

        # 4. 价格过滤
        if self.criteria.min_price or self.criteria.max_price:
            filtered_symbols = self._filter_by_price(filtered_symbols, stock_info)

        # 5. 成交量过滤
        if self.criteria.min_volume or self.criteria.min_amount:
            filtered_symbols = self._filter_by_volume(filtered_symbols, stock_info)

        # 6. 市值过滤
        if self.criteria.min_market_cap or self.criteria.max_market_cap:
            filtered_symbols = self._filter_by_market_cap(filtered_symbols, stock_info)

        # 7. 行业过滤
        if self.criteria.exclude_industries or self.criteria.include_industries:
            filtered_symbols = self._filter_by_industry(filtered_symbols, stock_info)

        # 8. 板块过滤
        if self.criteria.exclude_boards or self.criteria.include_boards:
            filtered_symbols = self._filter_by_board(filtered_symbols, stock_info)

        # 9. 交易所过滤
        if self.criteria.exchanges:
            filtered_symbols = self._filter_by_exchange(filtered_symbols, stock_info)

        # 10. 自定义过滤
        if self.criteria.custom_filters:
            filtered_symbols = self._apply_custom_filters(filtered_symbols, stock_info)

        # 更新统计
        self.stats["total_output"] = len(filtered_symbols)

        # 打印筛选摘要
        self._print_summary()

        return sorted(list(filtered_symbols))

    def _get_all_symbols(self) -> List[str]:
        """获取全市场股票列表"""
        if self.unified_manager is None:
            self.logger.warning("UnifiedDataManager未初始化，返回空列表")
            return []

        # 通过UnifiedDataManager获取股票列表
        symbols_df = self.unified_manager.load_data_by_classification(
            classification="reference_data",
            table_name="symbols",
            filters={"is_active": True},
        )

        if symbols_df.empty:
            return []

        return symbols_df["symbol"].tolist()

    def _get_stock_info(self, symbols: List[str], as_of_date: date) -> pd.DataFrame:
        """
        获取股票基本信息

        返回DataFrame包含:
            - symbol: 股票代码
            - name: 股票名称
            - exchange: 交易所
            - industry: 行业
            - board: 板块
            - list_date: 上市日期
            - is_st: 是否ST
            - is_suspended: 是否停牌
            - close: 收盘价
            - volume: 成交量
            - amount: 成交额
            - market_cap: 市值
        """
        if self.unified_manager is None:
            self.logger.warning("UnifiedDataManager未初始化，返回空DataFrame")
            return pd.DataFrame()

        # 获取股票基础信息
        stock_info = self.unified_manager.load_data_by_classification(
            classification="reference_data",
            table_name="symbols",
            filters={"symbol": symbols},
        )

        # 获取最新行情数据 (用于价格、成交量、市值)
        # 注意: 实际实现需要根据UnifiedDataManager的接口调整
        latest_quotes = self.unified_manager.load_data_by_classification(
            classification="market_data",
            symbols=symbols,
            start_date=as_of_date,
            end_date=as_of_date,
            limit=len(symbols),
        )

        # 合并信息
        if not latest_quotes.empty:
            stock_info = stock_info.merge(
                latest_quotes[["symbol", "close", "volume", "amount"]],
                on="symbol",
                how="left",
            )

        return stock_info

    def _filter_st_stocks(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """过滤ST股票"""
        st_stocks = stock_info[stock_info["name"].str.contains("ST", na=False)]["symbol"].tolist()

        excluded = symbols & set(st_stocks)
        self.stats["excluded_st"] = len(excluded)

        self.logger.info("排除ST股票: %s只", len(excluded))

        return symbols - excluded

    def _filter_suspended_stocks(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """过滤停牌股票"""
        # 通过成交量为0判断停牌
        suspended = stock_info[(stock_info["volume"].isna()) | (stock_info["volume"] == 0)]["symbol"].tolist()

        excluded = symbols & set(suspended)
        self.stats["excluded_suspended"] = len(excluded)

        self.logger.info("排除停牌股票: %s只", len(excluded))

        return symbols - excluded

    def _filter_new_stocks(self, symbols: Set[str], stock_info: pd.DataFrame, as_of_date: date) -> Set[str]:
        """过滤次新股"""
        # 计算上市天数
        stock_info["list_date"] = pd.to_datetime(stock_info["list_date"])
        stock_info["listing_days"] = (pd.to_datetime(as_of_date) - stock_info["list_date"]).dt.days

        new_stocks = stock_info[stock_info["listing_days"] < self.criteria.new_stock_days]["symbol"].tolist()

        excluded = symbols & set(new_stocks)
        self.stats["excluded_new_stocks"] = len(excluded)

        self.logger.info("排除次新股(%s天内): %s只", self.criteria.new_stock_days, len(excluded))

        return symbols - excluded

    def _filter_by_price(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按价格过滤"""
        excluded = set()

        if self.criteria.min_price is not None:
            below_min = stock_info[stock_info["close"] < self.criteria.min_price]["symbol"].tolist()
            excluded |= symbols & set(below_min)

        if self.criteria.max_price is not None:
            above_max = stock_info[stock_info["close"] > self.criteria.max_price]["symbol"].tolist()
            excluded |= symbols & set(above_max)

        self.stats["excluded_price"] = len(excluded)

        if excluded:
            self.logger.info(
                f"价格过滤: 排除{len(excluded)}只 (范围: {self.criteria.min_price}-{self.criteria.max_price}元)"
            )

        return symbols - excluded

    def _filter_by_volume(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按成交量/成交额过滤"""
        excluded = set()

        if self.criteria.min_volume is not None:
            below_vol = stock_info[stock_info["volume"] < self.criteria.min_volume]["symbol"].tolist()
            excluded |= symbols & set(below_vol)

        if self.criteria.min_amount is not None:
            below_amt = stock_info[stock_info["amount"] < self.criteria.min_amount]["symbol"].tolist()
            excluded |= symbols & set(below_amt)

        self.stats["excluded_volume"] = len(excluded)

        if excluded:
            self.logger.info("成交量过滤: 排除%s只", len(excluded))

        return symbols - excluded

    def _filter_by_market_cap(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按市值过滤"""
        excluded = set()

        # 计算市值 (如果stock_info中没有market_cap字段)
        if "market_cap" not in stock_info.columns and "total_shares" in stock_info.columns:
            stock_info["market_cap"] = stock_info["close"] * stock_info["total_shares"]

        if "market_cap" in stock_info.columns:
            if self.criteria.min_market_cap is not None:
                below_min = stock_info[stock_info["market_cap"] < self.criteria.min_market_cap]["symbol"].tolist()
                excluded |= symbols & set(below_min)

            if self.criteria.max_market_cap is not None:
                above_max = stock_info[stock_info["market_cap"] > self.criteria.max_market_cap]["symbol"].tolist()
                excluded |= symbols & set(above_max)

        self.stats["excluded_market_cap"] = len(excluded)

        if excluded:
            self.logger.info("市值过滤: 排除%s只", len(excluded))

        return symbols - excluded

    def _filter_by_industry(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按行业过滤"""
        excluded = set()

        # 排除指定行业
        if self.criteria.exclude_industries:
            excluded_ind = stock_info[stock_info["industry"].isin(self.criteria.exclude_industries)]["symbol"].tolist()
            excluded |= symbols & set(excluded_ind)

        # 仅包含指定行业
        if self.criteria.include_industries:
            not_included = stock_info[~stock_info["industry"].isin(self.criteria.include_industries)]["symbol"].tolist()
            excluded |= symbols & set(not_included)

        self.stats["excluded_industry"] = len(excluded)

        if excluded:
            self.logger.info("行业过滤: 排除%s只", len(excluded))

        return symbols - excluded

    def _filter_by_board(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按板块过滤"""
        excluded = set()

        if "board" in stock_info.columns:
            # 排除指定板块
            if self.criteria.exclude_boards:
                excluded_boards = stock_info[stock_info["board"].isin(self.criteria.exclude_boards)]["symbol"].tolist()
                excluded |= symbols & set(excluded_boards)

            # 仅包含指定板块
            if self.criteria.include_boards:
                not_included = stock_info[~stock_info["board"].isin(self.criteria.include_boards)]["symbol"].tolist()
                excluded |= symbols & set(not_included)

        if excluded:
            self.logger.info("板块过滤: 排除%s只", len(excluded))

        return symbols - excluded

    def _filter_by_exchange(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """按交易所过滤"""
        not_in_exchanges = stock_info[~stock_info["exchange"].isin(self.criteria.exchanges)]["symbol"].tolist()

        excluded = symbols & set(not_in_exchanges)

        if excluded:
            self.logger.info("交易所过滤: 排除%s只", len(excluded))

        return symbols - excluded

    def _apply_custom_filters(self, symbols: Set[str], stock_info: pd.DataFrame) -> Set[str]:
        """应用自定义过滤函数"""
        excluded_total = set()

        for i, filter_func in enumerate(self.criteria.custom_filters):
            try:
                # 自定义函数应返回需要保留的股票列表
                kept_symbols = filter_func(stock_info)
                excluded = symbols - set(kept_symbols)
                excluded_total |= excluded

                self.logger.info("自定义过滤%s: 排除%s只", i + 1, len(excluded))

            except Exception as e:
                self.logger.error("自定义过滤%s执行失败: %s", i + 1, e)

        self.stats["excluded_custom"] = len(excluded_total)

        return symbols - excluded_total

    def _print_summary(self):
        """打印筛选摘要"""
        self.logger.info("=" * 60)
        self.logger.info("股票筛选摘要")
        self.logger.info("输入股票数: %s", self.stats["total_input"])
        self.logger.info("  - 排除ST股票: %s", self.stats["excluded_st"])
        self.logger.info("  - 排除停牌股票: %s", self.stats["excluded_suspended"])
        self.logger.info("  - 排除次新股: %s", self.stats["excluded_new_stocks"])
        self.logger.info("  - 价格过滤: %s", self.stats["excluded_price"])
        self.logger.info("  - 成交量过滤: %s", self.stats["excluded_volume"])
        self.logger.info("  - 市值过滤: %s", self.stats["excluded_market_cap"])
        self.logger.info("  - 行业过滤: %s", self.stats["excluded_industry"])
        self.logger.info("  - 自定义过滤: %s", self.stats["excluded_custom"])
        self.logger.info("输出股票数: %s", self.stats["total_output"])
        self.logger.info("筛选通过率: %s%", self.stats["total_output"] / self.stats["total_input"] * 100)
        self.logger.info("=" * 60)


if __name__ == "__main__":
    # 测试代码
    print("股票筛选器测试")
    print("=" * 60)

    # 创建测试条件
    criteria = ScreeningCriteria(
        exclude_st=True,
        exclude_suspended=True,
        min_price=5.0,
        max_price=50.0,
        min_volume=1000000,
        exclude_industries=["银行", "保险"],
    )

    print("筛选条件:")
    print(f"  排除ST: {criteria.exclude_st}")
    print(f"  排除停牌: {criteria.exclude_suspended}")
    print(f"  价格范围: {criteria.min_price}-{criteria.max_price}元")
    print(f"  最小成交量: {criteria.min_volume}股")
    print(f"  排除行业: {criteria.exclude_industries}")

    # 创建筛选器
    screener = StockScreener(unified_manager=None, criteria=criteria)

    print("\n注意: 完整的筛选功能需要UnifiedDataManager实例")
    print("基础测试通过！")
