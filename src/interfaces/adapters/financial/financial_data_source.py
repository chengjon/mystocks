"""
# 功能：财务数据源 - 重构版本
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：3.0.0 (重构版本)
# 说明：财务数据的统一入口，使用模块化设计
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime
from loguru import logger

from src.interfaces.data_source import IDataSource
from src.utils import symbol_utils
from .stock_daily_adapter import StockDailyAdapter
from .financial_report_adapter import FinancialReportAdapter


class FinancialDataSource(IDataSource):
    """
    财务数据适配器 - 重构版本

    数据分类: DataClassification.FUNDAMENTAL_METRICS (第2类-参考数据-基本面数据)
    存储目标: MySQL/MariaDB
    数据特性: 低频、结构化、关系型

    重构后特性:
    - 模块化设计：股票日线和财务报告分离
    - 专门的适配器：每个适配器专注特定数据类型
    - 统一接口：保持向后兼容性
    - 更好的错误处理和日志记录
    """


def __init__(self):
    """初始化财务数据适配器"""
    super().__init__()

    # 初始化专门的适配器
    self._stock_daily_adapter = StockDailyAdapter()
    self._financial_report_adapter = FinancialReportAdapter()

    # 检查依赖库可用性
    self._check_dependency_availability()

    # 数据源可用性标志
    self._stock_daily_available = False
    self._financial_reports_available = False


def _check_dependency_availability(self) -> None:
    """检查依赖库的可用性"""
    try:
        self._stock_daily_adapter._check_dependency_availability()
        self._financial_report_adapter._check_dependency_availability()

        self._stock_daily_available = True
        self._financial_reports_available = True

        logger.info("财务数据源依赖检查完成")
    except Exception as e:
        logger.error("财务数据源依赖检查失败: %s", e)


def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取股票日线数据

    Args:
        symbol: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        pd.DataFrame: 日线数据
    """
    if not self._stock_daily_available:
        raise Exception("股票日线数据源不可用")

    logger.info("获取股票日线数据: %s %s ~ %s", symbol, start_date, end_date)

    try:
        data = self._stock_daily_adapter.get_stock_daily(symbol, start_date, end_date)
        logger.info("成功获取股票日线数据: %s 条记录", len(data))
        return data
    except Exception as e:
        logger.error("获取股票日线数据失败: %s", e)
        raise


def get_financial_report(self, symbol: str, report_type: str = "利润表", period: str = "年报") -> Dict:
    """
    获取财务报告

    Args:
        symbol: 股票代码
        report_type: 报告类型 ('资产负债表', '利润表', '现金流量表', '财务指标')
        period: 报告期 ('年报', '半年报', '季报', '中报', '一季报', '三季报')

    Returns:
        Dict: 财务报告数据
    """
    if not self._financial_reports_available:
        raise Exception("财务报告数据源不可用")

    logger.info("获取财务报告: %s %s %s", symbol, report_type, period)

    try:
        data = self._financial_report_adapter.get_financial_report(symbol, report_type, period)
        logger.info("成功获取财务报告: %s", symbol)
        return data
    except Exception as e:
        logger.error("获取财务报告失败: %s", e)
        raise


def get_financial_indicators(self, symbol: str, period: str = "年报") -> List[Dict]:
    """
    获取财务指标

    Args:
        symbol: 股票代码
        period: 报告期

    Returns:
        List[Dict]: 财务指标列表
    """
    try:
        indicators = self._financial_report_adapter.get_financial_indicators(symbol, period)
        logger.info("成功获取财务指标: %s", symbol)
        return indicators
    except Exception as e:
        logger.error("获取财务指标失败: %s", e)
        return []


def get_balance_sheet(self, symbol: str, period: str = "年报") -> Dict:
    """
    获取资产负债表

    Args:
        symbol: 股票代码
        period: 报告期

    Returns:
        Dict: 资产负债表数据
    """
    try:
        balance_sheet = self._financial_report_adapter.get_balance_sheet(symbol, period)
        logger.info("成功获取资产负债表: %s", symbol)
        return balance_sheet
    except Exception as e:
        logger.error("获取资产负债表失败: %s", e)
        return {}


