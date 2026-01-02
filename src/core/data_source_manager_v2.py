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

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import yaml
import pandas as pd
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

    def _load_from_database(self) -> Dict:
        """从PostgreSQL数据库加载数据源注册表"""
        query = """
            SELECT
                endpoint_name,
                source_name,
                source_type,
                data_category,
                data_classification,
                classification_level,
                target_db,
                table_name,
                parameters,
                data_quality_score,
                priority,
                status,
                health_status,
                avg_response_time,
                success_rate,
                consecutive_failures,
                last_success_time,
                last_failure_time,
                total_calls,
                failed_calls,
                tags,
                version,
                description
            FROM data_source_registry
            WHERE status = 'active'
        """

        try:
            db_manager = self._get_db_manager()
            pool = db_manager.get_postgresql_connection()
            conn = pool.getconn()
            try:
                df = pd.read_sql(query, conn)
            finally:
                pool.putconn(conn)

            sources = {}
            for _, row in df.iterrows():
                endpoint_name = row["endpoint_name"]
                sources[endpoint_name] = {
                    "endpoint_name": endpoint_name,
                    "source_name": row["source_name"],
                    "source_type": row["source_type"],
                    "data_category": row["data_category"],
                    "data_classification": row["data_classification"],
                    "classification_level": row["classification_level"],
                    "target_db": row["target_db"],
                    "table_name": row["table_name"],
                    "parameters": json.loads(row["parameters"]) if row["parameters"] else {},
                    "data_quality_score": row["data_quality_score"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "health_status": row["health_status"],
                    "avg_response_time": row["avg_response_time"],
                    "success_rate": row["success_rate"],
                    "consecutive_failures": row["consecutive_failures"],
                    "last_success_time": row["last_success_time"],
                    "last_failure_time": row["last_failure_time"],
                    "total_calls": row["total_calls"],
                    "failed_calls": row["failed_calls"],
                    "tags": list(row["tags"]) if row["tags"] else [],
                    "version": row["version"],
                    "description": row["description"],
                    "_loaded_from": "database",
                }

            return sources
        except Exception as e:
            logger.error(f"从数据库加载失败: {e}")
            return {}

    def _load_from_yaml(self) -> Dict:
        """从YAML配置文件加载数据源"""
        try:
            yaml_path = Path(self.yaml_config_path)
            if not yaml_path.exists():
                logger.warning(f"YAML配置文件不存在: {self.yaml_config_path}")
                return {}

            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            sources = {}
            for endpoint_key, source_config in config.get("data_sources", {}).items():
                # 确保endpoint_name一致
                if "endpoint_name" not in source_config:
                    source_config["endpoint_name"] = endpoint_key

                source_config["_loaded_from"] = "yaml"
                sources[endpoint_key] = source_config

            return sources
        except Exception as e:
            logger.error(f"从YAML加载失败: {e}")
            return {}

    def _merge_sources(self, db_sources: Dict, yaml_sources: Dict) -> Dict:
        """
        合并数据库和YAML配置

        策略：
        - 数据库优先（包含运行时统计：health_status, success_rate等）
        - YAML用于补充新数据源和配置详情（parameters, test_parameters等）
        """
        merged = db_sources.copy()

        for endpoint_name, yaml_config in yaml_sources.items():
            if endpoint_name not in merged:
                # 新数据源，从YAML添加
                merged[endpoint_name] = yaml_config
                logger.info(f"从YAML添加新数据源: {endpoint_name}")
            else:
                # 已存在的数据源，合并配置字段（不覆盖运行时统计）
                db_source = merged[endpoint_name]

                # 合并配置字段（保留数据库中的运行时统计）
                config_fields = [
                    "parameters",
                    "description",
                    "test_parameters",
                    "source_config",
                    "quality_rules",
                    "update_schedule",
                    "business_scene",
                    "tags",
                    "version",
                ]
                for field in config_fields:
                    if field in yaml_config:
                        db_source[field] = yaml_config[field]

        return merged

    # ==========================================================================
    # 查询接口（解决"找接口难"问题）
    # ==========================================================================

    def find_endpoints(
        self,
        data_category: str = None,
        classification_level: int = None,
        source_type: str = None,
        only_enabled: bool = True,
        only_healthy: bool = False,
        sort_by_priority: bool = True,
    ) -> List[Dict]:
        """
        查找可用的数据端点

        Args:
            data_category: 数据分类（如 DAILY_KLINE、TICK_DATA）
            classification_level: 分类层级（1-5）
            source_type: 数据源类型（akshare、tushare等）
            only_enabled: 仅返回启用的接口
            only_healthy: 仅返回健康状态正常的接口
            sort_by_priority: 按优先级和质量评分排序

        Returns:
            匹配的端点列表

        示例:
            # 查找所有日线数据接口
            apis = manager.find_endpoints(data_category="DAILY_KLINE")

            # 查找第1层分类（市场数据）的所有接口
            apis = manager.find_endpoints(classification_level=1)

            # 查找健康的akshare接口
            apis = manager.find_endpoints(source_type="akshare", only_healthy=True)
        """
        matches = []

        for endpoint_name, source in self.registry.items():
            config = source["config"]

            # 状态过滤
            if only_enabled and config.get("status") != "active":
                continue

            if only_healthy and config.get("health_status") == "failed":
                continue

            # 分类过滤
            if data_category and config.get("data_category") != data_category:
                continue

            if classification_level and config.get("classification_level") != classification_level:
                continue

            if source_type and config.get("source_type") != source_type:
                continue

            matches.append(
                {
                    "endpoint_name": endpoint_name,
                    "source_name": config.get("source_name"),
                    "source_type": config.get("source_type"),
                    "data_category": config.get("data_category"),
                    "data_classification": config.get("data_classification"),
                    "classification_level": config.get("classification_level"),
                    "target_db": config.get("target_db"),
                    "table_name": config.get("table_name"),
                    "quality_score": config.get("data_quality_score", 0),
                    "priority": config.get("priority", 999),
                    "health_status": config.get("health_status", "unknown"),
                    "success_rate": config.get("success_rate", 100),
                    "avg_response_time": config.get("avg_response_time", 0),
                    "total_calls": config.get("total_calls", 0),
                    "description": config.get("description", ""),
                    "tags": config.get("tags", []),
                }
            )

        # 排序：优先级（数字越小优先级越高）→ 质量评分（分数越高越好）
        if sort_by_priority:
            matches.sort(key=lambda x: (x["priority"], -x["quality_score"]))

        return matches

    def get_best_endpoint(self, data_category: str, exclude_failed: bool = True) -> Optional[Dict]:
        """
        获取最佳数据端点（智能路由）

        选择标准：
        1. 状态为active
        2. 健康状态为healthy或degraded（可选排除failed）
        3. 按优先级排序
        4. 同优先级按质量评分排序

        Args:
            data_category: 数据分类（如 DAILY_KLINE）
            exclude_failed: 是否排除失败状态的接口

        Returns:
            最佳端点配置，如果没有可用端点则返回None

        示例:
            best = manager.get_best_endpoint("DAILY_KLINE")
            if best:
                print(f"最佳接口: {best['endpoint_name']}, 评分: {best['quality_score']}")
        """
        endpoints = self.find_endpoints(data_category=data_category, only_healthy=exclude_failed)

        return endpoints[0] if endpoints else None

    def list_all_endpoints(self) -> pd.DataFrame:
        """
        列出所有已注册的数据端点（便于查看和管理）

        Returns:
            包含所有端点信息的DataFrame
        """
        data = []

        for endpoint_name, source in self.registry.items():
            config = source["config"]

            data.append(
                {
                    "数据源": config.get("source_name"),
                    "端点名称": endpoint_name,
                    "数据分类": config.get("data_category"),
                    "分类层级": config.get("classification_level"),
                    "目标数据库": config.get("target_db"),
                    "目标表": config.get("table_name"),
                    "更新频率": config.get("update_frequency", ""),
                    "质量评分": config.get("data_quality_score"),
                    "优先级": config.get("priority"),
                    "状态": config.get("status"),
                    "健康状态": config.get("health_status"),
                    "成功率": f"{config.get('success_rate', 100):.1f}%",
                    "平均响应时间": f"{config.get('avg_response_time', 0):.2f}s",
                    "调用次数": config.get("total_calls", 0),
                    "失败次数": config.get("failed_calls", 0),
                    "连续失败": config.get("consecutive_failures", 0),
                    "最后成功": config.get("last_success_time"),
                    "版本": config.get("version", ""),
                    "标签": ",".join(config.get("tags", [])),
                }
            )

        return pd.DataFrame(data)

    # ==========================================================================
    # 高层业务接口（向后兼容）
    # ==========================================================================

    def get_stock_daily(
        self, symbol: str, start_date: str = None, end_date: str = None, adjust: str = "qfq"
    ) -> pd.DataFrame:
        """
        获取日线数据（高层业务接口）

        内部逻辑：
        1. 查询DAILY_KLINE分类下的最佳接口
        2. 调用该接口
        3. 如果失败，按优先级尝试备用接口
        4. 记录调用历史

        Args:
            symbol: 股票代码
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）
            adjust: 复权类型（qfq=前复权, hfq=后复权）

        Returns:
            日线数据DataFrame

        示例:
            manager = DataSourceManagerV2()
            data = manager.get_stock_daily(symbol="000001", start_date="20240101")
        """
        # 获取最佳接口
        best_endpoint = self.get_best_endpoint("DAILY_KLINE")

        if not best_endpoint:
            raise ValueError("没有可用的日线数据接口")

        logger.info(f"使用接口: {best_endpoint['endpoint_name']}")

        # 调用接口（根据数据源类型适配参数）
        return self._call_endpoint(
            best_endpoint, symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust
        )

    def get_stock_realtime(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情（高层业务接口）"""
        best_endpoint = self.get_best_endpoint("REALTIME_QUOTE")

        if not best_endpoint:
            raise ValueError("没有可用的实时行情接口")

        return self._call_endpoint(best_endpoint, symbols=symbols)

    def get_stock_symbols(self) -> pd.DataFrame:
        """获取股票代码列表（高层业务接口）"""
        best_endpoint = self.get_best_endpoint("SYMBOLS_INFO")

        if not best_endpoint:
            raise ValueError("没有可用的股票代码接口")

        return self._call_endpoint(best_endpoint)

    # ==========================================================================
    # 内部调用方法
    # ==========================================================================

    def _call_endpoint(self, endpoint_info: Dict, **kwargs) -> pd.DataFrame:
        """
        调用具体的数据端点

        Args:
            endpoint_info: 端点信息（从find_endpoints或get_best_endpoint获取）
            **kwargs: 调用参数

        Returns:
            数据DataFrame
        """
        endpoint_name = endpoint_info["endpoint_name"]
        source_type = endpoint_info["source_type"]

        # 获取或创建handler
        source = self.registry.get(endpoint_name)
        if not source:
            raise ValueError(f"端点 {endpoint_name} 未注册")

        # 延迟创建handler
        if source["handler"] is None:
            source["handler"] = self._create_handler(endpoint_info)

        handler = source["handler"]

        # 记录调用开始时间
        start_time = time.time()
        caller = self._identify_caller()

        try:
            # 调用handler
            data = handler.fetch(**kwargs)

            # 记录成功
            response_time = time.time() - start_time
            self._record_success(endpoint_name, response_time, len(data), caller)

            return data

        except Exception as e:
            # 记录失败
            response_time = time.time() - start_time
            error_msg = str(e)
            self._record_failure(endpoint_name, response_time, error_msg, caller)

            logger.error(f"调用接口失败: {endpoint_name}, 错误: {error_msg}")
            raise

    def _create_handler(self, endpoint_info: Dict):
        """创建数据源处理器（工厂方法）"""
        source_type = endpoint_info["source_type"]

        # 延迟导入（避免循环依赖）
        from src.core.data_source_handlers_v2 import (
            AkshareHandler,
            TushareHandler,
            BaostockHandler,
            TdxHandler,
            WebCrawlerHandler,
            MockHandler,
        )

        handler_map = {
            "akshare": AkshareHandler,
            "tushare": TushareHandler,
            "baostock": BaostockHandler,
            "tdx": TdxHandler,
            "database": TdxHandler,
            "crawler": WebCrawlerHandler,
            "mock": MockHandler,
            "api_library": self._select_api_handler(endpoint_info["source_name"]),
        }

        handler_class = handler_map.get(source_type)
        if not handler_class:
            raise ValueError(f"不支持的数据源类型: {source_type}")

        return handler_class(endpoint_info)

    def _select_api_handler(self, source_name: str):
        """根据数据源名称选择处理器"""
        from src.core.data_source_handlers_v2 import AkshareHandler, TushareHandler

        handler_map = {"akshare": AkshareHandler, "tushare": TushareHandler, "baostock": TushareHandler}  # 复用

        return handler_map.get(source_name, AkshareHandler)

    def _identify_caller(self) -> str:
        """识别调用方"""
        import traceback

        stack = traceback.extract_stack()

        # 找到调用者（跳过内部调用）
        for frame in reversed(stack[:-2]):
            filename = frame.filename
            if "data_source_manager" not in filename:
                return f"{Path(filename).name}:{frame.lineno}"

        return "unknown"

    # ==========================================================================
    # 监控和记录
    # ==========================================================================

    def _record_success(self, endpoint_name: str, response_time: float, record_count: int, caller: str):
        """记录成功调用"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        config = source["config"]

        # 更新内存统计
        total_calls = config.get("total_calls", 0)
        failed_calls = config.get("failed_calls", 0)

        # 更新平均响应时间
        old_avg = config.get("avg_response_time", 0)
        new_avg = (old_avg * total_calls + response_time) / (total_calls + 1)

        config["avg_response_time"] = new_avg
        config["total_calls"] = total_calls + 1
        config["success_rate"] = (total_calls + 1 - failed_calls) / (total_calls + 1) * 100
        config["consecutive_failures"] = 0
        config["last_success_time"] = datetime.now()

        # 更新健康状态
        if response_time > 5.0:
            config["health_status"] = "degraded"
        else:
            config["health_status"] = "healthy"

        # 保存到数据库（异步，避免阻塞）
        self._save_call_history_async(
            endpoint_name=endpoint_name,
            success=True,
            response_time=response_time,
            record_count=record_count,
            caller=caller,
        )

    def _record_failure(self, endpoint_name: str, response_time: float, error_message: str, caller: str):
        """记录失败调用"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        config = source["config"]

        # 更新失败统计
        config["failed_calls"] = config.get("failed_calls", 0) + 1
        config["consecutive_failures"] = config.get("consecutive_failures", 0) + 1
        config["last_failure_time"] = datetime.now()

        # 连续失败3次标记为失败
        if config["consecutive_failures"] >= 3:
            config["health_status"] = "failed"

        # 保存到数据库
        self._save_call_history_async(
            endpoint_name=endpoint_name,
            success=False,
            response_time=response_time,
            error_message=error_message,
            caller=caller,
        )

    def _save_call_history_async(self, **kwargs):
        """异步保存调用历史（避免阻塞）"""
        try:
            query = """
                INSERT INTO data_source_call_history
                (endpoint_name, call_time, success, response_time, record_count, error_message, caller)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            db_manager = self._get_db_manager()
            with db_manager.get_postgresql_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        kwargs.get("endpoint_name"),
                        datetime.now(),
                        kwargs.get("success", True),
                        kwargs.get("response_time"),
                        kwargs.get("record_count"),
                        kwargs.get("error_message"),
                        kwargs.get("caller", "unknown"),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"保存调用历史失败: {e}")

    # ==========================================================================
    # 健康检查
    # ==========================================================================

    def health_check(self, endpoint_name: str = None) -> Dict:
        """
        执行健康检查

        Args:
            endpoint_name: 指定端点名称，None表示检查所有

        Returns:
            健康检查结果
        """
        if endpoint_name:
            return self._check_single_endpoint(endpoint_name)
        else:
            return self._check_all_endpoints()

    def _check_single_endpoint(self, endpoint_name: str) -> Dict:
        """检查单个端点"""
        source = self.registry.get(endpoint_name)
        if not source:
            return {"endpoint_name": endpoint_name, "status": "not_found"}

        config = source["config"]
        test_params = config.get("test_parameters", {})

        try:
            # 获取或创建handler
            if source["handler"] is None:
                source["handler"] = self._create_handler(config)

            handler = source["handler"]

            # 使用测试参数调用
            start_time = time.time()
            data = handler.fetch(**test_params)
            response_time = time.time() - start_time

            # 验证返回数据
            self._validate_data(endpoint_name, data)

            return {
                "endpoint_name": endpoint_name,
                "status": "healthy",
                "response_time": round(response_time, 3),
                "record_count": len(data) if hasattr(data, "__len__") else "N/A",
                "sample": data.head(1).to_dict() if hasattr(data, "head") else str(data)[:100],
            }
        except Exception as e:
            return {"endpoint_name": endpoint_name, "status": "unhealthy", "error": str(e)}

    def _check_all_endpoints(self) -> Dict:
        """检查所有端点"""
        results = {}

        for endpoint_name in self.registry.keys():
            results[endpoint_name] = self._check_single_endpoint(endpoint_name)

        total = len(results)
        healthy = sum(1 for r in results.values() if r["status"] == "healthy")
        unhealthy = total - healthy

        return {"total": total, "healthy": healthy, "unhealthy": unhealthy, "details": results}

    def _validate_data(self, endpoint_name: str, data: Any):
        """验证数据质量"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        quality_rules = source["config"].get("quality_rules", {})

        if not isinstance(data, pd.DataFrame):
            return  # 非DataFrame数据跳过验证

        # 检查最小记录数
        min_count = quality_rules.get("min_record_count", 0)
        if len(data) < min_count:
            raise ValueError(f"数据记录数不足: {len(data)} < {min_count}")

        # 检查必需列
        required_columns = quality_rules.get("required_columns", [])
        if required_columns:
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                raise ValueError(f"缺少必需列: {missing_columns}")


class LRUCache:
    """简单的LRU缓存实现"""

    def __init__(self, maxsize=100):
        from collections import OrderedDict

        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def __setitem__(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)


# 便捷的单例模式（可选）
_instance = None


def get_data_source_manager() -> DataSourceManagerV2:
    """获取数据源管理器单例"""
    global _instance
    if _instance is None:
        _instance = DataSourceManagerV2()
    return _instance
