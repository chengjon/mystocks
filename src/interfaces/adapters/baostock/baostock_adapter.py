"""
BaoStock Data Source Adapter
Baostock 数据源适配器

将 baostock 接口集成到 DataSourceManagerV2 系统中。
"""

import contextlib
import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import baostock as bs
import pandas as pd

logger = logging.getLogger(__name__)


def _login():
    """登录 baostock"""
    with open(os.devnull, "w") as fnull, contextlib.redirect_stdout(fnull):
        return bs.login()


def _logout():
    """登出 baostock"""
    with open(os.devnull, "w") as fnull, contextlib.redirect_stdout(fnull):
        bs.logout()


def _rs_to_df(rs, error_msg="查询失败"):
    """将 baostock rs 对象转换为 DataFrame"""
    if rs.error_code != "0":
        logger.error("%(error_msg)s: {rs.error_msg")
        return pd.DataFrame()
    data_list = []
    while rs.error_code == "0" and rs.next():
        data_list.append(rs.get_row_data())
    return pd.DataFrame(data_list, columns=rs.fields)


def _normalize_code(code):
    """统一股票代码格式为 sh.600000、sz.000001"""
    code = str(code).strip().lower()
    if code.startswith("sh.") or code.startswith("sz."):
        return code
    elif code.startswith("sh") and len(code) == 8:
        return "sh." + code[2:]
    elif code.startswith("sz") and len(code) == 8:
        return "sz." + code[2:]
    elif code.isdigit() and len(code) == 6:
        if code.startswith("6"):
            return "sh." + code
        else:
            return "sz." + code
    else:
        return code


