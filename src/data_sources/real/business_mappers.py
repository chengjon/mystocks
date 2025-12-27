"""
业务数据映射器
为具体的业务实体提供预定义的数据映射配置
"""

import logging

logger = logging.getLogger(__name__)

from .data_mapper import (
    BaseDataMapper,
    FieldMapping,
    FieldType,
    CommonTransformers,
    CommonValidators,
    MapperRegistry,
)


class WatchlistMapper(BaseDataMapper):
    """自选股数据映射器"""

    def __init__(self):
        """初始化自选股映射器"""
        field_mappings = [
            FieldMapping(
                source_field=0,
                target_field="id",
                field_type=FieldType.INTEGER,
                required=True,
                description="自选股记录ID",
            ),
            FieldMapping(
                source_field=1,
                target_field="user_id",
                field_type=FieldType.INTEGER,
                required=True,
                validator=CommonValidators.positive_number(),
                description="用户ID",
            ),
            FieldMapping(
                source_field=2,
                target_field="symbol",
                field_type=FieldType.STRING,
                required=True,
                transformer=CommonTransformers.safe_string(),
                description="股票代码",
            ),
            FieldMapping(
                source_field=3,
                target_field="list_type",
                field_type=FieldType.STRING,
                required=True,
                transformer=CommonTransformers.safe_string(),
                default_value="favorite",
                description="列表类型",
            ),
            FieldMapping(
                source_field=4,
                target_field="note",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
                default_value="",
                description="备注",
            ),
            FieldMapping(
                source_field=5,
                target_field="added_at",
                field_type=FieldType.DATETIME,
                required=True,
                transformer=CommonTransformers.datetime_formatter(),
                description="添加时间",
            ),
            FieldMapping(
                source_field=6,
                target_field="name",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
                description="股票名称",
            ),
            FieldMapping(
                source_field=7,
                target_field="industry",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
                description="所属行业",
            ),
            FieldMapping(
                source_field=8,
                target_field="market",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
                description="交易市场",
            ),
            FieldMapping(
                source_field=9,
                target_field="pinyin",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
                description="股票拼音",
            ),
        ]
        super().__init__(field_mappings)


class WatchlistSimpleMapper(BaseDataMapper):
    """简单自选股映射器（不包含股票信息）"""

    def __init__(self):
        """初始化简单自选股映射器"""
        field_mappings = [
            FieldMapping(
                source_field=0,
                target_field="id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=1,
                target_field="user_id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=2,
                target_field="symbol",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field=3,
                target_field="list_type",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field=4,
                target_field="note",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field=5,
                target_field="added_at",
                field_type=FieldType.DATETIME,
                required=True,
                transformer=CommonTransformers.datetime_formatter(),
            ),
        ]
        super().__init__(field_mappings)


