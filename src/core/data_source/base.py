"""
数据源管理器 V2.0 (中心化注册表 + 智能路由)
"""

import logging
from typing import Dict, List, Any, Optional
from .cache import LRUCache
from .smart_cache import SmartCache
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceManagerV2:
    """
    数据源管理器 V2.0
    """

    def __init__(self, yaml_config_path: str = "config/data_sources_registry.yaml", use_smart_cache: bool = True):
        """
        初始化数据源管理器

        Args:
            yaml_config_path: YAML配置文件路径
            use_smart_cache: 是否使用SmartCache (True) 或 LRUCache (False)
        """
        self.yaml_config_path = yaml_config_path
        self.registry = {}
        self.db_manager = None
        self.use_smart_cache = use_smart_cache

        # 熔断器字典 (每个endpoint一个)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # 加载所有数据源配置
        self._load_registry()

        logger.info(f"DataSourceManagerV2 初始化完成，已加载 {len(self.registry)} 个数据源")
        if use_smart_cache:
            logger.info("SmartCache 已启用")
        else:
            logger.info("LRUCache 已启用 (传统模式)")

    def _get_db_manager(self):
        """延迟加载数据库管理器"""
        if self.db_manager is None:
            from src.storage.database import DatabaseConnectionManager

            self.db_manager = DatabaseConnectionManager()
        return self.db_manager

    def _load_registry(self):
        """从数据库和YAML加载所有数据源配置"""
        logger.info("开始加载数据源注册表...")

        # 1. 从数据库加载
        try:
            db_sources = self._load_from_database()
        except Exception as e:
            logger.debug(f"DB load failed (expected if db not ready): {e}")
            db_sources = {}

        # 2. 从YAML加载配置
        try:
            yaml_sources = self._load_from_yaml()
        except Exception as e:
            logger.warning(f"YAML load failed: {e}")
            yaml_sources = {}

        # 3. 合并配置
        all_sources = self._merge_sources(db_sources, yaml_sources)

        # 4. 创建处理器和缓存
        for endpoint_name, source_config in all_sources.items():
            if source_config.get("status") != "active":
                continue

            # 选择缓存类型
            if self.use_smart_cache:
                cache = SmartCache(maxsize=100, default_ttl=3600, refresh_threshold=0.8)
            else:
                cache = LRUCache(maxsize=100)

            self.registry[endpoint_name] = {
                "config": source_config,
                "handler": None,
                "cache": cache,
                "last_call": None,
                "call_count": 0,
            }

            # 创建熔断器
            self.circuit_breakers[endpoint_name] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                name=endpoint_name,
            )

    def _load_from_database(self) -> Dict:
        from .registry import _load_from_database

        return _load_from_database(self)

    def _load_from_yaml(self) -> Dict:
        from .registry import _load_from_yaml

        return _load_from_yaml(self)

    def _merge_sources(self, db_sources: Dict, yaml_sources: Dict) -> Dict:
        from .registry import _merge_sources

        return _merge_sources(self, db_sources, yaml_sources)

    def find_endpoints(self, **kwargs) -> List[Dict]:
        from .router import find_endpoints

        return find_endpoints(self, **kwargs)

    def get_best_endpoint(self, data_category: str) -> Optional[Dict]:
        from .router import get_best_endpoint

        return get_best_endpoint(self, data_category)

    def _call_endpoint(self, endpoint_info: Dict, **kwargs) -> Any:
        from .handler import _call_endpoint

        return _call_endpoint(self, endpoint_info, **kwargs)

    def get_stock_daily(self, symbol, start_date=None, end_date=None, adjust="qfq"):
        best = self.get_best_endpoint("DAILY_KLINE")
        if not best:
            logger.warning(f"No endpoint found for DAILY_KLINE")
            return None
        return self._call_endpoint(best, symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust)

    def get_stock_realtime(self, symbols):
        best = self.get_best_endpoint("REALTIME_QUOTE")
        if not best:
            return None
        return self._call_endpoint(best, symbols=symbols)

    def list_all_endpoints(self):
        from .router import list_all_endpoints

        return list_all_endpoints(self)

    def _record_success(self, *args, **kwargs):
        pass

    def _record_failure(self, *args, **kwargs):
        pass

    def _save_call_history_async(self, *args, **kwargs):
        pass

    def _create_handler(self, endpoint_info):
        from .handler import _create_handler

        return _create_handler(self, endpoint_info)

    def _identify_caller(self):
        from .handler import _identify_caller

        return _identify_caller(self)

    def _validate_data(self, *args, **kwargs):
        pass
