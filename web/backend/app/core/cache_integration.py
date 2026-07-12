"""Cache Integration Module - 缓存集成工具

提供与数据服务集成的缓存工具函数，实现Cache-Aside模式。

Features:
- Cache-Aside读写模式
- 数据存储一致性保证
- 灵活的失效策略
- 性能优化装饰器

Usage:
    ```python
    # 使用装饰器包装现有方法
    @cache_read_wrapper(data_type="fund_flow")
    def fetch_fund_flow(symbol, timeframe):
        # 原始实现
        pass

    # 或使用手动模式
    cache_mgr = CacheIntegration.get_instance()
    data = cache_mgr.fetch_with_cache(
        symbol="000001",
        data_type="fund_flow",
        fetch_fn=lambda: fetch_from_source()
    )
    ```
"""

from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

import structlog

from app.core.cache_manager import CacheManager, get_cache_manager


logger = structlog.get_logger()

T = TypeVar("T")


class CacheIntegration:
    """缓存集成工具类"""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """初始化缓存集成

        Args:
            cache_manager: CacheManager实例 (如果不提供，使用单例)

        """
        self.cache_manager = cache_manager or get_cache_manager()
        logger.info("🔧 初始化缓存集成工具")

    # ==================== 读取模式 (Cache-Aside Read) ====================

    def fetch_with_cache(
        self,
        symbol: str,
        data_type: str,
        fetch_fn: Callable[[], Dict[str, Any]],
        timeframe: Optional[str] = None,
        use_cache: bool = True,
        ttl_days: int = 7,
    ) -> Dict[str, Any]:
        """缓存读取模式 (Cache-Aside)

        执行流程:
        1. 尝试从缓存读取
        2. 如果命中，返回缓存数据
        3. 如果未命中，调用fetch_fn从源获取数据
        4. 将数据写入缓存
        5. 返回数据

        Args:
            symbol: 股票代码
            data_type: 数据类型 (fund_flow, etf, chip_race, lhb等)
            fetch_fn: 从源获取数据的函数
            timeframe: 时间维度 (可选)
            use_cache: 是否使用缓存 (默认True)
            ttl_days: 缓存生存时间

        Returns:
            数据字典，包含:
            {
                "data": {...},
                "source": "cache" | "source",
                "timestamp": "2025-11-06T...",
                "cached_at": "2025-11-06T..." (仅当source=cache时)
            }

        """
        timeframe = timeframe or "1d"

        # 尝试从缓存读取
        if use_cache:
            cached_result = self.cache_manager.fetch_from_cache(
                symbol=symbol,
                data_type=data_type,
                timeframe=timeframe,
            )

            if cached_result:
                logger.info(
                    "✅ 缓存命中",
                    symbol=symbol,
                    data_type=data_type,
                    source="cache",
                )
                return cached_result

        # 缓存未命中，从源获取数据
        logger.debug(
            "⚠️ 缓存未命中，从源获取",
            symbol=symbol,
            data_type=data_type,
        )

        try:
            source_data = fetch_fn()

            if source_data:
                # 写入缓存
                if use_cache and isinstance(source_data, dict):
                    success = self.cache_manager.write_to_cache(
                        symbol=symbol,
                        data_type=data_type,
                        timeframe=timeframe,
                        data=source_data,
                        ttl_days=ttl_days,
                    )

                    if success:
                        logger.debug(
                            "✅ 数据已写入缓存",
                            symbol=symbol,
                            data_type=data_type,
                        )

                return {
                    "data": source_data,
                    "source": "source",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            logger.warning(
                "⚠️ 源数据为空",
                symbol=symbol,
                data_type=data_type,
            )
            return {
                "data": None,
                "source": "source",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(
                "❌ 获取源数据失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            raise

    def batch_fetch_with_cache(
        self,
        queries: List[Dict[str, Any]],
        fetch_fn: Callable[[str], Dict[str, Any]],
        use_cache: bool = True,
        ttl_days: int = 7,
    ) -> Dict[str, Dict[str, Any]]:
        """批量缓存读取

        Args:
            queries: 查询列表，每个元素:
                {
                    "symbol": "000001",
                    "data_type": "fund_flow",
                    "timeframe": "1d"  # 可选
                }
            fetch_fn: 接受symbol的获取函数
            use_cache: 是否使用缓存
            ttl_days: 缓存生存时间

        Returns:
            {
                "000001:fund_flow": {...},
                "000858:etf": {...},
                ...
            }

        """
        results = {}

        for query in queries:
            symbol = query.get("symbol")
            data_type = query.get("data_type")
            timeframe = query.get("timeframe", "1d")

            if not symbol or not data_type:
                logger.warning("查询缺少必要字段", query=query)
                continue

            try:
                result = self.fetch_with_cache(
                    symbol=symbol,
                    data_type=data_type,
                    fetch_fn=lambda s=symbol: fetch_fn(s),
                    timeframe=timeframe,
                    use_cache=use_cache,
                    ttl_days=ttl_days,
                )

                cache_key = f"{symbol}:{data_type}"
                results[cache_key] = result

            except Exception as e:
                logger.error(
                    "批量读取失败",
                    symbol=symbol,
                    data_type=data_type,
                    error=str(e),
                )
                results[f"{symbol}:{data_type}"] = {
                    "data": None,
                    "source": "error",
                    "error": str(e),
                }

        return results

    # ==================== 写入模式 (Cache-Aside Write) ====================

    def save_with_cache(
        self,
        symbol: str,
        data_type: str,
        data: Dict[str, Any],
        save_fn: Callable[[Dict[str, Any]], bool],
        timeframe: Optional[str] = None,
        use_cache: bool = True,
        ttl_days: int = 7,
    ) -> bool:
        """缓存写入模式 (Cache-Aside Write)

        执行流程:
        1. 调用save_fn保存到源
        2. 如果源保存成功，更新缓存
        3. 返回结果

        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: 要保存的数据
            save_fn: 保存到源的函数 (接受数据字典，返回bool)
            timeframe: 时间维度 (可选)
            use_cache: 是否使用缓存
            ttl_days: 缓存生存时间

        Returns:
            bool: 是否成功保存

        """
        timeframe = timeframe or "1d"

        try:
            # 1. 保存到源
            logger.debug(
                "保存数据到源",
                symbol=symbol,
                data_type=data_type,
            )

            success = save_fn(data)

            if not success:
                logger.warning(
                    "源保存失败",
                    symbol=symbol,
                    data_type=data_type,
                )
                return False

            # 2. 更新缓存
            if use_cache:
                cache_success = self.cache_manager.write_to_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=data,
                    ttl_days=ttl_days,
                )

                if cache_success:
                    logger.debug(
                        "✅ 数据已同时保存到缓存",
                        symbol=symbol,
                        data_type=data_type,
                    )
                else:
                    logger.warning(
                        "⚠️ 缓存保存失败，但源保存成功",
                        symbol=symbol,
                        data_type=data_type,
                    )

            logger.info(
                "✅ 数据保存成功",
                symbol=symbol,
                data_type=data_type,
                use_cache=use_cache,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ 数据保存失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            raise

    def batch_save_with_cache(
        self,
        records: List[Dict[str, Any]],
        save_fn: Callable[[List[Dict[str, Any]]], int],
        data_type: str,
        use_cache: bool = True,
        ttl_days: int = 7,
    ) -> int:
        """批量缓存写入

        Args:
            records: 记录列表，每个元素:
                {
                    "symbol": "000001",
                    "data": {...},
                    "timeframe": "1d"  # 可选
                }
            save_fn: 批量保存函数 (接受记录列表，返回保存数量)
            data_type: 数据类型
            use_cache: 是否使用缓存
            ttl_days: 缓存生存时间

        Returns:
            成功保存的记录数

        """
        try:
            # 1. 批量保存到源
            saved_count = save_fn(records)

            if saved_count == 0:
                logger.warning("批量保存返回0条")
                return 0

            # 2. 批量写入缓存
            if use_cache:
                cache_records = []
                for record in records[:saved_count]:  # 仅缓存实际保存的记录
                    symbol = record.get("symbol")
                    data = record.get("data", {})
                    timeframe = record.get("timeframe", "1d")

                    if symbol and data:
                        cache_records.append(
                            {
                                "symbol": symbol,
                                "data_type": data_type,
                                "timeframe": timeframe,
                                "data": data,
                            },
                        )

                if cache_records:
                    cache_count = self.cache_manager.batch_write(cache_records, ttl_days=ttl_days)

                    logger.debug(
                        "✅ 批量缓存写入",
                        total=saved_count,
                        cached=cache_count,
                    )

            logger.info(
                "✅ 批量保存成功",
                saved_count=saved_count,
                data_type=data_type,
            )
            return saved_count

        except Exception as e:
            logger.error(
                "❌ 批量保存失败",
                data_type=data_type,
                error=str(e),
            )
            raise

    # ==================== 缓存管理 ====================

    def invalidate_data(
        self,
        symbol: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> int:
        """清除缓存

        Args:
            symbol: 股票代码 (可选)
            data_type: 数据类型 (可选)

        Returns:
            清除的记录数

        """
        return self.cache_manager.invalidate_cache(symbol=symbol, data_type=data_type)

    def is_cache_fresh(
        self,
        symbol: str,
        data_type: str,
        max_age_days: int = 7,
    ) -> bool:
        """检查缓存是否新鲜

        Args:
            symbol: 股票代码
            data_type: 数据类型
            max_age_days: 最大缓存年龄

        Returns:
            bool: 缓存是否有效且未过期

        """
        return self.cache_manager.is_cache_valid(
            symbol=symbol,
            data_type=data_type,
            max_age_days=max_age_days,
        )

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self.cache_manager.get_cache_stats()


# ==================== 全局实例 ====================

_cache_integration: Optional[CacheIntegration] = None


def get_cache_integration(
    cache_manager: Optional[CacheManager] = None,
) -> CacheIntegration:
    """获取缓存集成工具单例

    Args:
        cache_manager: CacheManager实例 (可选)

    Returns:
        CacheIntegration实例

    """
    global _cache_integration

    if _cache_integration is None:
        _cache_integration = CacheIntegration(cache_manager)

    return _cache_integration


def reset_cache_integration() -> None:
    """重置缓存集成工具（用于测试）"""
    global _cache_integration
    _cache_integration = None


# ==================== 装饰器 ====================


def cache_read_wrapper(data_type: str, ttl_days: int = 7):
    """装饰器: 为读取方法添加缓存

    Usage:
        ```python
        @cache_read_wrapper("fund_flow")
        def query_fund_flow(symbol: str, timeframe: str = "1"):
            # 原始实现
            pass

        # 调用时自动使用缓存
        result = query_fund_flow("000001", "1")
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(symbol: str, *args, **kwargs) -> Dict[str, Any]:
            cache_mgr = get_cache_integration()

            return cache_mgr.fetch_with_cache(
                symbol=symbol,
                data_type=data_type,
                fetch_fn=lambda: func(symbol, *args, **kwargs),
                timeframe=kwargs.get("timeframe", "1d"),
                ttl_days=ttl_days,
            )

        return wrapper

    return decorator


def cache_write_wrapper(data_type: str, ttl_days: int = 7):
    """装饰器: 为写入方法添加缓存

    Usage:
        ```python
        @cache_write_wrapper("fund_flow")
        def save_fund_flow(symbol: str, data: dict):
            # 原始实现
            pass

        # 调用时自动使用缓存
        save_fund_flow("000001", {"value": 100})
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(symbol: str, data: Dict[str, Any], *args, **kwargs) -> bool:
            cache_mgr = get_cache_integration()

            return cache_mgr.save_with_cache(
                symbol=symbol,
                data_type=data_type,
                data=data,
                save_fn=lambda d: func(symbol, d, *args, **kwargs),
                timeframe=kwargs.get("timeframe", "1d"),
                ttl_days=ttl_days,
            )

        return wrapper

    return decorator


def cache_invalidate_on_write(data_type: Optional[str] = None):
    """装饰器: 在写入时自动清除缓存

    Usage:
        ```python
        @cache_invalidate_on_write("fund_flow")
        def delete_fund_flow(symbol: str):
            # 删除实现
            pass
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(symbol: str, *args, **kwargs) -> Any:
            result = func(symbol, *args, **kwargs)

            # 调用后清除缓存
            cache_mgr = get_cache_integration()
            cache_mgr.invalidate_data(symbol=symbol, data_type=data_type)

            logger.debug(
                "✅ 缓存已清除",
                symbol=symbol,
                data_type=data_type,
            )

            return result

        return wrapper

    return decorator
