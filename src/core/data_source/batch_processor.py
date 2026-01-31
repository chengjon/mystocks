"""
批量处理器模块 (BatchProcessor)

为 GovernanceDataFetcher 提供并发批量处理能力。
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    批量处理器

    特性:
    - ThreadPoolExecutor 并发调用
    - 按数据源分组批量请求
    - 超时控制 (30 秒)
    - 异常隔离 (单个失败不影响其他)
    - 优雅关闭
    """

    def __init__(
        self,
        max_workers: int = 10,  # 最大并发线程数
        timeout: float = 30.0,  # 单个请求超时时间 (秒)
    ):
        """
        初始化批量处理器

        Args:
            max_workers: 最大并发线程数
            timeout: 单个请求超时时间
        """
        self.max_workers = max_workers
        self.timeout = timeout

        # 创建线程池
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="batch_processor",
        )

        # 统计信息
        self.total_batches = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        logger.info("BatchProcessor initialized: max_workers=%(max_workers)s, timeout=%(timeout)ss")

    def fetch_batch_kline(
        self,
        data_fetcher: Any,  # GovernanceDataFetcher 实例
        symbols: List[str],
        start_date: str,
        end_date: str,
        adjust: str = "qfq",
    ) -> Dict[str, Any]:
        """
        批量获取 K线数据 (并发版本)

        Args:
            data_fetcher: GovernanceDataFetcher 实例
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            {
                "success": bool,
                "data": {symbol: kline_data},
                "errors": {symbol: error_message},
                "stats": {...},
            }
        """
        logger.info("Batch fetching K-line data for {len(symbols)} symbols")

        # 按数据源分组
        grouped_requests = self._group_by_data_source(data_fetcher, symbols)

        results: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        # 提交并发任务
        futures = {}
        for data_source, source_symbols in grouped_requests.items():
            for symbol in source_symbols:
                future = self.executor.submit(
                    self._fetch_single_kline,
                    data_fetcher,
                    symbol,
                    start_date,
                    end_date,
                    adjust,
                )
                futures[future] = (data_source, symbol)

        # 等待所有任务完成
        completed = 0
        total = len(futures)

        for future in as_completed(futures):
            data_source, symbol = futures[future]
            completed += 1

            try:
                # 获取结果 (带超时)
                result = future.result(timeout=self.timeout)

                if result.get("success"):
                    results[symbol] = result.get("data")
                    self.successful_requests += 1
                else:
                    error = result.get("error", "Unknown error")
                    errors[symbol] = error
                    self.failed_requests += 1
                    logger.warning("Failed to fetch %(symbol)s: %(error)s")

            except Exception as e:
                errors[symbol] = str(e)
                self.failed_requests += 1
                logger.error("Exception fetching %(symbol)s: %(e)s")

            if completed % 10 == 0:
                logger.debug("Progress: %(completed)s/%(total)s completed")

        self.total_batches += 1
        self.total_requests += total

        # 返回结果
        return {
            "success": len(errors) == 0,
            "data": results,
            "errors": errors,
            "stats": {
                "total_symbols": len(symbols),
                "successful": len(results),
                "failed": len(errors),
                "success_rate": len(results) / len(symbols) if symbols else 0,
            },
        }

    def fetch_batch_realtime(
        self,
        data_fetcher: Any,
        symbols: List[str],
    ) -> Dict[str, Any]:
        """
        批量获取实时行情 (并发版本)

        Args:
            data_fetcher: GovernanceDataFetcher 实例
            symbols: 股票代码列表

        Returns:
            {
                "success": bool,
                "data": {symbol: realtime_data},
                "errors": {symbol: error_message},
                "stats": {...},
            }
        """
        logger.info("Batch fetching realtime data for {len(symbols)} symbols")

        results: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        # 提交并发任务
        futures = {}
        for symbol in symbols:
            future = self.executor.submit(
                self._fetch_single_realtime,
                data_fetcher,
                symbol,
            )
            futures[future] = symbol

        # 等待所有任务完成
        completed = 0
        total = len(futures)

        for future in as_completed(futures):
            symbol = futures[future]
            completed += 1

            try:
                # 获取结果 (带超时)
                result = future.result(timeout=self.timeout)

                if result.get("success"):
                    results[symbol] = result.get("data")
                    self.successful_requests += 1
                else:
                    error = result.get("error", "Unknown error")
                    errors[symbol] = error
                    self.failed_requests += 1
                    logger.warning("Failed to fetch %(symbol)s: %(error)s")

            except Exception as e:
                errors[symbol] = str(e)
                self.failed_requests += 1
                logger.error("Exception fetching %(symbol)s: %(e)s")

            if completed % 10 == 0:
                logger.debug("Progress: %(completed)s/%(total)s completed")

        self.total_batches += 1
        self.total_requests += total

        # 返回结果
        return {
            "success": len(errors) == 0,
            "data": results,
            "errors": errors,
            "stats": {
                "total_symbols": len(symbols),
                "successful": len(results),
                "failed": len(errors),
                "success_rate": len(results) / len(symbols) if symbols else 0,
            },
        }

    def _group_by_data_source(self, data_fetcher: Any, symbols: List[str]) -> Dict[str, List[str]]:
        """
        按数据源分组股票代码

        Args:
            data_fetcher: GovernanceDataFetcher 实例
            symbols: 股票代码列表

        Returns:
            {data_source: [symbols]}
        """
        grouped = {}

        for symbol in symbols:
            # 获取最优数据源
            best_endpoint = data_fetcher.manager.get_best_endpoint("DAILY_KLINE")

            if best_endpoint:
                data_source = best_endpoint.get("endpoint_name", "unknown")
            else:
                data_source = "unknown"

            if data_source not in grouped:
                grouped[data_source] = []

            grouped[data_source].append(symbol)

        logger.debug("Grouped {len(symbols)} symbols into {len(grouped)} data sources")

        return grouped

    def _fetch_single_kline(
        self,
        data_fetcher: Any,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str,
    ) -> Dict[str, Any]:
        """
        获取单个股票的 K线数据

        Args:
            data_fetcher: GovernanceDataFetcher 实例
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            {
                "success": bool,
                "data": kline_data,
                "error": error_message,
            }
        """
        try:
            # 调用 data_fetcher 的同步方法
            # 注意: 这里保持同步调用，由 BatchProcessor 管理并发
            data = data_fetcher.fetch_kline(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            )

            if data is not None:
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fetch_single_realtime(
        self,
        data_fetcher: Any,
        symbol: str,
    ) -> Dict[str, Any]:
        """
        获取单个股票的实时行情

        Args:
            data_fetcher: GovernanceDataFetcher 实例
            symbol: 股票代码

        Returns:
            {
                "success": bool,
                "data": realtime_data,
                "error": error_message,
            }
        """
        try:
            # 调用 data_fetcher 的同步方法
            data = data_fetcher.fetch_realtime(symbol=symbol)

            if data is not None:
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        success_rate = self.successful_requests / self.total_requests if self.total_requests > 0 else 0

        return {
            "total_batches": self.total_batches,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
        }

    def shutdown(self, wait: bool = True):
        """
        关闭批量处理器

        Args:
            wait: 是否等待所有任务完成
        """
        logger.info("Shutting down BatchProcessor...")
        self.executor.shutdown(wait=wait)
        logger.info("BatchProcessor shutdown complete")

    def __del__(self):
        """析构函数，确保线程池关闭"""
        try:
            self.shutdown(wait=False)
        except Exception:
            pass
