"""缓存管理器子模块"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


class CacheFetchWriteMixin:
    """缓存读写与失效操作"""

    async def write_to_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        ttl_days: int = 7,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """写入数据到三级缓存 (Write-Through模式)

        同时写入L1(内存)+L2(Redis)，L3(TDengine)异步写入

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度
            data: 要缓存的数据
            ttl_days: 缓存生存时间 (天)
            timestamp: 自定义时间戳

        Returns:
            True 如果写入成功，False 否则

        """
        self._cache_stats["writes"] += 1

        try:
            # 验证数据
            is_invalid_data = data is None or not isinstance(data, dict)
            if is_invalid_data:
                logger.warning(
                    "无效的缓存数据",
                    symbol=symbol,
                    data_type=data_type,
                )
                return False

            # 增加元数据
            enriched_data = {
                **data,
                "_cached_at": datetime.now(timezone.utc).isoformat(),
                "_ttl_days": ttl_days,
                "_cache_version": "2.0",  # 升级到三级缓存版本
                "_source": "market_data",
            }

            # 准备缓存数据格式
            cache_data = {
                "data": data,
                "source": "cache",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            cache_key = self.get_cache_key(symbol, data_type, timeframe)

            # L1: 内存缓存 (同步写入，最高优先级)
            self._add_to_memory_cache(symbol, data_type, timeframe, cache_data)

            # L2: Redis缓存 (异步写入，不阻塞响应)
            if self._redis_available and self.redis_cache:
                redis_ttl = ttl_days * 24 * 3600  # 转换为秒
                asyncio.create_task(self.redis_cache.set(cache_key, cache_data, ttl=redis_ttl))

            # L3: TDengine缓存 (异步写入，持久化存储)
            asyncio.create_task(
                self._write_to_tdengine(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=enriched_data,
                    timestamp=timestamp,
                ),
            )

            logger.debug(
                "✅ 三级缓存写入完成",
                symbol=symbol,
                data_type=data_type,
                ttl_days=ttl_days,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ 三级缓存写入异常",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

            # 增加元数据
            enriched_data = {
                **data,
                "_cached_at": datetime.now(timezone.utc).isoformat(),
                "_ttl_days": ttl_days,
                "_cache_version": "1.0",
                "_source": "market_data",
            }

            # 首先写入内存缓存 (最高优先级)
            memory_data = {
                "data": data,
                "source": "memory",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._add_to_memory_cache(symbol, data_type, timeframe, memory_data)

            # 并行写入 TDengine (持久化存储)
            td_result = self._write_to_tdengine(
                symbol=symbol,
                data_type=data_type,
                timeframe=timeframe,
                data=enriched_data,
                timestamp=timestamp,
            )

            if td_result:
                logger.debug(
                    "✅ 数据已缓存(内存+TDengine)",
                    symbol=symbol,
                    data_type=data_type,
                    ttl_days=ttl_days,
                )
                return True
            logger.warning(
                "⚠️ TDengine写入失败，但内存缓存已更新",
                symbol=symbol,
                data_type=data_type,
            )
            return True  # 内存缓存成功就认为部分成功

        except Exception as e:
            logger.error(
                "❌ 缓存写入异常",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

    async def invalidate_cache(
        self,
        symbol: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> int:
        """清除三级缓存中的特定数据

        Args:
            symbol: 股票代码 (可选，如果省略则清除所有 symbol)
            data_type: 数据类型 (可选，如果省略则清除所有 data_type)

        Returns:
            删除的记录数

        """
        total_deleted = 0

        try:
            with self._cache_lock:
                # L1: 清理内存缓存
                if symbol and data_type:
                    # 清除特定符号+数据类型的缓存
                    cache_key = self.get_cache_key(symbol, data_type)

                    if cache_key in self._memory_cache:
                        del self._memory_cache[cache_key]
                        total_deleted += 1

                    if cache_key in self._cache_ttl:
                        del self._cache_ttl[cache_key]

                    if cache_key in self._access_patterns:
                        del self._access_patterns[cache_key]

                    logger.info("🗑️ 清除L1内存缓存", symbol=symbol, data_type=data_type)

                elif symbol:
                    # 清除特定符号的所有缓存
                    keys_to_delete = [key for key in self._memory_cache.keys() if key.startswith(symbol)]
                    for key in keys_to_delete:
                        del self._memory_cache[key]
                        total_deleted += 1

                        if key in self._cache_ttl:
                            del self._cache_ttl[key]
                        if key in self._access_patterns:
                            del self._access_patterns[key]

                    logger.info(
                        "🗑️ 清除符号所有L1内存缓存",
                        symbol=symbol,
                        count=len(keys_to_delete),
                    )

                else:
                    # 清除所有内存缓存
                    total_deleted = self.clear_memory_cache()
                    logger.warning("🗑️ 清除所有L1内存缓存")

            # L2: 清理Redis缓存
            if self._redis_available and self.redis_cache:
                try:
                    if symbol and data_type:
                        cache_key = self.get_cache_key(symbol, data_type)
                        await self.redis_cache.delete(cache_key)
                        logger.info("🗑️ 清除L2 Redis缓存", symbol=symbol, data_type=data_type)
                    elif symbol:
                        # 删除所有以symbol开头的缓存
                        pattern = f"{symbol}:*"
                        redis_deleted = await self.redis_cache.delete_pattern(pattern)
                        total_deleted += redis_deleted
                        logger.info("🗑️ 清除符号所有L2 Redis缓存", symbol=symbol, count=redis_deleted)
                    else:
                        await self.redis_cache.clear()
                        logger.warning("🗑️ 清除所有L2 Redis缓存")
                except Exception as e:
                    logger.warning("L2 Redis缓存清理失败", error=str(e))

            # L3: 清理TDengine缓存（异步）
            if self.tdengine is not None:
                try:
                    if symbol and data_type:
                        # 异步清理TDengine特定缓存
                        asyncio.create_task(self._async_tdengine_clear(symbol, data_type))
                    elif symbol:
                        asyncio.create_task(self._async_tdengine_clear_symbol(symbol))
                    else:
                        asyncio.create_task(self._async_tdengine_clear_all())
                except Exception as e:
                    logger.warning("L3 TDengine缓存清理任务创建失败", error=str(e))

            logger.info(
                "✅ 三级缓存清除完成",
                symbol=symbol,
                data_type=data_type,
                total_deleted=total_deleted,
            )
            return total_deleted

        except Exception as e:
            logger.error("❌ 缓存清除失败", error=str(e))
            return total_deleted

    # ==================== 批量操作 ====================

