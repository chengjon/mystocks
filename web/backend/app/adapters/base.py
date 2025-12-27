"""
Data source adapter base classes and interfaces
Multi-data Source Support

This module provides the foundation for multi-source data integration with:
- Unified data source interface
- Priority and fallback mechanisms
- Data source health monitoring
- Standardized data format
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import pandas as pd
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """数据源类型枚举"""

    AKSHARE = "akshare"  # AKShare数据源（免费）
    EASTMONEY = "eastmoney"  # 东方财富（免费）
    CNINFO = "cninfo"  # 巨潮资讯（免费，官方公告）
    WENCAI = "wencai"  # 问财（免费筛选）
    TQLEX = "tqlex"  # TQLEX（竞价数据）
    LOCAL_DB = "local_db"  # 本地数据库
    CUSTOM = "custom"  # 自定义数据源


class DataSourceStatus(str, Enum):
    """数据源状态枚举"""

    AVAILABLE = "available"  # 可用
    DEGRADED = "degraded"  # 降级（部分功能不可用）
    UNAVAILABLE = "unavailable"  # 不可用
    MAINTENANCE = "maintenance"  # 维护中
    RATE_LIMITED = "rate_limited"  # 请求受限
    ERROR = "error"  # 错误状态


class DataCategory(str, Enum):
    """数据类别枚举"""

    REALTIME_QUOTE = "realtime_quote"  # 实时行情
    HISTORICAL_QUOTE = "historical_quote"  # 历史行情
    FUND_FLOW = "fund_flow"  # 资金流向
    DRAGON_TIGER = "dragon_tiger"  # 龙虎榜
    ANNOUNCEMENT = "announcement"  # 公告
    FINANCIAL_REPORT = "financial_report"  # 财务报告
    DIVIDEND = "dividend"  # 分红配送
    BLOCK_TRADE = "block_trade"  # 大宗交易
    ETF_DATA = "etf_data"  # ETF数据
    SECTOR_DATA = "sector_data"  # 板块数据
    TECHNICAL_INDICATOR = "technical_indicator"  # 技术指标


@dataclass
class DataSourceConfig:
    """数据源配置"""

    source_type: DataSourceType
    priority: int = 1  # 优先级（1最高）
    enabled: bool = True
    timeout: int = 30  # 超时时间（秒）
    retry_count: int = 3  # 重试次数
    rate_limit: Optional[int] = None  # 每分钟请求限制
    api_key: Optional[str] = None  # API密钥
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数


@dataclass
class DataSourceHealthStatus:
    """数据源健康状态"""

    source_type: DataSourceType
    status: DataSourceStatus
    last_check: datetime
    success_rate: float = 0.0  # 成功率 (0-1)
    avg_response_time: float = 0.0  # 平均响应时间（秒）
    error_count: int = 0
    error_message: Optional[str] = None
    supported_categories: List[DataCategory] = field(default_factory=list)


class IDataSource(ABC):
    """
    数据源接口（抽象基类）

    所有数据源适配器必须实现此接口
    提供统一的数据访问接口和健康检查机制
    """

    @abstractmethod
    def get_source_type(self) -> DataSourceType:
        """
        获取数据源类型

        Returns:
            DataSourceType: 数据源类型
        """
        pass

    @abstractmethod
    def get_supported_categories(self) -> List[DataCategory]:
        """
        获取支持的数据类别

        Returns:
            List[DataCategory]: 支持的数据类别列表
        """
        pass

    @abstractmethod
    def check_health(self) -> DataSourceHealthStatus:
        """
        检查数据源健康状态

        Returns:
            DataSourceHealthStatus: 健康状态
        """
        pass

    @abstractmethod
    def fetch_realtime_quote(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            symbols: 股票代码列表，None表示获取全市场

        Returns:
            pd.DataFrame: 实时行情数据
        """
        pass

    @abstractmethod
    def fetch_historical_quote(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "daily",
    ) -> pd.DataFrame:
        """
        获取历史行情

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期 (daily, weekly, monthly)

        Returns:
            pd.DataFrame: 历史行情数据
        """
        pass


