"""
增强版PostgreSQL关系数据源
集成查询构建器、连接池和数据映射器，完全消除技术债务
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from src.interfaces.relational_data_source import IRelationalDataSource
from .query_builder import QueryExecutor
from .connection_adapter import PostgreSQLConnectionAdapter
from .business_mappers import (
    WatchlistMapper,
    WatchlistSimpleMapper,
    StrategyConfigMapper,
    RiskAlertMapper,
    UserConfigMapper,
    StockBasicInfoMapper,
    IndustryInfoMapper,
    ConceptInfoMapper,
)

logger = logging.getLogger(__name__)


class EnhancedPostgreSQLRelationalDataSource(IRelationalDataSource):
    """
    增强版PostgreSQL关系数据源

    集成了查询构建器、连接池和数据映射器，提供：
    - 统一的查询构建接口
    - 自动化的数据映射
    - 高性能的连接池管理
    - 完全消除的手动数据转换代码
    """

    def __init__(self, connection_pool_size: int = 20):
        """
        初始化增强版PostgreSQL关系数据源

        Args:
            connection_pool_size: 连接池大小
        """
        from src.storage.database.database_manager import (
            DatabaseTableManager,
            DatabaseType,
        )
        from src.monitoring import MonitoringDatabase
        from src.data_access import get_data_access_factory, initialize_data_access

        # 初始化数据库管理器和监控数据库
        db_manager = DatabaseTableManager()
        monitoring_db = MonitoringDatabase()

        # 初始化数据访问工厂
        initialize_data_access(db_manager, monitoring_db)

        # 创建PostgreSQL数据访问实例
        factory = get_data_access_factory()
        self.pg_access = factory.get_data_access(DatabaseType.POSTGRESQL)

        # 初始化连接适配器（使用连接池）
        self.connection_adapter = PostgreSQLConnectionAdapter(db_manager)

        # 初始化查询执行器
        self.query_executor = QueryExecutor(self.connection_adapter)

        # 初始化数据映射器
        self._init_mappers()

        self._connection_pool_size = connection_pool_size
        logger.info("增强版PostgreSQL关系数据源初始化完成 (连接池大小: %s)", connection_pool_size)

    def _init_mappers(self):
        """初始化数据映射器"""
        self.mappers = {
            "watchlist": WatchlistMapper(),
            "watchlist_simple": WatchlistSimpleMapper(),
            "strategy_config": StrategyConfigMapper(),
            "risk_alert": RiskAlertMapper(),
            "user_config": UserConfigMapper(),
            "stock_basic_info": StockBasicInfoMapper(),
            "industry_info": IndustryInfoMapper(),
            "concept_info": ConceptInfoMapper(),
        }

    # ==================== 增强版自选股管理 ====================

    def get_watchlist(
        self, user_id: int, list_type: str = "favorite", include_stock_info: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取自选股列表（增强版）

        使用查询构建器 + 数据映射器，完全消除手动数据转换
        """
        try:
            # 选择合适的映射器
            mapper = self.mappers["watchlist"] if include_stock_info else self.mappers["watchlist_simple"]

            # 构建查询
            query = self.query_executor.create_query()

            if include_stock_info:
                query = (
                    query.select(
                        "w.id",
                        "w.user_id",
                        "w.symbol",
                        "w.list_type",
                        "w.note",
                        "w.added_at",
                        "s.name",
                        "s.industry",
                        "s.market",
                        "s.pinyin",
                    )
                    .from_table("watchlist", "w")
                    .left_join("stock_basic_info s", "w.symbol = s.symbol")
                    .where("w.user_id = %s", user_id)
                    .where("w.list_type = %s", list_type)
                    .order_by("w.added_at", "DESC")
                )
            else:
                query = (
                    query.select("id", "user_id", "symbol", "list_type", "note", "added_at")
                    .from_table("watchlist", "w")
                    .where("w.user_id = %s", user_id)
                    .where("w.list_type = %s", list_type)
                    .order_by("added_at", "DESC")
                )

            # 执行查询
            raw_results = query.fetch_all()

            # 使用映射器进行数据转换
            mapped_results = mapper.map_rows(raw_results)

            logger.info(
                "获取自选股成功 (用户:%s, 类型:%s, 包含股票信息:%s, 数量:%s)"
                % (user_id, list_type, include_stock_info, len(mapped_results))
            )
            return mapped_results

        except Exception as e:
            logger.error("获取自选股失败: %s", e)
            raise

    def add_watchlist(self, user_id: int, symbol: str, list_type: str = "favorite", note: str = "") -> bool:
        """添加自选股（增强版）"""
        try:
            # 构建插入查询
            query = self.query_executor.create_query()
            query = (
                query.insert_into("watchlist")
                .values(
                    {
                        "user_id": user_id,
                        "symbol": symbol,
                        "list_type": list_type,
                        "note": note,
                        "added_at": datetime.now(),
                    }
                )
                .returning("id")
            )

            # 执行查询
            result = query.fetch_one()

            success = bool(result and result.get("id"))
            if success:
                logger.info("添加自选股成功: 用户%s, 股票%s", user_id, symbol)
            else:
                logger.warning("添加自选股失败: 用户%s, 股票%s", user_id, symbol)

            return success

        except Exception as e:
            logger.error("添加自选股失败: %s", e)
            return False

    def update_watchlist(self, user_id: int, symbol: str, note: str = None, list_type: str = None) -> bool:
        """更新自选股（增强版）"""
        try:
            query = self.query_executor.create_query()

            # 构建更新数据
            update_data = {"updated_at": datetime.now()}
            if note is not None:
                update_data["note"] = note
            if list_type is not None:
                update_data["list_type"] = list_type

            query = (
                query.update("watchlist").set(update_data).where("user_id = %s", user_id).where("symbol = %s", symbol)
            )

            # 执行更新
            affected_rows = query.execute()
            success = affected_rows > 0

            if success:
                logger.info("更新自选股成功: 用户%s, 股票%s", user_id, symbol)
            else:
                logger.warning("更新自选股失败，记录不存在: 用户%s, 股票%s", user_id, symbol)

            return success

        except Exception as e:
            logger.error("更新自选股失败: %s", e)
            return False

    def remove_watchlist(self, user_id: int, symbol: str) -> bool:
        """删除自选股（增强版）"""
        try:
            query = self.query_executor.create_query()
            query = query.delete_from("watchlist").where("user_id = %s", user_id).where("symbol = %s", symbol)

            # 执行删除
            affected_rows = query.execute()
            success = affected_rows > 0

            if success:
                logger.info("删除自选股成功: 用户%s, 股票%s", user_id, symbol)
            else:
                logger.warning("删除自选股失败，记录不存在: 用户%s, 股票%s", user_id, symbol)

            return success

        except Exception as e:
            logger.error("删除自选股失败: %s", e)
            return False

    # ==================== 增强版策略配置管理 ====================

    def get_strategy_configs(
        self,
        user_id: int,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """获取策略配置列表（增强版）"""
        try:
            mapper = self.mappers["strategy_config"]
            query = self.query_executor.create_query()

            query = query.select("*").from_table("strategy_configs").where("user_id = %s", user_id)

            if strategy_type:
                query = query.where("strategy_type = %s", strategy_type)
            if status:
                query = query.where("status = %s", status)

            query = query.order_by("created_at", "DESC")

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            logger.info(
                "获取策略配置成功: 用户{user_id}, 类型:{strategy_type}, " f"状态:{status}, 数量:{len(mapped_results)}"
            )
            return mapped_results

        except Exception as e:
            logger.error("获取策略配置失败: %s", e)
            raise

    def create_strategy_config(
        self,
        user_id: int,
        name: str,
        strategy_type: str,
        parameters: Dict[str, Any],
        description: str = "",
    ) -> Optional[int]:
        """创建策略配置（增强版）"""
        try:
            query = self.query_executor.create_query()
            query = (
                query.insert_into("strategy_configs")
                .values(
                    {
                        "user_id": user_id,
                        "name": name,
                        "strategy_type": strategy_type,
                        "parameters": parameters,
                        "description": description,
                        "status": "active",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }
                )
                .returning("id")
            )

            result = query.fetch_one()
            config_id = result.get("id") if result else None

            if config_id:
                logger.info("创建策略配置成功: 配置ID%s, 用户%s", config_id, user_id)
            else:
                logger.error("创建策略配置失败: 用户%s", user_id)

            return config_id

        except Exception as e:
            logger.error("创建策略配置失败: %s", e)
            return None

    def update_strategy_config(
        self,
        config_id: int,
        user_id: int,
        name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        """更新策略配置（增强版）"""
        try:
            query = self.query_executor.create_query()

            # 构建更新数据
            update_data = {"updated_at": datetime.now()}
            if name is not None:
                update_data["name"] = name
            if parameters is not None:
                update_data["parameters"] = parameters
            if description is not None:
                update_data["description"] = description
            if status is not None:
                update_data["status"] = status

            query = (
                query.update("strategy_configs")
                .set(update_data)
                .where("id = %s", config_id)
                .where("user_id = %s", user_id)
            )

            # 执行更新
            affected_rows = query.execute()
            success = affected_rows > 0

            if success:
                logger.info("更新策略配置成功: 配置ID%s", config_id)
            else:
                logger.warning("更新策略配置失败，记录不存在: 配置ID%s", config_id)

            return success

        except Exception as e:
            logger.error("更新策略配置失败: %s", e)
            return False

    def delete_strategy_config(self, config_id: int, user_id: int) -> bool:
        """删除策略配置（增强版）"""
        try:
            query = self.query_executor.create_query()
            query = query.delete_from("strategy_configs").where("id = %s", config_id).where("user_id = %s", user_id)

            # 执行删除
            affected_rows = query.execute()
            success = affected_rows > 0

            if success:
                logger.info("删除策略配置成功: 配置ID%s", config_id)
            else:
                logger.warning("删除策略配置失败，记录不存在: 配置ID%s", config_id)

            return success

        except Exception as e:
            logger.error("删除策略配置失败: %s", e)
            return False

    # ==================== 增强版风险管理配置 ====================

    def get_risk_alerts(
        self,
        user_id: int,
        alert_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """获取风险预警列表（增强版）"""
        try:
            mapper = self.mappers["risk_alert"]
            query = self.query_executor.create_query()

            query = query.select("*").from_table("risk_alerts").where("user_id = %s", user_id)

            if alert_type:
                query = query.where("alert_type = %s", alert_type)
            if status:
                query = query.where("status = %s", status)

            query = query.order_by("created_at", "DESC").limit(limit)

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            logger.info(
                "获取风险预警成功: 用户{user_id}, 类型:{alert_type}, " f"状态:{status}, 数量:{len(mapped_results)}"
            )
            return mapped_results

        except Exception as e:
            logger.error("获取风险预警失败: %s", e)
            raise

    # ==================== 增强版用户配置管理 ====================

    def get_user_config(self, user_id: int, config_key: str) -> Optional[Dict[str, Any]]:
        """获取用户配置（增强版）"""
        try:
            mapper = self.mappers["user_config"]
            query = self.query_executor.create_query()

            query = (
                query.select("*")
                .from_table("user_configs")
                .where("user_id = %s", user_id)
                .where("config_key = %s", config_key)
                .limit(1)
            )

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            if mapped_results:
                config = mapped_results[0]
                logger.info("获取用户配置成功: 用户%s, 配置%s", user_id, config_key)
                return config
            else:
                logger.warning("用户配置不存在: 用户%s, 配置%s", user_id, config_key)
                return None

        except Exception as e:
            logger.error("获取用户配置失败: %s", e)
            return None

    def set_user_config(
        self,
        user_id: int,
        config_key: str,
        config_value: Dict[str, Any],
        description: str = "",
    ) -> bool:
        """设置用户配置（增强版）"""
        try:
            # 先检查配置是否存在
            existing_config = self.get_user_config(user_id, config_key)

            if existing_config:
                # 更新现有配置
                query = self.query_executor.create_query()
                query = (
                    query.update("user_configs")
                    .set(
                        {
                            "config_value": config_value,
                            "description": description,
                            "updated_at": datetime.now(),
                        }
                    )
                    .where("user_id = %s", user_id)
                    .where("config_key = %s", config_key)
                )
            else:
                # 创建新配置
                query = self.query_executor.create_query()
                query = query.insert_into("user_configs").values(
                    {
                        "user_id": user_id,
                        "config_key": config_key,
                        "config_value": config_value,
                        "description": description,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }
                )

            # 执行操作
            affected_rows = query.execute()
            success = affected_rows > 0

            if success:
                action = "更新" if existing_config else "创建"
                logger.info("%s用户配置成功: 用户%s, 配置%s", action, user_id, config_key)
            else:
                logger.error("设置用户配置失败: 用户%s, 配置%s", user_id, config_key)

            return success

        except Exception as e:
            logger.error("设置用户配置失败: %s", e)
            return False

    # ==================== 增强版股票基础信息管理 ====================

    def get_stock_basic_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取股票基础信息（增强版）"""
        try:
            mapper = self.mappers["stock_basic_info"]
            query = self.query_executor.create_query()

            query = query.select("*").from_table("stock_basic_info").where("symbol = %s", symbol).limit(1)

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            if mapped_results:
                stock_info = mapped_results[0]
                logger.info("获取股票基础信息成功: 股票%s", symbol)
                return stock_info
            else:
                logger.warning("股票基础信息不存在: 股票%s", symbol)
                return None

        except Exception as e:
            logger.error("获取股票基础信息失败: %s", e)
            return None

    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索股票（增强版）"""
        try:
            mapper = self.mappers["stock_basic_info"]
            query = self.query_executor.create_query()

            query = (
                query.select("*")
                .from_table("stock_basic_info")
                .where("name ILIKE %s", f"%{keyword}%")
                .or_where("symbol ILIKE %s", f"%{keyword}%")
                .where("is_active = %s", True)
                .order_by("symbol", "ASC")
                .limit(limit)
            )

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            logger.info("搜索股票成功: 关键词%s, 数量%s", keyword, len(mapped_results))
            return mapped_results

        except Exception as e:
            logger.error("搜索股票失败: %s", e)
            return []

    # ==================== 增强版行业概念板块管理 ====================

    def get_industries(self, parent_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取行业列表（增强版）"""
        try:
            mapper = self.mappers["industry_info"]
            query = self.query_executor.create_query()

            query = query.select("*").from_table("industries").where("is_active = %s", True)

            if parent_code:
                query = query.where("parent_code = %s", parent_code)

            query = query.order_by("industry_code", "ASC")

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            logger.info("获取行业列表成功: 父级%s, 数量%s", parent_code, len(mapped_results))
            return mapped_results

        except Exception as e:
            logger.error("获取行业列表失败: %s", e)
            return []

    def get_concepts(self, hot_level_min: int = 0) -> List[Dict[str, Any]]:
        """获取概念板块列表（增强版）"""
        try:
            mapper = self.mappers["concept_info"]
            query = self.query_executor.create_query()

            query = (
                query.select("*")
                .from_table("concepts")
                .where("hot_level >= %s", hot_level_min)
                .order_by("hot_level", "DESC")
                .order_by("concept_name", "ASC")
            )

            # 执行查询并映射结果
            raw_results = query.fetch_all()
            mapped_results = mapper.map_rows(raw_results)

            logger.info("获取概念板块成功: 最小热度%s, 数量%s", hot_level_min, len(mapped_results))
            return mapped_results

        except Exception as e:
            logger.error("获取概念板块失败: %s", e)
            return []

    # ==================== 数据映射器管理方法 ====================

    def get_mapper_info(self) -> Dict[str, Any]:
        """获取映射器信息"""
        return {
            "available_mappers": list(self.mappers.keys()),
            "mapper_count": len(self.mappers),
            "connection_pool_size": self._connection_pool_size,
        }

    def get_connection_pool_info(self) -> Dict[str, Any]:
        """获取连接池信息"""
        return self.connection_adapter.get_pool_info()
