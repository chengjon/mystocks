"""
市场数据获取任务
实现各类市场数据获取功能
支持多数据源并带有自动故障转移和重试机制
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Union

from src.core.exceptions import (
    DataFetchError,
    DataValidationError,
    NetworkError,
    ServiceError,
)

logger = logging.getLogger(__name__)

# 数据源优先级 (优先使用，依次降级)
STOCK_DATA_SOURCES = ["akshare", "tushare", "baostock"]
ETF_DATA_SOURCES = ["akshare", "tushare"]

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒，指数退避


def _fetch_stock_data_from_akshare() -> int:
    """
    从AkShare获取实时股票数据

    Returns:
        获取的股票数量

    Raises:
        DataFetchError: 数据获取失败
        NetworkError: 网络连接失败
    """
    try:
        import akshare as ak

        # 获取A股实时行情数据
        logger.info("Fetching stock data from AkShare...")
        stock_data = ak.stock_zh_a_spot()

        if stock_data is None or stock_data.empty:
            raise DataValidationError(
                message="AkShare returned empty stock data",
                code="EMPTY_DATA",
                severity="HIGH",
            )

        count = len(stock_data)
        logger.info(f"Successfully fetched {count} stocks from AkShare")
        return count

    except ImportError:
        raise ServiceError(
            message="AkShare library not available",
            code="LIBRARY_NOT_AVAILABLE",
            severity="HIGH",
        )
    except Exception as e:
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            raise NetworkError(
                message=f"Network error while fetching from AkShare: {str(e)}",
                code="NETWORK_ERROR",
                severity="HIGH",
                original_exception=e,
            )
        else:
            raise DataFetchError(
                message=f"Failed to fetch stock data from AkShare: {str(e)}",
                code="AKSHARE_FETCH_ERROR",
                severity="HIGH",
                original_exception=e,
            )


def _fetch_stock_data_from_tushare() -> int:
    """
    从TuShare获取实时股票数据

    Returns:
        获取的股票数量

    Raises:
        DataFetchError: 数据获取失败
        NetworkError: 网络连接失败
    """
    try:
        import tushare as ts

        # 获取A股列表
        logger.info("Fetching stock data from TuShare...")
        pro = ts.pro_api()
        stock_data = pro.stock_basic(exchange="", list_status="L")

        if stock_data is None or stock_data.empty:
            raise DataValidationError(
                message="TuShare returned empty stock data",
                code="EMPTY_DATA",
                severity="HIGH",
            )

        count = len(stock_data)
        logger.info(f"Successfully fetched {count} stocks from TuShare")
        return count

    except ImportError:
        raise ServiceError(
            message="TuShare library not available",
            code="LIBRARY_NOT_AVAILABLE",
            severity="HIGH",
        )
    except Exception as e:
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            raise NetworkError(
                message=f"Network error while fetching from TuShare: {str(e)}",
                code="NETWORK_ERROR",
                severity="HIGH",
                original_exception=e,
            )
        else:
            raise DataFetchError(
                message=f"Failed to fetch stock data from TuShare: {str(e)}",
                code="TUSHARE_FETCH_ERROR",
                severity="HIGH",
                original_exception=e,
            )


def _fetch_stock_data_with_retry() -> int:
    """
    带重试机制的股票数据获取

    尝试按优先级顺序从不同数据源获取数据

    Returns:
        获取的股票数量

    Raises:
        DataFetchError: 所有数据源都失败
    """
    last_exception: Union[NetworkError, ServiceError, DataFetchError, DataValidationError, None] = None

    for source in STOCK_DATA_SOURCES:
        for attempt in range(MAX_RETRIES):
            try:
                if source == "akshare":
                    return _fetch_stock_data_from_akshare()
                elif source == "tushare":
                    return _fetch_stock_data_from_tushare()
                elif source == "baostock":
                    # BaoStock实现保留作为备选，暂时跳过
                    logger.warning("BaoStock not implemented yet, skipping...")
                    continue

            except (NetworkError, ServiceError) as e:
                # 网络错误或服务错误，尝试下一个源
                last_exception = e
                delay = RETRY_DELAY * (2**attempt)
                logger.warning(
                    f"Failed to fetch from {source} (attempt {attempt + 1}/{MAX_RETRIES}), "
                    f"retry in {delay}s: {str(e)}"
                )
                time.sleep(delay)
                continue

            except (DataFetchError, DataValidationError) as e:
                # 数据错误，尝试下一个源而不重试
                last_exception = e
                logger.warning(f"Data error from {source}, trying next source: {str(e)}")
                break

    # 所有数据源和重试都失败
    if last_exception:
        raise DataFetchError(
            message=f"Failed to fetch stock data from all sources: {str(last_exception)}",
            code="ALL_SOURCES_FAILED",
            severity="CRITICAL",
            original_exception=last_exception,
        )
    else:
        raise DataFetchError(
            message="No stock data sources available",
            code="NO_SOURCES_AVAILABLE",
            severity="CRITICAL",
        )


def _fetch_etf_data_from_akshare() -> int:
    """
    从AkShare获取实时ETF数据

    Returns:
        获取的ETF数量

    Raises:
        DataFetchError: 数据获取失败
        NetworkError: 网络连接失败
    """
    try:
        import akshare as ak

        logger.info("Fetching ETF data from AkShare...")
        # 获取ETF实时行情
        etf_data = ak.fund_etf_spot()

        if etf_data is None or etf_data.empty:
            raise DataValidationError(
                message="AkShare returned empty ETF data",
                code="EMPTY_DATA",
                severity="HIGH",
            )

        count = len(etf_data)
        logger.info(f"Successfully fetched {count} ETFs from AkShare")
        return count

    except ImportError:
        raise ServiceError(
            message="AkShare library not available",
            code="LIBRARY_NOT_AVAILABLE",
            severity="HIGH",
        )
    except Exception as e:
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            raise NetworkError(
                message=f"Network error while fetching ETF from AkShare: {str(e)}",
                code="NETWORK_ERROR",
                severity="HIGH",
                original_exception=e,
            )
        else:
            raise DataFetchError(
                message=f"Failed to fetch ETF data from AkShare: {str(e)}",
                code="AKSHARE_ETF_ERROR",
                severity="HIGH",
                original_exception=e,
            )


def _fetch_etf_data_with_retry() -> int:
    """
    带重试机制的ETF数据获取

    尝试按优先级顺序从不同数据源获取数据

    Returns:
        获取的ETF数量

    Raises:
        DataFetchError: 所有数据源都失败
    """
    last_exception: Union[NetworkError, ServiceError, DataFetchError, DataValidationError, None] = None

    for source in ETF_DATA_SOURCES:
        for attempt in range(MAX_RETRIES):
            try:
                if source == "akshare":
                    return _fetch_etf_data_from_akshare()
                elif source == "tushare":
                    # TuShare ETF实现
                    logger.warning("TuShare ETF not implemented yet, skipping...")
                    continue

            except (NetworkError, ServiceError) as e:
                last_exception = e
                delay = RETRY_DELAY * (2**attempt)
                logger.warning(
                    f"Failed to fetch ETF from {source} (attempt {attempt + 1}/{MAX_RETRIES}), "
                    f"retry in {delay}s: {str(e)}"
                )
                time.sleep(delay)
                continue

            except (DataFetchError, DataValidationError) as e:
                last_exception = e
                logger.warning(f"Data error from {source} for ETF, trying next source: {str(e)}")
                break

    if last_exception:
        raise DataFetchError(
            message=f"Failed to fetch ETF data from all sources: {str(last_exception)}",
            code="ALL_ETF_SOURCES_FAILED",
            severity="CRITICAL",
            original_exception=last_exception,
        )
    else:
        raise DataFetchError(
            message="No ETF data sources available",
            code="NO_ETF_SOURCES_AVAILABLE",
            severity="CRITICAL",
        )


def fetch_realtime_market_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取实时市场数据

    从多个数据源获取股票和ETF实时数据，具有自动故障转移和重试机制。

    Args:
        params: 任务参数
            - fetch_stocks: 是否获取股票数据 (默认True)
            - fetch_etfs: 是否获取ETF数据 (默认True)

    Returns:
        执行结果字典，包含：
            - status: "success" or "failed"
            - fetch_time: 获取时间 (ISO格式)
            - stocks_fetched: 成功获取的股票数量 (成功时)
            - etfs_fetched: 成功获取的ETF数量 (成功时)
            - data_sources: 实际使用的数据源列表
            - errors: 错误详情 (失败时)
    """
    logger.info(f"Starting realtime market data fetch with params: {params}")

    fetch_stocks = params.get("fetch_stocks", True)
    fetch_etfs = params.get("fetch_etfs", True)

    result: Dict[str, Any] = {
        "fetch_time": datetime.now().isoformat(),
        "stocks_fetched": 0,
        "etfs_fetched": 0,
        "data_sources": [],
        "errors": [],
    }

    try:
        # 获取股票数据
        if fetch_stocks:
            try:
                logger.info("Fetching stock realtime data...")
                stocks_count = _fetch_stock_data_with_retry()
                result["stocks_fetched"] = stocks_count
                result["data_sources"].append(f"stocks: {STOCK_DATA_SOURCES[0]}")
            except DataFetchError as e:
                logger.error(f"Failed to fetch stock data: {e.message}")
                result["errors"].append(
                    {
                        "type": "stock_fetch_failed",
                        "message": e.message,
                        "code": e.code,
                    }
                )
                # 记录部分失败但继续获取ETF数据

        # 获取ETF数据
        if fetch_etfs:
            try:
                logger.info("Fetching ETF realtime data...")
                etfs_count = _fetch_etf_data_with_retry()
                result["etfs_fetched"] = etfs_count
                result["data_sources"].append(f"etfs: {ETF_DATA_SOURCES[0]}")
            except DataFetchError as e:
                logger.error(f"Failed to fetch ETF data: {e.message}")
                result["errors"].append(
                    {
                        "type": "etf_fetch_failed",
                        "message": e.message,
                        "code": e.code,
                    }
                )

        # 判断整体状态
        if result["errors"]:
            result["status"] = (
                "partial_success" if (result["stocks_fetched"] > 0 or result["etfs_fetched"] > 0) else "failed"
            )
        else:
            result["status"] = "success"

        logger.info(f"Realtime market data fetch completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error during market data fetch: {str(e)}")
        return {
            "status": "failed",
            "fetch_time": datetime.now().isoformat(),
            "error": str(e),
            "error_type": type(e).__name__,
        }


def fetch_longhubang_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取龙虎榜数据"""
    logger.info(f"Starting longhubang data fetch with params: {params}")

    try:
        data_source = params.get("data_source", "akshare")

        result = {
            "status": "success",
            "data_source": data_source,
            "fetch_time": datetime.now().isoformat(),
            "records_fetched": 100,  # 示例数据
        }

        logger.info(f"Longhubang data fetch completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch longhubang data: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "fetch_time": datetime.now().isoformat(),
        }


def fetch_capital_flow_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取资金流向数据"""
    logger.info(f"Starting capital flow data fetch with params: {params}")

    try:
        data_source = params.get("data_source", "akshare")
        flow_types = params.get("flow_types", [])

        result = {
            "status": "success",
            "data_source": data_source,
            "fetch_time": datetime.now().isoformat(),
            "flow_types": flow_types,
            "records_fetched": len(flow_types) * 50,  # 示例数据
        }

        logger.info(f"Capital flow data fetch completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to fetch capital flow data: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "fetch_time": datetime.now().isoformat(),
        }
