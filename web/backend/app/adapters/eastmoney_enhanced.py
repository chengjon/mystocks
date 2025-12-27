"""
EastMoney Enhanced Adapter
Multi-data Source Support

This adapter enhances the existing EastMoneyAdapter with BaseDataSourceAdapter features:
- Health monitoring
- Request statistics
- Standardized interface
- Multi-source integration support
"""

import time
from typing import List, Optional
import pandas as pd
import logging

from app.adapters.base import (
    BaseDataSourceAdapter,
    DataSourceType,
    DataSourceStatus,
    DataSourceConfig,
    DataCategory,
)
from app.adapters.eastmoney_adapter import EastMoneyAdapter

logger = logging.getLogger(__name__)


class EastMoneyEnhancedAdapter(BaseDataSourceAdapter):
    """
    增强版东方财富适配器

    在原有EastMoneyAdapter基础上，集成BaseDataSourceAdapter功能
    提供统一的接口和健康监控
    """

    def __init__(self, config: Optional[DataSourceConfig] = None):
        """
        初始化增强版适配器

        Args:
            config: 数据源配置
        """
        # 使用默认配置
        if config is None:
            config = DataSourceConfig(
                source_type=DataSourceType.EASTMONEY,
                priority=1,
                enabled=True,
                timeout=30,
                retry_count=3,
            )

        super().__init__(config)

        # 创建原始适配器实例
        self._adapter = EastMoneyAdapter()

        logger.info("EastMoneyEnhancedAdapter initialized")

    def get_supported_categories(self) -> List[DataCategory]:
        """
        获取支持的数据类别

        Returns:
            List[DataCategory]: 支持的数据类别
        """
        return [
            DataCategory.REALTIME_QUOTE,
            DataCategory.FUND_FLOW,
            DataCategory.DRAGON_TIGER,
            DataCategory.ETF_DATA,
            DataCategory.SECTOR_DATA,
            DataCategory.DIVIDEND,
            DataCategory.BLOCK_TRADE,
        ]

    def fetch_realtime_quote(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            pd.DataFrame: 实时行情数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            # 东方财富的资金流向API包含实时行情数据
            # 使用fund_flow作为实时行情的数据源
            data = self._adapter.get_stock_fund_flow(symbol=symbols[0] if symbols else None, timeframe="今日")

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.warning("EastMoney returned empty realtime quote data")
                self.update_health_status(DataSourceStatus.DEGRADED, "Returned empty data")

        except Exception as e:
            logger.error(f"Failed to fetch realtime quote from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_fund_flow(self, symbol: Optional[str] = None, timeframe: str = "今日") -> pd.DataFrame:
        """
        获取资金流向

        Args:
            symbol: 股票代码
            timeframe: 时间范围 (今日, 3日, 5日, 10日)

        Returns:
            pd.DataFrame: 资金流向数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_stock_fund_flow(symbol=symbol, timeframe=timeframe)

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.warning(f"EastMoney returned empty fund flow data for {symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch fund flow from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_dragon_tiger(self, date_str: str) -> pd.DataFrame:
        """
        获取龙虎榜

        Args:
            date_str: 日期 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 龙虎榜数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_stock_lhb_detail(date_str=date_str)

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.info(f"No dragon tiger data for {date_str}")

        except Exception as e:
            logger.error(f"Failed to fetch dragon tiger from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_etf_spot(self) -> pd.DataFrame:
        """
        获取ETF实时行情

        Returns:
            pd.DataFrame: ETF实时数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_etf_spot()

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.warning("EastMoney returned empty ETF data")

        except Exception as e:
            logger.error(f"Failed to fetch ETF data from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_sector_fund_flow(self, sector_type: str = "行业", timeframe: str = "今日") -> pd.DataFrame:
        """
        获取板块资金流向

        Args:
            sector_type: 板块类型 (行业, 概念, 地域)
            timeframe: 时间范围 (今日, 3日, 5日, 10日)

        Returns:
            pd.DataFrame: 板块资金流向数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_sector_fund_flow(sector_type=sector_type, timeframe=timeframe)

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.warning(f"EastMoney returned empty sector data for {sector_type}")

        except Exception as e:
            logger.error(f"Failed to fetch sector data from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_dividend(self, symbol: str) -> pd.DataFrame:
        """
        获取分红配送

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 分红配送数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_stock_dividend(symbol=symbol)

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.info(f"No dividend data for {symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch dividend from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_block_trade(self, date_str: Optional[str] = None) -> pd.DataFrame:
        """
        获取大宗交易

        Args:
            date_str: 日期 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 大宗交易数据
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            data = self._adapter.get_stock_blocktrade(date_str=date_str)

            if not data.empty:
                success = True
                self.update_health_status(DataSourceStatus.AVAILABLE)
            else:
                logger.info(f"No block trade data for {date_str}")

        except Exception as e:
            logger.error(f"Failed to fetch block trade from EastMoney: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data


# 全局单例
_eastmoney_enhanced_adapter = None


def get_eastmoney_enhanced_adapter() -> EastMoneyEnhancedAdapter:
    """获取增强版东方财富适配器单例"""
    global _eastmoney_enhanced_adapter
    if _eastmoney_enhanced_adapter is None:
        _eastmoney_enhanced_adapter = EastMoneyEnhancedAdapter()
    return _eastmoney_enhanced_adapter
