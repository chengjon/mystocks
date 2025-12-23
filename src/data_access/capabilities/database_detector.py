"""
数据库特性检测器
动态检测和适配不同数据库的特性
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from ..interfaces.i_data_access import DatabaseType, IDataAccess


class FeatureType(Enum):
    """数据库特性类型"""

    TRANSACTIONS = "transactions"
    CONCURRENT_OPERATIONS = "concurrent_operations"
    INDEX_TYPES = "index_types"
    DATA_TYPES = "data_types"
    QUERY_FEATURES = "query_features"
    PERFORMANCE_FEATURES = "performance_features"
    SCHEMA_FEATURES = "schema_features"
    SECURITY_FEATURES = "security_features"


@dataclass
class DatabaseFeature:
    """数据库特性定义"""

    name: str
    feature_type: FeatureType
    description: str
    version_requirements: Optional[str] = None
    configuration_required: bool = False
    performance_impact: str = "low"  # low, medium, high
    limitation_notes: Optional[str] = None


@dataclass
class CapabilityProfile:
    """数据库能力配置文件"""

    database_type: DatabaseType
    version: str
    supported_features: Dict[FeatureType, List[str]]
    limitations: List[str]
    performance_characteristics: Dict[str, Any]
    configuration_recommendations: Dict[str, Any]


class DatabaseCapabilityDetector:
    """数据库能力检测器"""

    def __init__(self):
        self._capability_cache: Dict[str, CapabilityProfile] = {}
        self._feature_registry = self._initialize_feature_registry()

    def _initialize_feature_registry(self) -> Dict[str, DatabaseFeature]:
        """初始化特性注册表"""
        features = {
            # PostgreSQL 特性
            "postgresql_acid_transactions": DatabaseFeature(
                name="ACID Transactions",
                feature_type=FeatureType.TRANSACTIONS,
                description="完整的ACID事务支持",
                version_requirements=">= 9.0",
                performance_impact="medium",
            ),
            "postgresql_concurrent_operations": DatabaseFeature(
                name="Concurrent Operations",
                feature_type=FeatureType.CONCURRENT_OPERATIONS,
                description="支持并发读写操作",
                version_requirements=">= 9.0",
                performance_impact="high",
            ),
            "postgresql_json_support": DatabaseFeature(
                name="JSON Support",
                feature_type=FeatureType.DATA_TYPES,
                description="原生JSON数据类型支持",
                version_requirements=">= 9.2",
                performance_impact="low",
            ),
            "postgresql_timescaledb": DatabaseFeature(
                name="TimescaleDB Extension",
                feature_type=FeatureType.QUERY_FEATURES,
                description="时序数据库扩展",
                configuration_required=True,
                performance_impact="low",
            ),
            "postgresql_partitioning": DatabaseFeature(
                name="Table Partitioning",
                feature_type=FeatureType.SCHEMA_FEATURES,
                description="表分区功能",
                version_requirements=">= 10.0",
                performance_impact="medium",
            ),
            "postgresql_full_text_search": DatabaseFeature(
                name="Full Text Search",
                feature_type=FeatureType.QUERY_FEATURES,
                description="全文搜索功能",
                version_requirements=">= 9.0",
                performance_impact="medium",
            ),
            # TDengine 特性
            "tdengine_time_series_compression": DatabaseFeature(
                name="Time Series Compression",
                feature_type=FeatureType.PERFORMANCE_FEATURES,
                description="时序数据压缩算法",
                performance_impact="low",
            ),
            "tdengine_super_tables": DatabaseFeature(
                name="Super Tables",
                feature_type=FeatureType.SCHEMA_FEATURES,
                description="超级表功能用于时序数据管理",
                configuration_required=True,
                performance_impact="medium",
            ),
            "tdengine_continuous_queries": DatabaseFeature(
                name="Continuous Queries",
                feature_type=FeatureType.QUERY_FEATURES,
                description="连续查询和流计算功能",
                version_requirements=">= 2.0",
                performance_impact="medium",
            ),
            "tdengine_high_throughput": DatabaseFeature(
                name="High Throughput Write",
                feature_type=FeatureType.PERFORMANCE_FEATURES,
                description="超高写入性能支持",
                performance_impact="low",
            ),
            "tdengine_limited_transactions": DatabaseFeature(
                name="Limited Transactions",
                feature_type=FeatureType.TRANSACTIONS,
                description="有限的事务支持",
                limitation_notes="不支持跨表事务和回滚",
                performance_impact="low",
            ),
            # 通用特性
            "connection_pooling": DatabaseFeature(
                name="Connection Pooling",
                feature_type=FeatureType.PERFORMANCE_FEATURES,
                description="连接池支持",
                performance_impact="high",
            ),
            "batch_operations": DatabaseFeature(
                name="Batch Operations",
                feature_type=FeatureType.PERFORMANCE_FEATURES,
                description="批量操作支持",
                performance_impact="medium",
            ),
            "query_caching": DatabaseFeature(
                name="Query Caching",
                feature_type=FeatureType.PERFORMANCE_FEATURES,
                description="查询结果缓存",
                configuration_required=True,
                performance_impact="medium",
            ),
        }

        return features

    async def detect_capabilities(self, data_access: IDataAccess) -> CapabilityProfile:
        """检测数据库能力"""
        cache_key = self._generate_cache_key(data_access)

        # 检查缓存
        if cache_key in self._capability_cache:
            return self._capability_cache[cache_key]

        # 获取数据库基本信息
        db_info = await data_access.get_database_info()

        # 根据数据库类型检测特性
        if db_info.database_type == DatabaseType.POSTGRESQL:
            profile = await self._detect_postgresql_capabilities(data_access, db_info)
        elif db_info.database_type == DatabaseType.TDENGINE:
            profile = await self._detect_tdengine_capabilities(data_access, db_info)
        else:
            # 默认能力配置
            profile = self._create_default_profile(db_info)

        # 缓存结果
        self._capability_cache[cache_key] = profile
        return profile

    async def _detect_postgresql_capabilities(
        self, data_access: IDataAccess, db_info
    ) -> CapabilityProfile:
        """检测PostgreSQL能力"""
        supported_features = {
            FeatureType.TRANSACTIONS: ["ACID", "Savepoints", "Nested Transactions"],
            FeatureType.CONCURRENT_OPERATIONS: [
                "MVCC",
                "Read Committed",
                "Serializable",
            ],
            FeatureType.INDEX_TYPES: [
                "B-Tree",
                "Hash",
                "GiST",
                "SP-GiST",
                "GIN",
                "BRIN",
            ],
            FeatureType.DATA_TYPES: ["JSON", "JSONB", "Array", "UUID", "Range Types"],
            FeatureType.QUERY_FEATURES: ["CTE", "Window Functions", "LATERAL JOIN"],
            FeatureType.SCHEMA_FEATURES: ["Partitioning", "Inheritance", "Tablespaces"],
            FeatureType.SECURITY_FEATURES: ["Row Level Security", "Column Encryption"],
        }

        # 检查扩展
        extensions = await self._check_postgresql_extensions(data_access)

        if "timescaledb" in extensions:
            supported_features[FeatureType.QUERY_FEATURES].append("TimescaleDB")
            supported_features[FeatureType.DATA_TYPES].append("Hypertables")

        if "pg_trgm" in extensions:
            supported_features[FeatureType.QUERY_FEATURES].append("Trigram Search")

        limitations = ["写入性能受限于单机I/O", "大表查询可能需要优化索引策略"]

        performance_characteristics = {
            "read_throughput": "high",
            "write_throughput": "medium",
            "concurrent_connections": "high",
            "query_complexity_support": "high",
            "memory_usage": "medium",
        }

        return CapabilityProfile(
            database_type=DatabaseType.POSTGRESQL,
            version=db_info.version,
            supported_features=supported_features,
            limitations=limitations,
            performance_characteristics=performance_characteristics,
            configuration_recommendations={
                "work_mem": "64MB",
                "shared_buffers": "25% of RAM",
                "effective_cache_size": "75% of RAM",
                "max_connections": "100-200",
            },
        )

    async def _detect_tdengine_capabilities(
        self, data_access: IDataAccess, db_info
    ) -> CapabilityProfile:
        """检测TDengine能力"""
        supported_features = {
            FeatureType.TRANSACTIONS: ["Limited", "Single Table"],
            FeatureType.CONCURRENT_OPERATIONS: ["High Concurrency"],
            FeatureType.INDEX_TYPES: ["Tag Index", "Timestamp Index"],
            FeatureType.DATA_TYPES: ["Timestamp", "Int", "Float", "Binary", "NChar"],
            FeatureType.QUERY_FEATURES: [
                "Time Series Functions",
                "Super Tables",
                "Continuous Queries",
            ],
            FeatureType.PERFORMANCE_FEATURES: [
                "Compression",
                "High Throughput",
                "Auto Partitioning",
            ],
            FeatureType.SCHEMA_FEATURES: ["Super Tables", "Tags", "Child Tables"],
        }

        limitations = [
            "不支持复杂JOIN操作",
            "事务支持有限",
            "不支持外键约束",
            "数据类型相对有限",
        ]

        performance_characteristics = {
            "read_throughput": "very_high",
            "write_throughput": "very_high",
            "concurrent_connections": "medium",
            "query_complexity_support": "medium",
            "memory_usage": "low",
        }

        return CapabilityProfile(
            database_type=DatabaseType.TDENGINE,
            version=db_info.version,
            supported_features=supported_features,
            limitations=limitations,
            performance_characteristics=performance_characteristics,
            configuration_recommendations={
                "max_connections": "1000",
                "keepalive": "7200",
                "compress": "1",
                "max_batch_insert_rows": "1000",
            },
        )

    def _create_default_profile(self, db_info) -> CapabilityProfile:
        """创建默认能力配置"""
        return CapabilityProfile(
            database_type=db_info.database_type,
            version=db_info.version,
            supported_features={},
            limitations=["未知数据库类型，功能支持有限"],
            performance_characteristics={},
            configuration_recommendations={},
        )

    async def _check_postgresql_extensions(self, data_access: IDataAccess) -> Set[str]:
        """检查PostgreSQL扩展"""
        try:
            query = """
            SELECT extname FROM pg_extension
            WHERE extnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            """

            # 这里需要使用 data_access 的 raw query 方法
            # 实际实现时需要根据具体的 IDataAccess 实现调整
            # result = await data_access.execute_raw_query(query)
            # extensions = {row['extname'] for row in result.data}

            # 暂时返回常见扩展
            return {"plpgsql", "uuid-ossp"}
        except Exception:
            return set()

    def _generate_cache_key(self, data_access: IDataAccess) -> str:
        """生成缓存键"""
        db_type = data_access.get_database_type()
        # 这里应该包含连接信息的哈希，简化处理
        return f"{db_type.value}_default"

    def get_feature_info(self, feature_name: str) -> Optional[DatabaseFeature]:
        """获取特性信息"""
        return self._feature_registry.get(feature_name)

    def list_all_features(self) -> Dict[str, DatabaseFeature]:
        """列出所有注册的特性"""
        return self._feature_registry.copy()

    def is_feature_supported(
        self, profile: CapabilityProfile, feature_name: str
    ) -> bool:
        """检查特性是否支持"""
        if feature_name not in self._feature_registry:
            return False

        feature = self._feature_registry[feature_name]
        return feature.name in profile.supported_features.get(feature.feature_type, [])

    def get_recommendations(
        self, profile: CapabilityProfile, operation_type: str
    ) -> List[str]:
        """获取操作建议"""
        recommendations = []

        if profile.database_type == DatabaseType.POSTGRESQL:
            if operation_type == "bulk_insert":
                recommendations.extend(
                    [
                        "使用COPY命令而不是INSERT",
                        "在事务中批量执行",
                        "考虑临时禁用索引和约束",
                    ]
                )
            elif operation_type == "time_series_query":
                recommendations.extend(
                    [
                        "使用TimescaleDB扩展（如果可用）",
                        "利用分区裁剪",
                        "考虑时序特定函数",
                    ]
                )

        elif profile.database_type == DatabaseType.TDENGINE:
            if operation_type == "time_series_write":
                recommendations.extend(
                    ["使用批量插入", "合理设计超级表的标签", "利用数据压缩特性"]
                )
            elif operation_type == "time_series_query":
                recommendations.extend(
                    ["利用超级表标签过滤", "使用连续查询进行预计算", "考虑数据保留策略"]
                )

        return recommendations

    async def update_capability_cache(self, data_access: IDataAccess):
        """更新能力缓存"""
        cache_key = self._generate_cache_key(data_access)
        if cache_key in self._capability_cache:
            del self._capability_cache[cache_key]

        await self.detect_capabilities(data_access)

    def clear_cache(self):
        """清空能力缓存"""
        self._capability_cache.clear()


class FeatureCompatibilityChecker:
    """特性兼容性检查器"""

    def __init__(self, detector: DatabaseCapabilityDetector):
        self.detector = detector

    async def check_query_compatibility(
        self, query, target_databases: List[DatabaseType]
    ) -> Dict[DatabaseType, bool]:
        """检查查询兼容性"""
        compatibility = {}

        for db_type in target_databases:
            # 这里需要实现查询兼容性检查逻辑
            # 简化处理，假设都兼容
            compatibility[db_type] = True

        return compatibility

    async def suggest_database_for_operation(
        self, operation_type: str, data_characteristics: Dict[str, Any]
    ) -> DatabaseType:
        """为操作建议数据库类型"""
        # 简化的建议逻辑
        if data_characteristics.get("is_time_series", False):
            if data_characteristics.get("write_frequency", "") == "high":
                return DatabaseType.TDENGINE
            else:
                return DatabaseType.POSTGRESQL  # with TimescaleDB
        else:
            return DatabaseType.POSTGRESQL

    async def detect_migration_issues(
        self, source_profile: CapabilityProfile, target_profile: CapabilityProfile
    ) -> List[str]:
        """检测迁移问题"""
        issues = []

        # 检查特性支持差异
        for feature_type in FeatureType:
            source_features = set(
                source_profile.supported_features.get(feature_type, [])
            )
            target_features = set(
                target_profile.supported_features.get(feature_type, [])
            )

            missing_features = source_features - target_features
            if missing_features:
                issues.append(
                    f"目标数据库不支持特性: {feature_type.value}: {missing_features}"
                )

        return issues


# 全局检测器实例
_global_detector = None


def get_global_detector() -> DatabaseCapabilityDetector:
    """获取全局检测器实例"""
    global _global_detector
    if _global_detector is None:
        _global_detector = DatabaseCapabilityDetector()
    return _global_detector
