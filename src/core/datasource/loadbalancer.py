"""
Data Source Load Balancer

Provides intelligent load balancing and failover capabilities
for selecting the optimal data source for requests.
"""

import asyncio
import logging
import random
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from .registry import DataSourceConfig, DataSourceInfo, DataSourceRegistry, HealthStatus

logger = logging.getLogger(__name__)


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""

    max_retries: int = 3
    retry_delay: float = 0.5
    fallback_enabled: bool = True
    health_check_enabled: bool = True


class MultiSourceLoadBalancer:
    """
    Load balancer that selects the optimal data source based on
    health status, weight, and availability.
    """

    def __init__(self, registry: DataSourceRegistry, config: Optional[LoadBalancerConfig] = None):
        self._registry = registry
        self._config = config or LoadBalancerConfig()
        self._request_counts: Dict[str, int] = {}

    async def select_source(
        self, preferred_sources: Optional[List[str]] = None
    ) -> Tuple[Optional[DataSourceConfig], str]:
        """
        Select the best data source for a request.

        Args:
            preferred_sources: List of preferred source IDs (in order of preference)

        Returns:
            Tuple of (selected config, selection_reason)
        """
        sources = await self._registry.list_sources()
        enabled_sources = [s for s in sources if s.config.enabled]

        if not enabled_sources:
            return None, "no_enabled_sources"

        # Filter to preferred sources if specified
        if preferred_sources:
            preferred = [s for s in enabled_sources if s.source_id in preferred_sources]
            if preferred:
                enabled_sources = preferred

        # Get healthy sources
        healthy_sources = [s for s in enabled_sources if s.health_status == HealthStatus.HEALTHY]

        if healthy_sources:
            # Weighted random selection among healthy sources
            selected = self._weighted_selection(healthy_sources)
            return selected.config, "healthy_selected"

        # No healthy sources, try unhealthy but available
        available_sources = [
            s for s in enabled_sources if s.health_status in (HealthStatus.UNKNOWN, HealthStatus.UNHEALTHY)
        ]

        if available_sources and self._config.fallback_enabled:
            selected = self._weighted_selection(available_sources)
            return selected.config, "fallback_selected"

        # All sources are in error state
        if enabled_sources:
            selected = self._weighted_selection(enabled_sources)
            return selected.config, "error_fallback"

        return None, "no_sources_available"

    def _weighted_selection(self, sources: List[DataSourceInfo]) -> DataSourceInfo:
        """
        Perform weighted random selection among sources.

        Args:
            sources: List of data source infos

        Returns:
            Selected data source info
        """
        if len(sources) == 1:
            return sources[0]

        # Calculate total weight
        total_weight = sum(s.config.weight for s in sources)

        # Random selection based on weight
        random_value = random.uniform(0, total_weight)
        cumulative = 0

        for source in sources:
            cumulative += source.config.weight
            if random_value <= cumulative:
                return source

        return sources[0]

    async def execute_with_failover(
        self,
        operation: str,
        execute_func: Callable[[DataSourceConfig], Awaitable[Any]],
        preferred_sources: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
    ) -> Tuple[Any, bool]:
        """
        Execute an operation with automatic failover.

        Args:
            operation: Operation name for logging
            execute_func: Async function that takes a DataSourceConfig and returns result
            preferred_sources: Preferred data sources
            max_retries: Maximum number of retries

        Returns:
            Tuple of (result, success)
        """
        max_retries = max_retries or self._config.max_retries
        sources_tried = set()

        for attempt in range(max_retries):
            config, reason = await self.select_source(preferred_sources)

            if not config:
                logger.error("[%(operation)s] No data source available")
                return None, False

            if config.source_id in sources_tried:
                continue

            sources_tried.add(config.source_id)

            try:
                logger.info(
                    f"[{operation}] Attempt {attempt + 1}/{max_retries} using {config.source_id} (reason: {reason})"
                )

                result = await execute_func(config)

                logger.info("[%(operation)s] Success with {config.source_id")
                return result, True

            except Exception as e:
                logger.warning("[%(operation)s] Failed with {config.source_id}: %(e)s")

                # Mark source as unhealthy temporarily
                from .health import HealthReport, HealthStatus

                report = HealthReport(
                    source_id=config.source_id,
                    status=HealthStatus.UNHEALTHY,
                    error=str(e),
                )
                await self._registry.update_health_status(config.source_id, report)

                if attempt < max_retries - 1:
                    await asyncio.sleep(self._config.retry_delay)

        logger.error("[%(operation)s] All retries failed. Sources tried: %(sources_tried)s")
        return None, False

    async def get_source_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all data sources.

        Returns:
            Dictionary mapping source_id to statistics
        """
        sources = await self._registry.list_sources()
        stats = {}

        for source in sources:
            stats[source.source_id] = {
                "name": source.name,
                "type": source.source_type.value,
                "health_status": source.health_status.value,
                "weight": source.config.weight,
                "enabled": source.config.enabled,
                "request_count": self._request_counts.get(source.source_id, 0),
            }

        return stats

    async def record_request(self, source_id: str) -> None:
        """Record a request for a data source"""
        self._request_counts[source_id] = self._request_counts.get(source_id, 0) + 1
