"""
# 功能：财务报告数据适配器
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理财务报告数据的获取和处理
"""

import pandas as pd
from typing import Dict, List
from loguru import logger

from .base_financial_adapter import BaseFinancialAdapter


class FinancialReportAdapter(BaseFinancialAdapter):
    """
    财务报告数据适配器

    专门处理财务报告数据，包括资产负债表、利润表、现金流量表等
    """

    def __init__(self):
        super().__init__()
        self._akshare_available = False
        self._tushare_available = False

    def _check_dependency_availability(self) -> None:
        """检查依赖库的可用性"""
        try:
            import akshare as ak

            self._akshare_available = True
            logger.info("akshare 库可用")
        except ImportError:
            logger.warning("akshare 库不可用")

        try:
            import tushare as ts

            self._tushare_available = True
            logger.info("tushare 库可用")
        except ImportError:
            logger.warning("tushare 库不可用")

    def get_financial_report(
        self, symbol: str, report_type: str = "利润表", period: str = "年报"
    ) -> Dict:
        """获取财务报告"""
        symbol = self._validate_financial_report_params(symbol, report_type, period)

        cache_key = self._get_cache_key(
            symbol, "financial_report", report_type=report_type, period=period
        )
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取财务报告: {symbol} {report_type} {period}")
            return cached_data

        # 按优先级尝试不同的数据源
        data_sources = [
            ("akshare", self._fetch_financial_report_from_akshare),
            ("tushare", self._fetch_financial_report_from_tushare),
        ]

        for source_name, fetch_func in data_sources:
            try:
                data = fetch_func(symbol, report_type, period)
                if data:
                    self._save_to_cache(cache_key, data)
                    logger.info(f"通过 {source_name} 获取财务报告成功: {symbol}")
                    return data
            except Exception as e:
                logger.warning(f"通过 {source_name} 获取财务报告失败: {e}")
                continue

        raise Exception(f"所有数据源都无法获取股票 {symbol} 的财务报告")

    def _validate_financial_report_params(
        self, symbol: str, report_type: str, period: str
    ) -> str:
        """验证财务报告参数"""
        if not symbol:
            raise ValueError("股票代码不能为空")

        if not self._validate_symbol(symbol):
            raise ValueError(f"无效的股票代码格式: {symbol}")

        # 验证报告类型
        valid_report_types = ["资产负债表", "利润表", "现金流量表", "财务指标"]
        if report_type not in valid_report_types:
            raise ValueError(
                f"无效的报告类型: {report_type}，支持的类型: {valid_report_types}"
            )

        # 验证报告期
        valid_periods = ["年报", "半年报", "季报", "中报", "一季报", "三季报"]
        if period not in valid_periods:
            raise ValueError(f"无效的报告期: {period}，支持的类型: {valid_periods}")

        return symbol

    def _fetch_financial_report_from_akshare(
        self, symbol: str, report_type: str, period: str
    ) -> Dict:
        """通过 akshare 获取财务报告"""
        if not self._akshare_available:
            raise Exception("akshare 库不可用")

        try:
            import akshare as ak

            # 映射到akshare的函数
            report_type_mapping = {
                "资产负债表": ak.stock_financial_analysis_indicator,
                "利润表": ak.stock_financial_analysis_indicator,
                "现金流量表": ak.stock_financial_analysis_indicator,
                "财务指标": ak.stock_financial_analysis_indicator,
            }

            # 映射报告期到akshare的格式
            period_mapping = {
                "年报": "year",
                "半年报": "half_year",
                "季报": "quarter",
                "中报": "half_year",
                "一季报": "quarter",
                "三季报": "quarter",
            }

            if report_type not in report_type_mapping:
                raise ValueError(f"akshare 不支持的报告类型: {report_type}")

            # 获取财务指标数据
            data = report_type_mapping[report_type](symbol=symbol)

            if data is None or data.empty:
                return {}

            # 根据报告类型提取相关数据
            result = self._extract_financial_data_by_type(data, report_type, period)

            return result

        except Exception as e:
            logger.error(f"akshare 获取财务报告失败: {e}")
            raise

    def _fetch_financial_report_from_tushare(
        self, symbol: str, report_type: str, period: str
    ) -> Dict:
        """通过 tushare 获取财务报告"""
        if not self._tushare_available:
            raise Exception("tushare 库不可用")

        try:
            import tushare as ts

            # 注意：tushare 需要token
            # 这里假设已经配置了ts.set_token()

            # 映射到tushare的API
            report_type_mapping = {
                "资产负债表": "balancesheet",
                "利润表": "income",
                "现金流量表": "cashflow",
                "财务指标": "fina_indicator",
            }

            if report_type not in report_type_mapping:
                raise ValueError(f"tushare 不支持的报告类型: {report_type}")

            # 获取财务数据
            pro = ts.pro_api()
            data = pro.income(
                ts_code=symbol, period_type=period_mapping.get(period, "annual")
            )

            if data is None or data.empty:
                return {}

            # 转换为字典格式
            result = self._convert_tushare_data_to_dict(data, report_type)

            return result

        except Exception as e:
            logger.error(f"tushare 获取财务报告失败: {e}")
            raise

    def _extract_financial_data_by_type(
        self, data: pd.DataFrame, report_type: str, period: str
    ) -> Dict:
        """根据报告类型提取相关数据"""
        try:
            if data.empty:
                return {}

            # 获取最新一期的数据
            latest_data = data.iloc[-1] if len(data) > 0 else data.iloc[0]

            result = {
                "symbol": latest_data.get("代码", ""),
                "report_date": latest_data.get("报告日期", ""),
                "report_type": report_type,
                "period": period,
                "data": {},
            }

            # 根据报告类型提取不同的数据
            if report_type == "利润表":
                result["data"] = {
                    "营业收入": latest_data.get("营业收入", 0),
                    "营业成本": latest_data.get("营业成本", 0),
                    "净利润": latest_data.get("净利润", 0),
                    "归母净利润": latest_data.get("归母净利润", 0),
                    "毛利率": latest_data.get("毛利率", 0),
                    "净利率": latest_data.get("净利率", 0),
                    "ROE": latest_data.get("净资产收益率", 0),
                    "ROA": latest_data.get("总资产收益率", 0),
                }
            elif report_type == "资产负债表":
                result["data"] = {
                    "总资产": latest_data.get("总资产", 0),
                    "总负债": latest_data.get("总负债", 0),
                    "净资产": latest_data.get("净资产", 0),
                    "流动资产": latest_data.get("流动资产", 0),
                    "流动负债": latest_data.get("流动负债", 0),
                    "资产负债率": latest_data.get("资产负债率", 0),
                }
            elif report_type == "现金流量表":
                result["data"] = {
                    "经营活动现金流": latest_data.get("经营活动现金流净额", 0),
                    "投资活动现金流": latest_data.get("投资活动现金流净额", 0),
                    "筹资活动现金流": latest_data.get("筹资活动现金流净额", 0),
                    "现金净增加额": latest_data.get("现金净增加额", 0),
                }
            elif report_type == "财务指标":
                result["data"] = {
                    "每股收益": latest_data.get("每股收益", 0),
                    "每股净资产": latest_data.get("每股净资产", 0),
                    "市盈率": latest_data.get("市盈率", 0),
                    "市净率": latest_data.get("市净率", 0),
                    "股息率": latest_data.get("股息率", 0),
                    "净利润增长率": latest_data.get("净利润增长率", 0),
                }

            return result

        except Exception as e:
            logger.error(f"提取财务数据失败: {e}")
            return {}

    def _convert_tushare_data_to_dict(
        self, data: pd.DataFrame, report_type: str
    ) -> Dict:
        """将tushare数据转换为字典格式"""
        try:
            if data.empty:
                return {}

            latest_data = data.iloc[-1] if len(data) > 0 else data.iloc[0]

            result = {
                "symbol": latest_data.get("ts_code", ""),
                "report_date": latest_data.get("end_date", ""),
                "report_type": report_type,
                "data": {},
            }

            # 将所有列数据添加到data字典
            for col in data.columns:
                if col not in ["ts_code", "end_date", "ann_date", "f_ann_date"]:
                    result["data"][col] = latest_data.get(col, 0)

            return result

        except Exception as e:
            logger.error(f"转换tushare数据失败: {e}")
            return {}

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取股票日线数据 - 此适配器不实现日线数据功能"""
        raise NotImplementedError("FinancialReportAdapter 不支持日线数据获取")

    def get_financial_indicators(self, symbol: str, period: str = "年报") -> List[Dict]:
        """获取财务指标"""
        try:
            return [self.get_financial_report(symbol, "财务指标", period)]
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return []

    def get_balance_sheet(self, symbol: str, period: str = "年报") -> Dict:
        """获取资产负债表"""
        return self.get_financial_report(symbol, "资产负债表", period)

    def get_income_statement(self, symbol: str, period: str = "年报") -> Dict:
        """获取利润表"""
        return self.get_financial_report(symbol, "利润表", period)

    def get_cash_flow_statement(self, symbol: str, period: str = "年报") -> Dict:
        """获取现金流量表"""
        return self.get_financial_report(symbol, "现金流量表", period)