class BaseDataSourceAdapter(IDataSource):
    """
    数据源适配器基类

    提供通用功能：
    - 健康检查机制
    - 请求统计
    - 错误处理
    - 日志记录
    """

    def __init__(self, config: DataSourceConfig):
        """
        初始化适配器

        Args:
            config: 数据源配置
        """
        self.config = config
        self._health_status = DataSourceHealthStatus(
            source_type=config.source_type,
            status=DataSourceStatus.AVAILABLE,
            last_check=datetime.now(),
        )
        self._request_count = 0
        self._success_count = 0
        self._error_count = 0
        self._total_response_time = 0.0

        logger.info(f"Initialized {self.config.source_type.value} adapter " f"(priority={self.config.priority})")

    def get_source_type(self) -> DataSourceType:
        """获取数据源类型"""
        return self.config.source_type

    def get_config(self) -> DataSourceConfig:
        """获取配置"""
        return self.config

    def update_health_status(self, status: DataSourceStatus, error_message: Optional[str] = None):
        """
        更新健康状态

        Args:
            status: 新状态
            error_message: 错误信息
        """
        self._health_status.status = status
        self._health_status.last_check = datetime.now()

        if error_message:
            self._health_status.error_message = error_message
            self._health_status.error_count += 1
            logger.warning(
                f"{self.config.source_type.value} health status changed to {status.value}: " f"{error_message}"
            )

    def record_request(self, success: bool, response_time: float):
        """
        记录请求统计

        Args:
            success: 是否成功
            response_time: 响应时间（秒）
        """
        self._request_count += 1
        if success:
            self._success_count += 1
        else:
            self._error_count += 1

        self._total_response_time += response_time

        # 更新成功率和平均响应时间
        if self._request_count > 0:
            self._health_status.success_rate = self._success_count / self._request_count
            self._health_status.avg_response_time = self._total_response_time / self._request_count

    def check_health(self) -> DataSourceHealthStatus:
        """
        检查健康状态

        Returns:
            DataSourceHealthStatus: 当前健康状态
        """
        # 更新支持的数据类别
        self._health_status.supported_categories = self.get_supported_categories()
        self._health_status.last_check = datetime.now()

        return self._health_status

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            Dict: 统计信息
        """
        return {
            "source_type": self.config.source_type.value,
            "total_requests": self._request_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "success_rate": self._health_status.success_rate,
            "avg_response_time": self._health_status.avg_response_time,
            "current_status": self._health_status.status.value,
        }

    def is_available(self) -> bool:
        """
        检查数据源是否可用

        Returns:
            bool: 是否可用
        """
        return self.config.enabled and self._health_status.status in [
            DataSourceStatus.AVAILABLE,
            DataSourceStatus.DEGRADED,
        ]

    def supports_category(self, category: DataCategory) -> bool:
        """
        检查是否支持指定数据类别

        Args:
            category: 数据类别

        Returns:
            bool: 是否支持
        """
        return category in self.get_supported_categories()

    @abstractmethod
    def get_supported_categories(self) -> List[DataCategory]:
        """
        获取支持的数据类别（子类必须实现）

        Returns:
            List[DataCategory]: 支持的数据类别
        """
        pass

    def fetch_realtime_quote(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取实时行情（默认实现，子类可覆盖）

        Args:
            symbols: 股票代码列表

        Returns:
            pd.DataFrame: 实时行情数据
        """
        logger.warning(f"{self.config.source_type.value} does not support realtime_quote")
        return pd.DataFrame()

    def fetch_historical_quote(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "daily",
    ) -> pd.DataFrame:
        """
        获取历史行情（默认实现，子类可覆盖）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期

        Returns:
            pd.DataFrame: 历史行情数据
        """
        logger.warning(f"{self.config.source_type.value} does not support historical_quote")
        return pd.DataFrame()

    def fetch_fund_flow(self, symbol: Optional[str] = None, timeframe: str = "今日") -> pd.DataFrame:
        """
        获取资金流向（可选方法）

        Args:
            symbol: 股票代码
            timeframe: 时间范围

        Returns:
            pd.DataFrame: 资金流向数据
        """
        logger.warning(f"{self.config.source_type.value} does not support fund_flow")
        return pd.DataFrame()

    def fetch_dragon_tiger(self, date_str: str) -> pd.DataFrame:
        """
        获取龙虎榜（可选方法）

        Args:
            date_str: 日期

        Returns:
            pd.DataFrame: 龙虎榜数据
        """
        logger.warning(f"{self.config.source_type.value} does not support dragon_tiger")
        return pd.DataFrame()

    def fetch_announcements(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取公告（可选方法）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            category: 公告类别

        Returns:
            pd.DataFrame: 公告数据
        """
        logger.warning(f"{self.config.source_type.value} does not support announcements")
        return pd.DataFrame()


class DataSourceFactory:
    """
    数据源工厂类

    负责创建和管理数据源适配器实例
    """

    _instances: Dict[DataSourceType, BaseDataSourceAdapter] = {}

    @classmethod
    def create_adapter(
        cls, source_type: DataSourceType, config: Optional[DataSourceConfig] = None
    ) -> BaseDataSourceAdapter:
        """
        创建数据源适配器

        Args:
            source_type: 数据源类型
            config: 配置（可选）

        Returns:
            BaseDataSourceAdapter: 数据源适配器实例
        """
        # 单例模式：如果已存在，直接返回
        if source_type in cls._instances:
            return cls._instances[source_type]

        # 创建默认配置
        if config is None:
            config = DataSourceConfig(source_type=source_type)

        # 根据类型创建相应的适配器
        adapter = None

        if source_type == DataSourceType.EASTMONEY:
            # 注意：需要将现有的EastMoneyAdapter重构为继承BaseDataSourceAdapter
            # 暂时使用wrapper
            adapter = _create_eastmoney_wrapper(config)

        elif source_type == DataSourceType.CNINFO:
            from app.adapters.cninfo_adapter import CninfoAdapter

            adapter = CninfoAdapter(config)

        elif source_type == DataSourceType.WENCAI:
            # WencaiDataSource暂时不继承BaseDataSourceAdapter
            logger.warning("Wencai adapter not yet integrated with BaseDataSourceAdapter")

        else:
            raise ValueError(f"Unsupported data source type: {source_type}")

        if adapter:
            cls._instances[source_type] = adapter
            logger.info(f"Created adapter for {source_type.value}")

        return adapter

    @classmethod
    def get_adapter(cls, source_type: DataSourceType) -> Optional[BaseDataSourceAdapter]:
        """
        获取已创建的适配器

        Args:
            source_type: 数据源类型

        Returns:
            Optional[BaseDataSourceAdapter]: 适配器实例或None
        """
        return cls._instances.get(source_type)

    @classmethod
    def get_all_adapters(cls) -> List[BaseDataSourceAdapter]:
        """
        获取所有已创建的适配器

        Returns:
            List[BaseDataSourceAdapter]: 适配器列表
        """
        return list(cls._instances.values())


def _create_eastmoney_wrapper(config: DataSourceConfig) -> BaseDataSourceAdapter:
    """
    为现有的EastMoneyAdapter创建wrapper
    临时方案，待重构
    """
    # 这里需要创建一个wrapper类来适配现有的EastMoneyAdapter
    # 或者重构EastMoneyAdapter继承BaseDataSourceAdapter
    logger.warning("EastMoney adapter wrapper not yet implemented")
    return None
