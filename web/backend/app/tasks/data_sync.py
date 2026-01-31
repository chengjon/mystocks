"""
数据同步任务
实现各类数据同步功能
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from src.adapters.akshare_adapter import AkshareDataSource
from src.adapters.baostock_adapter import BaostockDataSource
from src.adapters.financial_adapter import FinancialDataSource
from src.core.data_classification import DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

logger = logging.getLogger(__name__)

# 初始化数据管理器和数据源
_unified_manager = None
_data_sources = {}


def _get_unified_manager() -> MyStocksUnifiedManager:
    """获取统一数据管理器实例（单例模式）"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = MyStocksUnifiedManager(enable_monitoring=True)
    return _unified_manager


def _get_data_source(source_name: str):
    """获取数据源实例（单例模式）"""
    global _data_sources
    if source_name not in _data_sources:
        if source_name == "akshare":
            _data_sources[source_name] = AkshareDataSource()
        elif source_name == "baostock":
            _data_sources[source_name] = BaostockDataSource()
        elif source_name == "financial":
            _data_sources[source_name] = FinancialDataSource()
        else:
            raise ValueError(f"Unknown data source: {source_name}")
    return _data_sources[source_name]


def sync_daily_stock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    同步每日股票数据

    Args:
        params: 任务参数
            - data_source: 数据源 (akshare, baostock等)
            - include_basic: 是否包含基础数据
            - include_kline: 是否包含K线数据
            - symbols: 股票代码列表（可选，默认同步所有A股）
            - start_date: 开始日期（可选，默认最近30天）
            - end_date: 结束日期（可选，默认今天）

    Returns:
        执行结果字典
    """
    logger.info("Starting daily stock data sync with params: %(params)s"")

    try:
        data_source_name = params.get("data_source", "akshare")
        include_basic = params.get("include_basic", True)
        include_kline = params.get("include_kline", True)
        symbols = params.get("symbols", [])

        # 日期范围：默认最近30天
        end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        start_date = params.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        # 获取数据源和管理器
        data_source = _get_data_source(data_source_name)
        manager = _get_unified_manager()

        result = {
            "status": "success",
            "data_source": data_source_name,
            "sync_time": datetime.now().isoformat(),
            "records_synced": 0,
            "errors": [],
        }

        # 如果未指定股票代码，获取所有A股列表
        if not symbols:
            logger.info("Fetching all A-share stock list...")
            try:
                stock_list_df = data_source.get_stock_list()
                symbols = stock_list_df["symbol"].tolist()[:100]  # 限制前100只股票避免超时
                logger.info("Found {len(symbols)} stocks to sync"")
            except Exception as e:
                logger.error("Failed to fetch stock list: %(e)s"")
                result["errors"].append(f"Stock list fetch error: {str(e)}")
                symbols = []

        # 同步基础数据
        if include_basic and symbols:
            logger.info("Syncing basic stock info for {len(symbols)} stocks..."")
            try:
                for symbol in symbols:
                    try:
                        # 获取股票基本信息
                        basic_info = data_source.get_stock_info(symbol)
                        if not basic_info.empty:
                            # 保存到参考数据分类 → PostgreSQL
                            manager.save_data_by_classification(
                                DataClassification.REFERENCE_DATA,
                                basic_info,
                                table_name="stock_basic_info",
                            )
                            result["records_synced"] += len(basic_info)
                    except Exception as e:
                        logger.warning("Failed to sync basic info for %(symbol)s: %(e)s"")
                        result["errors"].append(f"{symbol} basic: {str(e)}")
            except Exception as e:
                logger.error("Basic data sync error: %(e)s"")
                result["errors"].append(f"Basic sync error: {str(e)}")

        # 同步K线数据
        if include_kline and symbols:
            logger.info("Syncing daily K-line data for {len(symbols)} stocks..."")
            try:
                for symbol in symbols:
                    try:
                        # 获取日线数据
                        kline_df = data_source.get_stock_daily(symbol, start_date, end_date)
                        if not kline_df.empty:
                            # 保存到日线数据分类 → PostgreSQL (TimescaleDB hypertable)
                            manager.save_data_by_classification(
                                DataClassification.DAILY_KLINE,
                                kline_df,
                                table_name="daily_kline",
                            )
                            result["records_synced"] += len(kline_df)
                    except Exception as e:
                        logger.warning("Failed to sync K-line for %(symbol)s: %(e)s"")
                        result["errors"].append(f"{symbol} kline: {str(e)}")
            except Exception as e:
                logger.error("K-line data sync error: %(e)s"")
                result["errors"].append(f"K-line sync error: {str(e)}")

        logger.info("Daily stock data sync completed: {result['records_synced']} records"")

        # 如果有错误但成功同步了部分数据，标记为partial_success
        if result["errors"] and result["records_synced"] > 0:
            result["status"] = "partial_success"
        elif result["errors"] and result["records_synced"] == 0:
            result["status"] = "failed"

        return result

    except Exception as e:
        logger.error("Failed to sync daily stock data: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "sync_time": datetime.now().isoformat(),
            "records_synced": 0,
        }


def sync_basic_stock_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    同步股票基础信息（股票列表、名称、代码等）

    Args:
        params: 任务参数
            - data_source: 数据源 (akshare, baostock等)
            - include_delisted: 是否包含退市股票
            - market: 市场类型 (可选: 'A', 'HK', 'US'，默认'A')

    Returns:
        执行结果字典
    """
    logger.info("Starting basic stock info sync with params: %(params)s"")

    try:
        data_source_name = params.get("data_source", "akshare")
        include_delisted = params.get("include_delisted", False)
        market = params.get("market", "A")

        # 获取数据源和管理器
        data_source = _get_data_source(data_source_name)
        manager = _get_unified_manager()

        result = {
            "status": "success",
            "data_source": data_source_name,
            "sync_time": datetime.now().isoformat(),
            "stocks_synced": 0,
            "include_delisted": include_delisted,
            "market": market,
            "errors": [],
        }

        # 获取股票列表
        logger.info("Fetching %(market)s-share stock list..."")
        try:
            stock_list_df = data_source.get_stock_list()

            if not stock_list_df.empty:
                # 如果不包含退市股票，过滤掉退市的股票
                if not include_delisted and "status" in stock_list_df.columns:
                    stock_list_df = stock_list_df[stock_list_df["status"].str.contains("正常|上市", na=False)]

                # 保存股票列表到参考数据分类 → PostgreSQL
                manager.save_data_by_classification(
                    DataClassification.REFERENCE_DATA,
                    stock_list_df,
                    table_name="stock_list",
                )

                result["stocks_synced"] = len(stock_list_df)
                logger.info("Synced {result['stocks_synced']} stock records"")

                # 同步每只股票的详细信息（批量操作，限制数量避免超时）
                symbols_to_sync = stock_list_df["symbol"].tolist()[:50]  # 限制50只
                logger.info("Syncing detailed info for {len(symbols_to_sync)} stocks..."")

                for symbol in symbols_to_sync:
                    try:
                        stock_info = data_source.get_stock_info(symbol)
                        if not stock_info.empty:
                            manager.save_data_by_classification(
                                DataClassification.REFERENCE_DATA,
                                stock_info,
                                table_name="stock_info_detail",
                            )
                    except Exception as e:
                        logger.warning("Failed to sync detailed info for %(symbol)s: %(e)s"")
                        result["errors"].append(f"{symbol}: {str(e)}")

            else:
                logger.warning("Stock list is empty")
                result["status"] = "failed"
                result["errors"].append("Empty stock list returned")

        except Exception as e:
            logger.error("Failed to fetch stock list: {e}", exc_info=True)
            result["status"] = "failed"
            result["errors"].append(f"Stock list error: {str(e)}")

        logger.info("Basic stock info sync completed: %(result)s"")

        # 如果有错误但成功同步了部分数据，标记为partial_success
        if result["errors"] and result["stocks_synced"] > 0:
            result["status"] = "partial_success"

        return result

    except Exception as e:
        logger.error("Failed to sync basic stock info: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "sync_time": datetime.now().isoformat(),
            "stocks_synced": 0,
        }


def sync_financial_statements(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    同步财务报表数据（利润表、资产负债表、现金流量表等）

    Args:
        params: 任务参数
            - data_source: 数据源 (默认使用 financial 适配器)
            - report_types: 报表类型列表 ['income', 'balance', 'cashflow']
            - symbols: 股票代码列表（可选）
            - report_date: 报告期（可选，格式：YYYY-MM-DD或YYYYMMDD）

    Returns:
        执行结果字典
    """
    logger.info("Starting financial statements sync with params: %(params)s"")

    try:
        data_source_name = params.get("data_source", "financial")
        report_types = params.get("report_types", ["income", "balance", "cashflow"])
        symbols = params.get("symbols", [])
        report_date = params.get("report_date", None)

        # 获取数据源和管理器
        data_source = _get_data_source(data_source_name)
        manager = _get_unified_manager()

        result = {
            "status": "success",
            "data_source": data_source_name,
            "sync_time": datetime.now().isoformat(),
            "report_types": report_types,
            "records_synced": 0,
            "errors": [],
        }

        # 如果未指定股票代码，获取A股列表（限制数量）
        if not symbols:
            logger.info("Fetching stock list for financial data sync...")
            try:
                # 使用akshare获取股票列表
                akshare_source = _get_data_source("akshare")
                stock_list_df = akshare_source.get_stock_list()
                symbols = stock_list_df["symbol"].tolist()[:20]  # 限制20只避免超时
                logger.info("Found {len(symbols)} stocks for financial sync"")
            except Exception as e:
                logger.error("Failed to fetch stock list: %(e)s"")
                result["errors"].append(f"Stock list error: {str(e)}")
                symbols = []

        # 同步各类财务报表
        for report_type in report_types:
            logger.info("Syncing %(report_type)s statements for {len(symbols)} stocks..."")

            for symbol in symbols:
                try:
                    financial_data = None

                    # 根据报表类型调用不同的方法
                    if report_type == "income":
                        # 利润表
                        financial_data = data_source.get_income_statement(symbol, report_date)
                        table_name = "income_statement"
                    elif report_type == "balance":
                        # 资产负债表
                        financial_data = data_source.get_balance_sheet(symbol, report_date)
                        table_name = "balance_sheet"
                    elif report_type == "cashflow":
                        # 现金流量表
                        financial_data = data_source.get_cashflow_statement(symbol, report_date)
                        table_name = "cashflow_statement"
                    else:
                        logger.warning("Unknown report type: %(report_type)s"")
                        result["errors"].append(f"Unknown report type: {report_type}")
                        continue

                    # 保存财务数据到派生数据分类 → PostgreSQL
                    if financial_data is not None and not financial_data.empty:
                        manager.save_data_by_classification(
                            DataClassification.DERIVED_DATA,
                            financial_data,
                            table_name=table_name,
                        )
                        result["records_synced"] += len(financial_data)

                except AttributeError as e:
                    # 如果方法不存在，记录警告
                    logger.warning("Financial adapter missing method for %(report_type)s: %(e)s"")
                    result["errors"].append(f"{symbol} {report_type}: method not implemented")
                except Exception as e:
                    logger.warning("Failed to sync %(report_type)s for %(symbol)s: %(e)s"")
                    result["errors"].append(f"{symbol} {report_type}: {str(e)}")

        logger.info("Financial statements sync completed: {result['records_synced']} records"")

        # 如果有错误但成功同步了部分数据，标记为partial_success
        if result["errors"] and result["records_synced"] > 0:
            result["status"] = "partial_success"
        elif result["errors"] and result["records_synced"] == 0:
            result["status"] = "failed"

        return result

    except Exception as e:
        logger.error("Failed to sync financial statements: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "sync_time": datetime.now().isoformat(),
            "records_synced": 0,
        }
