import baostock as bs
import pandas as pd
import logging
from datetime import datetime, timedelta
import sys
import os
from functools import wraps
import contextlib

# 装饰器移到类外部


def with_login(func):
    """
    装饰器：自动登录、登出，并在登录失败时返回空DataFrame。
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        lg = self._login()
        if hasattr(lg, "error_code") and lg.error_code != "0":
            return pd.DataFrame()
        try:
            return func(self, *args, **kwargs)
        finally:
            self._logout()

    return wrapper


class BaoStockData:
    def __init__(self, log_level=logging.INFO):
        # 初始化日志
        self.logger = logging.getLogger("BaoStockData")
        self.logger.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 控制台输出
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # 初始化baostock
        self._login()

    def __del__(self):
        # 确保程序结束时登出
        self._logout()

    def _login(self):
        """统一登录方法，返回登录对象"""
        with open(os.devnull, "w") as fnull, contextlib.redirect_stdout(fnull):
            lg = bs.login()
        if lg.error_code != "0":
            self.logger.error(f"Baostock登录失败: {lg.error_msg}")
        return lg

    def _logout(self):
        """统一登出方法"""
        with open(os.devnull, "w") as fnull, contextlib.redirect_stdout(fnull):
            bs.logout()

    def _rs_to_df(self, rs, error_msg="查询失败"):
        """
        将baostock的rs对象转换为DataFrame，并处理错误
        :param rs: baostock返回的rs对象
        :param error_msg: 错误时的日志信息
        :return: pandas.DataFrame
        """
        if rs.error_code != "0":
            self.logger.error(f"{error_msg}: {rs.error_msg}")
            return pd.DataFrame()
        data_list = []
        while rs.error_code == "0" and rs.next():
            data_list.append(rs.get_row_data())
        return pd.DataFrame(data_list, columns=rs.fields)

    @with_login
    def query_trade_dates(self, start_date=None, end_date=None):
        """
        交易日查询
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认为今天-7天
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认为当前日期
        :return: pandas.DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询交易日失败")

    @with_login
    def query_all_stock(self, day=None):
        """
        证券代码查询
        :param day: 需要查询的交易日期，格式YYYY-MM-DD，为空时默认当前日期
        :return: pandas.DataFrame
        """
        if day is None:
            day = datetime.now().strftime("%Y-%m-%d")
        rs = bs.query_all_stock(day=day)
        return self._rs_to_df(rs, "查询证券代码失败")

    @with_login
    def query_stock_basic(self, code=None, code_name=None):
        """
        证券基本资料
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param code_name: 股票名称，支持模糊查询
        :return: pandas.DataFrame
        示例: bao.query_stock_basic('300377')
        """
        if code is not None:
            code = self._normalize_code(code)
        rs = bs.query_stock_basic(code=code, code_name=code_name)
        return self._rs_to_df(rs, "查询证券基本资料失败")

    def _normalize_code(self, code):
        """
        统一股票代码格式为 sh.600000、sz.000001
        支持输入 sh.600000、sh600000、600000、SZ000001、000001 等
        """
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
            self.logger.error(f"无效的股票代码格式: {code}")
            return code  # 返回原始，baostock会报错

    @with_login
    def query_history_k_data_plus(
        self, symbol, timeframe, adj=None, start_date=None, end_date=None
    ):
        """
        获取K线数据
        :param symbol: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param timeframe: K线周期，支持"5m","15m","30m","1h","1d","1w","1M"
        :param adj: 复权类型，默认"3"不复权；"2"前复权；"1"后复权
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时取今天-7天
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时取最近一个交易日
        :return: pandas.DataFrame
        示例: bao.query_history_k_data_plus('300377', '1d', start_date='2024-01-01', end_date='2024-06-30')
        """
        valid_timeframes = {"5m", "15m", "30m", "1h", "1d", "1w", "1M"}
        if timeframe not in valid_timeframes:
            self.logger.error(
                f"无效的时间周期: {timeframe}，必须为 {valid_timeframes} 之一"
            )
            return pd.DataFrame()
        frequency_map = {
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "1d": "d",
            "1w": "w",
            "1M": "m",
        }
        frequency = frequency_map[timeframe]
        if timeframe in {"5m", "15m", "30m", "1h"}:
            fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"
        elif timeframe == "1d":
            fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
        else:
            fields = (
                "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
            )
        stock_name = self._normalize_code(symbol)
        if not (stock_name.startswith("sh.") or stock_name.startswith("sz.")):
            return pd.DataFrame()
        adjust_flag = adj or "3"
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        rs = bs.query_history_k_data_plus(
            code=stock_name,
            fields=fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjust_flag,
        )
        result = self._rs_to_df(rs, "查询K线数据失败")
        if result.empty:
            return result
        if timeframe in {"5m", "15m", "30m", "1h"}:
            result = result.drop(["date", "code"], axis=1)
        else:
            result = result.drop("code", axis=1)
        return result

    def query_dividend_data(self, code, year, yearType):
        """
        查询除权除息信息
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 年份，如：2017
        :param yearType: 年份类别，"report":预案公告年份，"operate":除权除息年份
        :return: pandas.DataFrame
        示例: bao.query_dividend_data('300377', 2023, 'operate')
        """
        code = self._normalize_code(code)
        rs = bs.query_dividend_data(code=code, year=year, yearType=yearType)
        return self._rs_to_df(rs, "查询除权除息信息失败")

    def query_adjust_factor(self, code, start_date=None, end_date=None):
        """
        查询复权因子信息
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认为今天-7天
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认当前日期
        :return: pandas.DataFrame
        示例: bao.query_adjust_factor('300377', start_date='2024-01-01', end_date='2024-06-30')
        """
        code = self._normalize_code(code)
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_adjust_factor(code=code, start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询复权因子失败")

    def query_profit_data(self, code, year=None, quarter=None):
        """
        季频盈利能力
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_profit_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频盈利能力失败")

    def query_operation_data(self, code, year=None, quarter=None):
        """
        季频营运能力
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_operation_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_operation_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频营运能力失败")

    def query_growth_data(self, code, year=None, quarter=None):
        """
        季频成长能力
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_growth_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频成长能力失败")

    def query_balance_data(self, code, year=None, quarter=None):
        """
        季频偿债能力
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_balance_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_balance_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频偿债能力失败")

    def query_cash_flow_data(self, code, year=None, quarter=None):
        """
        季频现金流量
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_cash_flow_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频现金流量失败")

    def query_dupont_data(self, code, year=None, quarter=None):
        """
        季频杜邦指数
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param year: 统计年份，为空时默认当前年
        :param quarter: 统计季度，可为1,2,3,4，为空时默认当前季度
        :return: pandas.DataFrame
        示例: bao.query_dupont_data('300377', year=2023, quarter=2)
        """
        code = self._normalize_code(code)
        if year is None:
            year = datetime.now().year

        if quarter is None:
            current_month = datetime.now().month
            quarter = (current_month - 1) // 3 + 1

        rs = bs.query_dupont_data(code=code, year=year, quarter=quarter)
        return self._rs_to_df(rs, "查询季频杜邦指数失败")

    def query_performance_express_report(self, code, start_date, end_date):
        """
        季频公司业绩快报
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param start_date: 开始日期，格式YYYY-MM-DD
        :param end_date: 结束日期，格式YYYY-MM-DD
        :return: pandas.DataFrame
        示例: bao.query_performance_express_report('300377', start_date='2024-01-01', end_date='2024-06-30')
        """
        code = self._normalize_code(code)
        rs = bs.query_performance_express_report(
            code, start_date=start_date, end_date=end_date
        )
        return self._rs_to_df(rs, "查询业绩快报失败")

    def query_forcast_report(self, code, start_date, end_date):
        """
        季频公司业绩预告
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化
        :param start_date: 开始日期，格式YYYY-MM-DD
        :param end_date: 结束日期，格式YYYY-MM-DD
        :return: pandas.DataFrame
        示例: bao.query_forcast_report('300377', start_date='2024-01-01', end_date='2024-06-30')
        """
        code = self._normalize_code(code)
        rs = bs.query_forecast_report(code, start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询业绩预告失败")

    def query_deposit_rate_data(self, start_date=None, end_date=None):
        """
        存款利率
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认不限
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认不限
        :return: pandas.DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_deposit_rate_data(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询存款利率失败")

    def query_loan_rate_data(self, start_date=None, end_date=None):
        """
        贷款利率
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认不限
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认不限
        :return: pandas.DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_loan_rate_data(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询贷款利率失败")

    def query_required_reserve_ratio_data(
        self, start_date=None, end_date=None, yearType=None
    ):
        """
        存款准备金率
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认不限
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认不限
        :param yearType: 年份类别，0查询公告日期；1查询生效日期，默认0
        :return: pandas.DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        yearType = yearType or "0"
        rs = bs.query_required_reserve_ratio_data(
            start_date=start_date, end_date=end_date, yearType=yearType
        )
        return self._rs_to_df(rs, "查询存款准备金率失败")

    def query_money_supply_data_month(self, start_date=None, end_date=None):
        """
        货币供应量(月度)
        :param start_date: 开始日期，格式YYYY-MM，为空时默认不限
        :param end_date: 结束日期，格式YYYY-MM，为空时默认不限
        :return: pandas.DataFrame
        """
        if start_date is None:
            current_date = datetime.now()
            start_date = (current_date - timedelta(days=7)).strftime("%Y-%m")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m")

        rs = bs.query_money_supply_data_month(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询货币供应量(月度)失败")

    def query_money_supply_data_year(self, start_date=None, end_date=None):
        """
        货币供应量(年度)
        :param start_date: 开始日期，格式YYYY，为空时默认不限
        :param end_date: 结束日期，格式YYYY，为空时默认不限
        :return: pandas.DataFrame
        """
        if start_date is None:
            current_date = datetime.now()
            start_date = str(current_date.year - 1)
        if end_date is None:
            end_date = str(datetime.now().year)

        rs = bs.query_money_supply_data_year(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询货币供应量(年度)失败")

    def query_shibor_data(self, start_date=None, end_date=None):
        """
        银行间同业拆放利率
        :param start_date: 开始日期，格式YYYY-MM-DD，为空时默认不限
        :param end_date: 结束日期，格式YYYY-MM-DD，为空时默认不限
        :return: pandas.DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # pylint: disable=no-member
        rs = bs.query_shibor_data(start_date=start_date, end_date=end_date)
        return self._rs_to_df(rs, "查询Shibor利率失败")

    def query_stock_industry(self, code=None, date=None):
        """
        行业分类
        :param code: 股票代码，支持 sh.600000、sz.000001、600000、000001、sh600000、sz300377 等格式，自动标准化。为空时返回全量数据
        :param date: 查询日期，格式YYYY-MM-DD，为空时默认最新日期
        :return: pandas.DataFrame
        示例: bao.query_stock_industry('300377')
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if code is not None:
            code = self._normalize_code(code)
        rs = bs.query_stock_industry(code, date)
        return self._rs_to_df(rs, "查询行业分类失败")

    def query_sz50_stocks(self, date=None):
        """
        上证50成分股
        :param date: 查询日期，格式YYYY-MM-DD，为空时默认最新日期
        :return: pandas.DataFrame
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_sz50_stocks(date)
        return self._rs_to_df(rs, "查询上证50成分股失败")

    def query_hs300_stocks(self, date=None):
        """
        沪深300成分股
        :param date: 查询日期，格式YYYY-MM-DD，为空时默认最新日期
        :return: pandas.DataFrame
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_hs300_stocks(date)
        return self._rs_to_df(rs, "查询沪深300成分股失败")

    def query_zz500_stocks(self, date=None):
        """
        中证500成分股
        :param date: 查询日期，格式YYYY-MM-DD，为空时默认最新日期
        :return: pandas.DataFrame
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rs = bs.query_zz500_stocks(date)
        return self._rs_to_df(rs, "查询中证500成分股失败")


if __name__ == "__main__":
    # 示例：初始化并查询交易日
    bao = BaoStockData()
    print(bao.query_trade_dates())