class StrategyConfigMapper(BaseDataMapper):
    """策略配置映射器"""

    def __init__(self):
        """初始化策略配置映射器"""
        field_mappings = [
            FieldMapping(
                source_field=0,
                target_field="id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=1,
                target_field="user_id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=2,
                target_field="name",
                field_type=FieldType.STRING,
                required=True,
                validator=CommonValidators.not_empty(),
            ),
            FieldMapping(
                source_field=3,
                target_field="strategy_type",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field=4,
                target_field="status",
                field_type=FieldType.STRING,
                required=True,
                default_value="active",
            ),
            FieldMapping(
                source_field=5,
                target_field="parameters",
                field_type=FieldType.JSON,
                default_value={},
            ),
            FieldMapping(
                source_field=6,
                target_field="description",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field=7,
                target_field="created_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
            FieldMapping(
                source_field=8,
                target_field="updated_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
        ]
        super().__init__(field_mappings)


class RiskAlertMapper(BaseDataMapper):
    """风险预警映射器"""

    def __init__(self):
        """初始化风险预警映射器"""
        field_mappings = [
            FieldMapping(
                source_field=0,
                target_field="id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=1,
                target_field="user_id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=2,
                target_field="symbol",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field=3,
                target_field="alert_type",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field=4,
                target_field="status",
                field_type=FieldType.STRING,
                required=True,
                default_value="pending",
            ),
            FieldMapping(
                source_field=5,
                target_field="message",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field=6,
                target_field="priority",
                field_type=FieldType.STRING,
                default_value="medium",
            ),
            FieldMapping(
                source_field=7,
                target_field="threshold_value",
                field_type=FieldType.FLOAT,
                transformer=CommonTransformers.safe_float(),
            ),
            FieldMapping(
                source_field=8,
                target_field="current_value",
                field_type=FieldType.FLOAT,
                transformer=CommonTransformers.safe_float(),
            ),
            FieldMapping(
                source_field=9,
                target_field="created_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
        ]
        super().__init__(field_mappings)


class UserConfigMapper(BaseDataMapper):
    """用户配置映射器"""

    def __init__(self):
        """初始化用户配置映射器"""
        field_mappings = [
            FieldMapping(
                source_field=0,
                target_field="id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=1,
                target_field="user_id",
                field_type=FieldType.INTEGER,
                required=True,
            ),
            FieldMapping(
                source_field=2,
                target_field="config_key",
                field_type=FieldType.STRING,
                required=True,
                validator=CommonValidators.not_empty(),
            ),
            FieldMapping(
                source_field=3,
                target_field="config_value",
                field_type=FieldType.JSON,
                default_value={},
            ),
            FieldMapping(
                source_field=4,
                target_field="description",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field=5,
                target_field="created_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
            FieldMapping(
                source_field=6,
                target_field="updated_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
        ]
        super().__init__(field_mappings)


class StockBasicInfoMapper(BaseDataMapper):
    """股票基础信息映射器"""

    def __init__(self):
        """初始化股票基础信息映射器"""
        field_mappings = [
            FieldMapping(
                source_field="symbol",
                target_field="symbol",
                field_type=FieldType.STRING,
                required=True,
                validator=CommonValidators.not_empty(),
            ),
            FieldMapping(
                source_field="name",
                target_field="name",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="industry",
                target_field="industry",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="market",
                target_field="market",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="pinyin",
                target_field="pinyin",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="listing_date",
                target_field="listing_date",
                field_type=FieldType.DATE,
            ),
            FieldMapping(
                source_field="total_shares",
                target_field="total_shares",
                field_type=FieldType.FLOAT,
                transformer=CommonTransformers.safe_float(),
            ),
            FieldMapping(
                source_field="float_shares",
                target_field="float_shares",
                field_type=FieldType.FLOAT,
                transformer=CommonTransformers.safe_float(),
            ),
            FieldMapping(
                source_field="is_active",
                target_field="is_active",
                field_type=FieldType.BOOLEAN,
                transformer=CommonTransformers.bool_converter(),
                default_value=True,
            ),
        ]
        super().__init__(field_mappings)


class IndustryInfoMapper(BaseDataMapper):
    """行业信息映射器"""

    def __init__(self):
        """初始化行业信息映射器"""
        field_mappings = [
            FieldMapping(
                source_field="industry_code",
                target_field="industry_code",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field="industry_name",
                target_field="industry_name",
                field_type=FieldType.STRING,
                required=True,
                validator=CommonValidators.not_empty(),
            ),
            FieldMapping(
                source_field="parent_code",
                target_field="parent_code",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="level",
                target_field="level",
                field_type=FieldType.INTEGER,
                transformer=CommonTransformers.safe_int(1),
            ),
            FieldMapping(
                source_field="description",
                target_field="description",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="is_active",
                target_field="is_active",
                field_type=FieldType.BOOLEAN,
                transformer=CommonTransformers.bool_converter(),
                default_value=True,
            ),
        ]
        super().__init__(field_mappings)


class ConceptInfoMapper(BaseDataMapper):
    """概念板块映射器"""

    def __init__(self):
        """初始化概念板块映射器"""
        field_mappings = [
            FieldMapping(
                source_field="concept_code",
                target_field="concept_code",
                field_type=FieldType.STRING,
                required=True,
            ),
            FieldMapping(
                source_field="concept_name",
                target_field="concept_name",
                field_type=FieldType.STRING,
                required=True,
                validator=CommonValidators.not_empty(),
            ),
            FieldMapping(
                source_field="description",
                target_field="description",
                field_type=FieldType.STRING,
                transformer=CommonTransformers.safe_string(),
            ),
            FieldMapping(
                source_field="related_stocks",
                target_field="related_stocks",
                field_type=FieldType.JSON,
                default_value=[],
            ),
            FieldMapping(
                source_field="hot_level",
                target_field="hot_level",
                field_type=FieldType.INTEGER,
                transformer=CommonTransformers.safe_int(0),
            ),
            FieldMapping(
                source_field="created_at",
                target_field="created_at",
                field_type=FieldType.DATETIME,
                transformer=CommonTransformers.datetime_formatter(),
            ),
        ]
        super().__init__(field_mappings)


def register_all_mappers():
    """注册所有业务映射器"""
    # 注册业务映射器
    MapperRegistry.register_mapper("watchlist", WatchlistMapper())
    MapperRegistry.register_mapper("watchlist_simple", WatchlistSimpleMapper())
    MapperRegistry.register_mapper("strategy_config", StrategyConfigMapper())
    MapperRegistry.register_mapper("risk_alert", RiskAlertMapper())
    MapperRegistry.register_mapper("user_config", UserConfigMapper())
    MapperRegistry.register_mapper("stock_basic_info", StockBasicInfoMapper())
    MapperRegistry.register_mapper("industry_info", IndustryInfoMapper())
    MapperRegistry.register_mapper("concept_info", ConceptInfoMapper())

    logger.info("所有业务数据映射器已注册")


# 预定义的映射器实例
WATCHLIST_MAPPER = WatchlistMapper()
WATCHLIST_SIMPLE_MAPPER = WatchlistSimpleMapper()
STRATEGY_CONFIG_MAPPER = StrategyConfigMapper()
RISK_ALERT_MAPPER = RiskAlertMapper()
USER_CONFIG_MAPPER = UserConfigMapper()
STOCK_BASIC_INFO_MAPPER = StockBasicInfoMapper()
INDUSTRY_INFO_MAPPER = IndustryInfoMapper()
CONCEPT_INFO_MAPPER = ConceptInfoMapper()

# 映射器别名，便于使用
WATCHLIST = WATCHLIST_MAPPER
WATCHLIST_SIMPLE = WATCHLIST_SIMPLE_MAPPER
STRATEGY = STRATEGY_CONFIG_MAPPER
RISK_ALERT = RISK_ALERT_MAPPER
USER_CONFIG = USER_CONFIG_MAPPER
STOCK_INFO = STOCK_BASIC_INFO_MAPPER
INDUSTRY = INDUSTRY_INFO_MAPPER
CONCEPT = CONCEPT_INFO_MAPPER