def get_income_statement(self, symbol: str, period: str = "年报") -> Dict:
    """
    获取利润表

    Args:
        symbol: 股票代码
        period: 报告期

    Returns:
        Dict: 利润表数据
    """
    try:
        income_statement = self._financial_report_adapter.get_income_statement(symbol, period)
        logger.info("成功获取利润表: %s", symbol)
        return income_statement
    except Exception as e:
        logger.error("获取利润表失败: %s", e)
        return {}


def get_cash_flow_statement(self, symbol: str, period: str = "年报") -> Dict:
    """
    获取现金流量表

    Args:
        symbol: 股票代码
        period: 报告期

    Returns:
        Dict: 现金流量表数据
    """
    try:
        cash_flow = self._financial_report_adapter.get_cash_flow_statement(symbol, period)
        logger.info("成功获取现金流量表: %s", symbol)
        return cash_flow
    except Exception as e:
        logger.error("获取现金流量表失败: %s", e)
        return {}


def get_comprehensive_financial_data(self, symbol: str, period: str = "年报") -> Dict:
    """
    获取综合财务数据（包含所有报表类型）

    Args:
        symbol: 股票代码
        period: 报告期

    Returns:
        Dict: 综合财务数据
    """
    try:
        logger.info("获取综合财务数据: %s %s", symbol, period)

        comprehensive_data = {
            "symbol": symbol,
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "balance_sheet": self.get_balance_sheet(symbol, period),
            "income_statement": self.get_income_statement(symbol, period),
            "cash_flow_statement": self.get_cash_flow_statement(symbol, period),
            "financial_indicators": self.get_financial_indicators(symbol, period),
        }

        logger.info("成功获取综合财务数据: %s", symbol)
        return comprehensive_data

    except Exception as e:
        logger.error("获取综合财务数据失败: %s", e)
        return {}


def validate_data_integrity(self, data: Dict) -> bool:
    """
    验证数据完整性

    Args:
        data: 待验证的数据

    Returns:
        bool: 验证结果
    """
    try:
        if not data or not isinstance(data, dict):
            return False

        # 基本字段检查
        if "symbol" not in data:
            return False

        if not self._validate_symbol(data["symbol"]):
            return False

        return True

    except Exception as e:
        logger.error("数据完整性验证失败: %s", e)
        return False


def _validate_symbol(self, symbol: str) -> bool:
    """验证股票代码格式"""
    return symbol_utils.is_valid_stock_code(symbol)


def get_data_source_status(self) -> Dict:
    """
    获取数据源状态

    Returns:
        Dict: 数据源状态信息
    """
    try:
        status = {
            "financial_data_source": {
                "available": True,
                "last_check": datetime.now().isoformat(),
            },
            "stock_daily_adapter": {
                "available": self._stock_daily_available,
            },
            "financial_report_adapter": {
                "available": self._financial_reports_available,
            },
            "dependencies": {
                "efinance": False,  # TODO: 实际检查
                "akshare": False,
                "tushare": False,
                "easyquotation": False,
            },
        }

        # 检查各个依赖库的实际可用性（使用 importlib 规范检查）
        import importlib.util

        # 检查 efinance
        if importlib.util.find_spec("efinance"):
            status["dependencies"]["efinance"] = True

        # 检查 akshare
        if importlib.util.find_spec("akshare"):
            status["dependencies"]["akshare"] = True

        # 检查 tushare
        if importlib.util.find_spec("tushare"):
            status["dependencies"]["tushare"] = True

        # 检查 easyquotation
        if importlib.util.find_spec("easyquotation"):
            status["dependencies"]["easyquotation"] = True

        return status

    except Exception as e:
        logger.error("获取数据源状态失败: %s", e)
        return {"error": str(e)}
