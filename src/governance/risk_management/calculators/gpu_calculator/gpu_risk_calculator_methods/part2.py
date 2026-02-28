"""
GPU加速风险计算器
GPU-Accelerated Risk Calculator

扩展现有的GPU引擎，支持风险指标的高性能计算。
复用现有的GPU基础设施和数据源。
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


from src.governance.risk_management.core import StockRiskMetrics

# 复用现有的GPU基础设施
try:
    from src.gpu.data_processor_factory import get_processor
    from src.monitoring.async_monitoring import MonitoringEventPublisher

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    get_processor = None
    MonitoringEventPublisher = None

# 风险监控缓存系统
try:
    from src.utils.cache_optimization_enhanced import get_enhanced_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    get_enhanced_cache_manager = None

logger = logging.getLogger(__name__)


class GPURiskCalculatorGetConcentrationLevelMixin:
    """GPURiskCalculator 方法集 Part 2"""

    def _get_concentration_level_cpu(self, score: int) -> str:
        """CPU版本的集中度等级"""
        if score >= 80:
            return "highly_concentrated"
        elif score >= 60:
            return "moderately_concentrated"
        elif score >= 40:
            return "somewhat_concentrated"
        elif score >= 20:
            return "well_diversified"
        else:
            return "highly_diversified"

    async def _get_cached_risk_metrics(self, cache_key: str) -> Optional[StockRiskMetrics]:
        """从缓存获取风险指标"""
        try:
            if not self.cache_manager:
                return None

            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                # 验证缓存数据的有效性
                if self._is_cache_data_valid(cached_data):
                    return cached_data
                else:
                    # 缓存数据过期，删除
                    await self.cache_manager.delete(cache_key)

            return None

        except Exception:
            logger.debug("缓存读取失败 %(cache_key)s: %(e)s")
            return None

    async def _cache_risk_metrics(self, cache_key: str, metrics: StockRiskMetrics, ttl: int = 300):
        """缓存风险指标"""
        try:
            if not self.cache_manager:
                return

            await self.cache_manager.put(cache_key, metrics, ttl=ttl)
            self.risk_cache_stats["cache_puts"] += 1

            logger.debug("✅ 风险指标已缓存: %(cache_key)s (TTL: %(ttl)ss)")

        except Exception:
            logger.debug("缓存写入失败 %(cache_key)s: %(e)s")

    def _is_cache_data_valid(self, cached_data: Any) -> bool:
        """验证缓存数据的有效性"""
        try:
            if not isinstance(cached_data, StockRiskMetrics):
                return False

            # 检查时间戳是否在合理范围内 (不超过1小时)
            age_seconds = (datetime.now() - cached_data.timestamp).total_seconds()
            return age_seconds < 3600  # 1小时

        except Exception:
            return False

    def _update_cache_stats(self, start_time: float, hit: bool):
        """更新缓存统计信息"""
        self.risk_cache_stats["total_cache_requests"] += 1

        access_time = time.time() - start_time
        self.risk_cache_stats["avg_cache_time"] = (
            (self.risk_cache_stats["avg_cache_time"] * (self.risk_cache_stats["total_cache_requests"] - 1))
            + access_time
        ) / self.risk_cache_stats["total_cache_requests"]

    async def get_risk_cache_performance(self) -> Dict[str, Any]:
        """获取风险缓存性能统计"""
        try:
            if not self.cache_manager:
                return {"cache_enabled": False}

            base_stats = self.cache_manager.get_comprehensive_stats()

            total_requests = self.risk_cache_stats["cache_hits"] + self.risk_cache_stats["cache_misses"]
            hit_rate = self.risk_cache_stats["cache_hits"] / total_requests * 100 if total_requests > 0 else 0

            return {
                "cache_enabled": True,
                "risk_cache_stats": {
                    "cache_hits": self.risk_cache_stats["cache_hits"],
                    "cache_misses": self.risk_cache_stats["cache_misses"],
                    "cache_puts": self.risk_cache_stats["cache_puts"],
                    "hit_rate_percent": hit_rate,
                    "avg_cache_access_time_ms": self.risk_cache_stats["avg_cache_time"] * 1000,
                    "total_cache_requests": self.risk_cache_stats["total_cache_requests"],
                },
                "multi_level_cache_stats": base_stats.get("cache_stats", {}),
                "optimization_suggestions": base_stats.get("optimization_suggestions", []),
            }

        except Exception as e:
            logger.error("获取缓存性能统计失败: %(e)s")
            return {"error": str(e), "cache_enabled": bool(self.cache_manager)}

    async def clear_risk_cache(self, pattern: Optional[str] = None):
        """清除风险缓存"""
        try:
            if not self.cache_manager:
                return

            if pattern:
                # 清除匹配模式的风险缓存
                await self.cache_manager.clear_pattern(f"*{pattern}*")
            else:
                # 清除所有风险相关缓存
                await self.cache_manager.clear_pattern("*risk*")
                await self.cache_manager.clear_pattern("*portfolio*")

            # 重置统计信息
            self.risk_cache_stats = {
                "cache_hits": 0,
                "cache_misses": 0,
                "cache_puts": 0,
                "avg_cache_time": 0.0,
                "total_cache_requests": 0,
            }

            logger.info("✅ 风险缓存已清除")

        except Exception:
            logger.error("清除风险缓存失败: %(e)s")

    async def warmup_risk_cache(self, symbols: List[str]):
        """预热风险缓存"""
        try:
            if not self.cache_manager:
                return

            logger.info("开始预热风险缓存，共 {len(symbols)} 个股票")

            # 并发预热风险计算
            tasks = []
            for symbol in symbols:
                task = asyncio.create_task(self.calculate_stock_risk(symbol, use_cache=False))
                tasks.append(task)

            # 等待所有预热完成
            await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("✅ 风险缓存预热完成")

        except Exception:
            logger.error("风险缓存预热失败: %(e)s")

    async def monitor_risk_cache_health(self) -> Dict[str, Any]:
        """监控风险缓存健康状态"""
        try:
            if not self.cache_manager:
                return {"cache_enabled": False, "health_status": "disabled"}

            stats = await self.get_risk_cache_performance()

            # 健康检查标准
            hit_rate = stats.get("risk_cache_stats", {}).get("hit_rate_percent", 0)
            avg_access_time = stats.get("risk_cache_stats", {}).get("avg_cache_access_time_ms", 0)

            health_issues = []

            if hit_rate < 70:
                health_issues.append("缓存命中率偏低")
            if avg_access_time > 50:  # 超过50ms
                health_issues.append("缓存访问延迟过高")
            if (
                stats.get("risk_cache_stats", {}).get("cache_misses", 0)
                > stats.get("risk_cache_stats", {}).get("cache_hits", 0) * 2
            ):
                health_issues.append("缓存未命中率过高")

            health_status = "healthy" if not health_issues else "warning" if len(health_issues) == 1 else "critical"

            return {
                "cache_enabled": True,
                "health_status": health_status,
                "health_issues": health_issues,
                "performance_metrics": stats,
                "recommendations": self._generate_cache_recommendations(health_issues),
            }

        except Exception as e:
            logger.error("缓存健康监控失败: %(e)s")
            return {
                "cache_enabled": bool(self.cache_manager),
                "health_status": "error",
                "error": str(e),
            }

    def _generate_cache_recommendations(self, health_issues: List[str]) -> List[str]:
        """生成缓存优化建议"""
        recommendations = []

        for issue in health_issues:
            if "命中率偏低" in issue:
                recommendations.extend(
                    [
                        "考虑增加缓存TTL时间",
                        "检查数据访问模式，优化缓存键设计",
                        "启用预测性预加载功能",
                    ]
                )
            elif "访问延迟过高" in issue:
                recommendations.extend(
                    [
                        "检查Redis连接性能",
                        "考虑增加L1缓存大小",
                        "优化数据压缩策略",
                    ]
                )
            elif "未命中率过高" in issue:
                recommendations.extend(
                    [
                        "启用负缓存以减少无效查询",
                        "调整缓存失效策略",
                        "增加热点数据预加载",
                    ]
                )

        return recommendations

