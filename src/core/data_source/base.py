"""
数据源管理器 V2.0 (中心化注册表 + 智能路由)

核心功能：
1. 从PostgreSQL注册表和YAML配置加载数据源元数据
2. 提供5层数据分类维度的查询接口
3. 智能路由：根据质量评分、优先级、健康状态自动选择最佳数据源
4. 健康监控：定时检查接口可用性、记录调用历史
5. 向后兼容：保留高层业务接口（get_stock_daily等）

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceManagerV2:
    """
    数据源管理器 V2.0

    设计理念：
    - 中心化注册表：所有接口元数据存储在PostgreSQL
    - 5层数据分类绑定：每个接口必须绑定到你的34个分类之一
    - 智能路由：自动选择质量最好、优先级最高的健康接口
    - 向后兼容：保留高层业务接口，内部调用V2逻辑

    使用示例：
        # 方式1：查询可用接口（解决"找接口难"）
        manager = DataSourceManagerV2()
        apis = manager.find_endpoints("DAILY_KLINE")

        # 方式2：获取最佳接口（智能路由）
        best = manager.get_best_endpoint("DAILY_KLINE")

        # 方式3：高层业务接口（向后兼容）
        data = manager.get_stock_daily(symbol="000001")
    """

    def __init__(self, yaml_config_path: str = "config/data_sources_registry.yaml"):
        """
        初始化数据源管理器

        Args:
            yaml_config_path: YAML配置文件路径
        """
        self.yaml_config_path = yaml_config_path
        self.registry = {}  # 内存缓存：{endpoint_name: {config, handler, cache}}
        self.db_manager = None  # 延迟加载

        # 加载所有数据源配置
        self._load_registry()

        logger.info(f"DataSourceManagerV2 初始化完成，已加载 {len(self.registry)} 个数据源")

    def _get_db_manager(self):
        """延迟加载数据库管理器（避免循环导入）"""
        if self.db_manager is None:
            from src.storage.database import DatabaseConnectionManager

            self.db_manager = DatabaseConnectionManager()
        return self.db_manager

    def _load_registry(self):
        """从数据库和YAML加载所有数据源配置"""
        logger.info("开始加载数据源注册表...")

        # 1. 从数据库加载（运行时统计）
        db_sources = self._load_from_database()
        logger.info(f"从数据库加载 {len(db_sources)} 个数据源")

        # 2. 从YAML加载配置（版本控制和批量配置）
        yaml_sources = self._load_from_yaml()
        logger.info(f"从YAML加载 {len(yaml_sources)} 个数据源配置")

        # 3. 合并配置（数据库优先，补充YAML中的新数据源）
        all_sources = self._merge_sources(db_sources, yaml_sources)

        # 4. 创建处理器和缓存
        for endpoint_name, source_config in all_sources.items():
            if source_config.get("status") != "active":
                continue

            # 延迟创建handler（按需加载）
            self.registry[endpoint_name] = {
                "config": source_config,
                "handler": None,  # 延迟创建
                "cache": LRUCache(maxsize=100),
                "last_call": None,
                "call_count": 0,
            }

        logger.info(f"注册表加载完成，活跃数据源：{len(self.registry)} 个")