def with_baostock_login(func):
    """装饰器：自动登录、登出"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        lg = _login()
        if hasattr(lg, "error_code") and lg.error_code != "0":
            logger.error("Baostock登录失败: {lg.error_msg")
            return pd.DataFrame()
        try:
            return func(*args, **kwargs)
        finally:
            _logout()

    return wrapper


class BaoStockAdapter:
    """
    BaoStock 数据源适配器

    提供与 DataSourceManagerV2 兼容的接口。
    """

    def __init__(self):
        pass

    @with_baostock_login
    def get_daily_kline(
        self, symbol: str, start_date: str = None, end_date: str = None, adjust: str = "qfq"
    ) -> pd.DataFrame:
        """
        获取日K线数据

        Args:
            symbol: 股票代码 (如 600000, 000001, 300377)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            adjust: 复权类型 (qfq=前复权, hfq=后复权, none=不复权)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        adj_map = {"qfq": "2", "hfq": "1", "none": "3"}
        adj = adj_map.get(adjust, "3")

        normalized_code = _normalize_code(symbol)
        fields = "date,open,high,low,close,volume,amount"
        adj_map = {"qfq": "2", "hfq": "1", "none": "3"}
        adj = adj_map.get(adjust, "3")
        rs = bs.query_history_k_data_plus(normalized_code, fields, start_date, end_date, "d", adj)
        df = _rs_to_df(rs, "获取K线数据失败")

        if not df.empty:
            df = df.rename(
                columns={
                    "date": "trade_date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                    "amount": "amount",
                }
            )
            df["trade_date"] = pd.to_datetime(df["trade_date"])

        return df

    @with_baostock_login
    def get_minute_kline(
        self, symbol: str, period: str = "5", start_date: str = None, end_date: str = None
    ) -> pd.DataFrame:
        """
        获取分钟K线数据

        Args:
            symbol: 股票代码
            period: 分钟周期 (1, 5, 15, 30, 60)
            start_date: 开始日期
            end_date: 结束日期
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        period_map = {"1": "1", "5": "5", "15": "15", "30": "30", "60": "60"}
        frequency = period_map.get(period, "5")
        normalized_code = _normalize_code(symbol)
        fields = "date,time,open,high,low,close,volume"
        rs = bs.query_history_k_data_plus(normalized_code, fields, start_date, end_date, frequency, "3")
        df = _rs_to_df(rs, "获取分钟K线数据失败")

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["time"] = pd.to_datetime(df["time"])

        return df

    @with_baostock_login
    def get_stock_basic(self, code: str = None) -> pd.DataFrame:
        """
        获取股票基本信息

        Args:
            code: 股票代码 (可选)
        """
        if code:
            code = _normalize_code(code)
        rs = bs.query_stock_basic(code=code)
        return _rs_to_df(rs, "获取股票基本信息失败")

    @with_baostock_login
    def get_trade_dates(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)
        return _rs_to_df(rs, "获取交易日历失败")

    @with_baostock_login
    def get_financial_indicator(self, code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取财务指标

        Args:
            code: 股票代码
            year: 报表年份
            quarter: 报表季度 (1, 2, 3, 4)
        """
        normalized_code = _normalize_code(code)
        if year is None:
            year = datetime.now().year - 1
        if quarter is None:
            quarter = 4

        rs = bs.query_financial_indicator(normalized_code, str(year), str(quarter))
        return _rs_to_df(rs, "获取财务指标失败")

    @with_baostock_login
    def get_dupont_data(self, code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取杜邦分析数据

        Args:
            code: 股票代码
            year: 报表年份
            quarter: 报表季度
        """
        normalized_code = _normalize_code(code)
        if year is None:
            year = datetime.now().year - 1
        if quarter is None:
            quarter = 4

        rs = bs.query_dupont_data(normalized_code, str(year), str(quarter))
        return _rs_to_df(rs, "获取杜邦数据失败")

    @with_baostock_login
    def get_balance_sheet(self, code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取资产负债表

        Args:
            code: 股票代码
            year: 报表年份
            quarter: 报表季度
        """
        normalized_code = _normalize_code(code)
        if year is None:
            year = datetime.now().year - 1
        if quarter is None:
            quarter = 4

        rs = bs.query_balance_sheet(normalized_code, str(year), str(quarter))
        return _rs_to_df(rs, "获取资产负债表失败")

    @with_baostock_login
    def get_income_statement(self, code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取利润表

        Args:
            code: 股票代码
            year: 报表年份
            quarter: 报表季度
        """
        normalized_code = _normalize_code(code)
        if year is None:
            year = datetime.now().year - 1
        if quarter is None:
            quarter = 4

        rs = bs.query_income_statement(normalized_code, str(year), str(quarter))
        return _rs_to_df(rs, "获取利润表失败")

    @with_baostock_login
    def get_cash_flow(self, code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取现金流量表

        Args:
            code: 股票代码
            year: 报表年份
            quarter: 报表季度
        """
        normalized_code = _normalize_code(code)
        if year is None:
            year = datetime.now().year - 1
        if quarter is None:
            quarter = 4

        rs = bs.query_cash_flow_statement(normalized_code, str(year), str(quarter))
        return _rs_to_df(rs, "获取现金流量表失败")

    @with_baostock_login
    def get_index_components(self, index_code: str) -> pd.DataFrame:
        """
        获取指数成分股

        Args:
            index_code: 指数代码 (sh.000001, sz.399001, sz.399300, sh.000905)
        """
        index_map = {
            "000001": "sh.000001",
            "399001": "sz.399001",
            "399300": "sz.399300",
            "000905": "sh.000905",
            "sz399300": "sz.399300",
            "sh000001": "sh.000001",
        }
        bs_code = index_map.get(index_code, index_code)
        if not bs_code.startswith("sh.") and not bs_code.startswith("sz."):
            bs_code = "sh." + bs_code

        if bs_code == "sz.399300":
            rs = bs.query_hs300_stocks()
        elif bs_code == "sh.000001":
            rs = bs.query_sz50_stocks()
        elif bs_code == "sh.000905":
            rs = bs.query_zz500_stocks()
        else:
            rs = bs.query_zz500_stocks()

        return _rs_to_df(rs, "获取指数成分股失败")

    @with_baostock_login
    def get_deposit_rate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取存款利率
        """
        if start_date is None:
            start_date = "1990-01-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_deposit_rate_data(start_date, end_date)
        return _rs_to_df(rs, "获取存款利率失败")

    @with_baostock_login
    def get_loan_rate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取贷款利率
        """
        if start_date is None:
            start_date = "1990-01-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_loan_rate_data(start_date, end_date)
        return _rs_to_df(rs, "获取贷款利率失败")

    @with_baostock_login
    def get_reserve_ratio(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取存款准备金率
        """
        if start_date is None:
            start_date = "1990-01-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_required_reserve_ratio_data(start_date, end_date)
        return _rs_to_df(rs, "获取存款准备金率失败")

    @with_baostock_login
    def get_money_supply_monthly(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取货币供应量(月度)
        """
        if start_date is None:
            start_date = "2023-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m")

        rs = bs.query_money_supply_data_month(start_date, end_date)
        return _rs_to_df(rs, "获取货币供应量(月度)失败")

    @with_baostock_login
    def get_industry_classified(self) -> pd.DataFrame:
        """
        获取行业分类
        """
        rs = bs.query_stock_industry()
        return _rs_to_df(rs, "获取行业分类失败")


# 便捷函数
def create_baostock_adapter() -> BaoStockAdapter:
    """创建 baostock 适配器实例"""
    return BaoStockAdapter()
