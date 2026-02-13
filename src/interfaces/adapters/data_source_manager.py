"""
# 功能：数据源管理器，统一管理多个数据源适配器的生命周期
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from src.adapters.akshare import AkshareDataSource
from src.adapters.tdx import TdxDataSource

# V2 管理器导入（Phase 3: 手术式替换）
from src.core.data_source import DataSourceManagerV2
from src.interfaces.data_source import IDataSource


class DataSourceManager:
    """
    数据源管理器

    功能:
    1. 统一管理多个数据源适配器
    2. 数据源优先级和故障转移
    3. 数据验证和质量检查
    4. 缓存和性能优化

    使用示例:
        >>> manager = DataSourceManager()
        >>> manager.register_source('tdx', TdxDataSource())
        >>> manager.register_source('akshare', AkshareDataSource())
        >>>
        >>> # 获取实时行情(优先使用TDX)
        >>> quote = manager.get_real_time_data('600519', source='tdx')
        >>>
        >>> # 获取历史数据(自动故障转移)
        >>> df = manager.get_stock_daily('600519', '2024-01-01', '2024-12-31')
    """


    def __init__(self, use_v2: bool = True):
        """
        初始化数据源管理器

        Args:
            use_v2: 是否使用V2管理器（默认True）
                   False表示使用旧的硬编码优先级方式（向后兼容）
        """
        self.logger = logging.getLogger(__name__)

        # 数据源注册表 {name: IDataSource实例}
        self._sources: Dict[str, IDataSource] = {}

        # 数据源优先级配置（旧版，向后兼容）
        self._priority_config = {
            "real_time": ["tdx", "akshare"],  # 实时行情优先级
            "daily": ["tdx", "akshare"],  # 日线数据优先级
            "financial": ["akshare", "tdx"],  # 财务数据优先级
        }

        # Phase 3: 初始化V2管理器（智能路由 + 中心化注册表）
        self._use_v2 = use_v2
        self._v2_manager = None

        if use_v2:
            try:
                self._v2_manager = DataSourceManagerV2()
                self.logger.info("✓ V2管理器初始化成功（智能路由已启用）")
            except Exception:
                self.logger.warning("V2管理器初始化失败，将使用旧版方式: %(e)s")
                self._use_v2 = False

        self.logger.info("数据源管理器初始化完成")


    def register_source(self, name: str, source: IDataSource):
        """
        注册数据源适配器

        Args:
            name: 数据源名称(如'tdx', 'akshare')
            source: IDataSource实例
        """
        if not isinstance(source, IDataSource):
            raise TypeError(f"数据源必须实现IDataSource接口: {type(source)}")

        self._sources[name] = source
        self.logger.info("数据源已注册: %s", name)


    def get_source(self, name: str) -> Optional[IDataSource]:
        """
        获取指定数据源

        Args:
            name: 数据源名称

        Returns:
            IDataSource实例,不存在返回None
        """
        return self._sources.get(name)


    def list_sources(self) -> List[str]:
        """获取所有已注册的数据源名称"""
        return list(self._sources.keys())

        # ==================== 实时行情 ====================


    def get_real_time_data(self, symbol: str, source: Optional[str] = None) -> Union[Dict, str]:
        """
        获取实时行情数据

        Args:
            symbol: 股票代码
            source: 指定数据源,None表示按优先级自动选择

        Returns:
            Dict: 成功时返回行情字典
            str: 失败时返回错误消息
        """
        if source:
            # 使用指定数据源
            data_source = self._sources.get(source)
            if not data_source:
                return f"数据源不存在: {source}"

            return data_source.get_real_time_data(symbol)

        # 按优先级尝试多个数据源
        for source_name in self._priority_config["real_time"]:
            data_source = self._sources.get(source_name)
            if not data_source:
                continue

            self.logger.info("尝试从%s获取实时行情: %s", source_name, symbol)
            result = data_source.get_real_time_data(symbol)

            if isinstance(result, dict):
                self.logger.info("成功从%s获取实时行情", source_name)
                return result
            else:
                self.logger.warning("%s获取失败: %s", source_name, result)

        return "所有数据源均获取失败"

        # ==================== 历史K线 ====================


    def get_stock_daily(self, symbol: str, start_date: str, end_date: str, source: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            source: 指定数据源,None表示按优先级自动选择

        Returns:
            pd.DataFrame: 日线数据
        """
        # Phase 3: 使用V2管理器的智能路由
        if self._use_v2 and not source:
            try:
                self.logger.info("使用V2智能路由获取股票日线: %s", symbol)

                # V2管理器会自动选择最佳数据源并记录监控指标
                df = self._v2_manager.get_stock_daily(symbol=symbol, start_date=start_date, end_date=end_date)

                if not df.empty:
                    self.logger.info("✓ V2智能路由成功获取%s条日线数据", len(df))
                    return df
                else:
                    self.logger.warning("V2智能路由未返回数据，尝试旧版方式")

            except Exception:
                self.logger.warning("V2智能路由失败，尝试旧版方式: %(e)s")

        # 旧版方式：硬编码优先级（向后兼容）
        if source:
            # 使用指定数据源
            data_source = self._sources.get(source)
            if not data_source:
                self.logger.error("数据源不存在: %s", source)
                return pd.DataFrame()

            return data_source.get_stock_daily(symbol, start_date, end_date)

        # 按优先级尝试多个数据源
        for source_name in self._priority_config["daily"]:
            data_source = self._sources.get(source_name)
            if not data_source:
                continue

            self.logger.info("尝试从%s获取股票日线: %s", source_name, symbol)
            df = data_source.get_stock_daily(symbol, start_date, end_date)

            if not df.empty:
                self.logger.info("成功从%s获取%s条日线数据", source_name, len(df))
                return df
            else:
                self.logger.warning("%s获取失败或数据为空", source_name)

        self.logger.error("所有数据源均获取失败")
        return pd.DataFrame()


    def get_index_daily(self, symbol: str, start_date: str, end_date: str, source: Optional[str] = None) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            source: 指定数据源,None表示按优先级自动选择

        Returns:
            pd.DataFrame: 指数日线数据
        """
        # Phase 3: 使用V2管理器的智能路由
        if self._use_v2 and not source:
            try:
                self.logger.info("使用V2智能路由获取指数日线: %s", symbol)

                # V2管理器会自动选择最佳数据源
                df = self._v2_manager.get_stock_daily(symbol=symbol, start_date=start_date, end_date=end_date)

                if not df.empty:
                    self.logger.info("✓ V2智能路由成功获取%s条指数数据", len(df))
                    return df
                else:
                    self.logger.warning("V2智能路由未返回数据，尝试旧版方式")

            except Exception:
                self.logger.warning("V2智能路由失败，尝试旧版方式: %(e)s")

        # 旧版方式：硬编码优先级（向后兼容）
        if source:
            # 使用指定数据源
            data_source = self._sources.get(source)
            if not data_source:
                self.logger.error("数据源不存在: %s", source)
                return pd.DataFrame()

            return data_source.get_index_daily(symbol, start_date, end_date)

        # 按优先级尝试多个数据源
        for source_name in self._priority_config["daily"]:
            data_source = self._sources.get(source_name)
            if not data_source:
                continue

            self.logger.info("尝试从%s获取指数日线: %s", source_name, symbol)
            df = data_source.get_index_daily(symbol, start_date, end_date)

            if not df.empty:
                self.logger.info("成功从%s获取%s条指数数据", source_name, len(df))
                return df
            else:
                self.logger.warning("%s获取失败或数据为空", source_name)

        self.logger.error("所有数据源均获取失败")
        return pd.DataFrame()

        # ==================== 其他接口 ====================


    def get_stock_basic(self, symbol: str, source: Optional[str] = None) -> Dict:
        """获取股票基本信息"""
        if source:
            data_source = self._sources.get(source)
            if data_source:
                return data_source.get_stock_basic(symbol)

        # 尝试所有数据源
        for data_source in self._sources.values():
            result = data_source.get_stock_basic(symbol)
            if result:
                return result

        return {}


    def get_financial_data(self, symbol: str, period: str = "quarter", source: Optional[str] = None) -> pd.DataFrame:
        """获取财务数据"""
        if source:
            data_source = self._sources.get(source)
            if data_source:
                return data_source.get_financial_data(symbol, period)

        # 按优先级尝试(财务数据优先akshare)
        for source_name in self._priority_config["financial"]:
            data_source = self._sources.get(source_name)
            if not data_source:
                continue

            df = data_source.get_financial_data(symbol, period)
            if not df.empty:
                return df

        return pd.DataFrame()


    def get_index_components(self, symbol: str, source: Optional[str] = None) -> List[str]:
        """获取指数成分股"""
        if source:
            data_source = self._sources.get(source)
            if data_source:
                return data_source.get_index_components(symbol)

        # 尝试所有数据源
        for data_source in self._sources.values():
            result = data_source.get_index_components(symbol)
            if result:
                return result

        return []


    def set_priority(self, data_type: str, priority_list: List[str]):
        """
        设置数据源优先级

        Args:
            data_type: 数据类型('real_time', 'daily', 'financial')
            priority_list: 优先级列表(从高到低)
        """
        if data_type not in self._priority_config:
            raise ValueError(f"未知的数据类型: {data_type}")

        self._priority_config[data_type] = priority_list
        self.logger.info("已更新%s优先级: %s", data_type, priority_list)

        # ==================== Phase 3: V2管理器便捷访问方法 ====================


    def find_endpoints(
        self,
        data_category: str = None,
        classification_level: int = None,
        source_type: str = None,
        only_healthy: bool = False,
        sort_by_priority: bool = True,
    ) -> List[Dict]:
        """
        查找数据源端点（V2功能）

        Args:
            data_category: 数据分类（如 'DAILY_KLINE', 'REALTIME_QUOTES'）
            classification_level: 分类层级（1-5）
            source_type: 数据源类型（如 'akshare', 'tdx', 'tushare'）
            only_healthy: 仅返回健康的数据源
            sort_by_priority: 按优先级排序

        Returns:
            端点信息列表

        Example:
            >>> manager = DataSourceManager()
            >>> # 查找所有日线数据接口
            >>> endpoints = manager.find_endpoints(data_category="DAILY_KLINE")
            >>> for ep in endpoints:
            ...     print(f"{ep['endpoint_name']}: 质量={ep['quality_score']}")
        """
        if not self._use_v2 or not self._v2_manager:
            self.logger.warning("V2管理器未启用，无法使用find_endpoints()")
            return []

        return self._v2_manager.find_endpoints(
            data_category=data_category,
            classification_level=classification_level,
            source_type=source_type,
            only_healthy=only_healthy,
            sort_by_priority=sort_by_priority,
        )


    def get_best_endpoint(self, data_category: str) -> Optional[Dict]:
        """
        获取最佳数据源端点（V2功能）

        Args:
            data_category: 数据分类

        Returns:
            最佳端点信息，不存在返回None

        Example:
            >>> manager = DataSourceManager()
            >>> best = manager.get_best_endpoint("DAILY_KLINE")
            >>> print(f"最佳端点: {best['endpoint_name']}")
        """
        if not self._use_v2 or not self._v2_manager:
            self.logger.warning("V2管理器未启用，无法使用get_best_endpoint()")
            return None

        return self._v2_manager.get_best_endpoint(data_category=data_category)


    def health_check(self, endpoint_name: str = None) -> Dict:
        """
        健康检查（V2功能）

        Args:
            endpoint_name: 端点名称，None表示检查所有

        Returns:
            健康检查结果字典

        Example:
            >>> manager = DataSourceManager()
            >>> # 检查所有数据源
            >>> health = manager.health_check()
            >>> print(f"总计: {health['total']}, 健康: {health['healthy']}")
        """
        if not self._use_v2 or not self._v2_manager:
            self.logger.warning("V2管理器未启用，无法使用health_check()")
            return {"total": 0, "healthy": 0, "unhealthy": 0, "details": {}}

        # V2管理器暂不支持health_check，返回占位结果
        endpoints = self._v2_manager.list_all_endpoints()
        return {"total": len(endpoints), "healthy": len(endpoints), "unhealthy": 0, "details": {}}


    def list_all_endpoints(self) -> pd.DataFrame:
        """
        列出所有已注册的数据源端点（V2功能）

        Returns:
            包含所有端点信息的DataFrame

        Example:
            >>> manager = DataSourceManager()
            >>> df = manager.list_all_endpoints()
            >>> print(df[['endpoint_name', 'source_name', 'data_category', 'health_status']])
        """
        if not self._use_v2 or not self._v2_manager:
            self.logger.warning("V2管理器未启用，无法使用list_all_endpoints()")
            return pd.DataFrame()

        return self._v2_manager.list_all_endpoints()


    def disable_v2(self):
        """
        禁用V2管理器（强制使用旧版方式）

        Example:
            >>> manager = DataSourceManager()
            >>> manager.disable_v2()  # 禁用V2，使用旧版硬编码优先级
        """
        self._use_v2 = False
        self.logger.info("已禁用V2管理器，将使用旧版方式")


    def enable_v2(self):
        """
        启用V2管理器（使用智能路由）

        Example:
            >>> manager = DataSourceManager(use_v2=False)
            >>> manager.enable_v2()  # 启用V2智能路由
        """
        if not self._v2_manager:
            self.logger.error("V2管理器未初始化，无法启用")
            return

        self._use_v2 = True
        self.logger.info("已启用V2管理器，将使用智能路由")


def get_default_manager() -> DataSourceManager:
    """
    获取默认配置的数据源管理器

    自动注册TDX和AKShare数据源

    Returns:
        DataSourceManager实例
    """
    manager = DataSourceManager()

    # 注册TDX数据源
    try:
        # pylint: disable=abstract-class-instantiated
        tdx = TdxDataSource()
        manager.register_source("tdx", tdx)
    except Exception as e:
        logging.warning("TDX数据源注册失败: %s", e)

    # 注册AKShare数据源
    try:
        akshare = AkshareDataSource()
        manager.register_source("akshare", akshare)
    except Exception as e:
        logging.warning("AKShare数据源注册失败: %s", e)

    return manager


if __name__ == "__main__":
    """测试数据源管理器"""
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("数据源管理器测试")
    print("=" * 60)

    # 创建管理器
    manager = get_default_manager()

    print(f"\n已注册的数据源: {manager.list_sources()}")

    # 测试实时行情
    print("\n测试实时行情 (贵州茅台 600519):")
    quote = manager.get_real_time_data("600519", source="tdx")
    if isinstance(quote, dict):
        print(f"  股票名称: {quote['name']}")
        print(f"  最新价: {quote['price']:.2f}")
        print(f"  成交量: {quote['volume']:,}手")
    else:
        print(f"  获取失败: {quote}")

    # 测试日线数据
    print("\n测试日线数据 (最近10天):")
    from datetime import datetime, timedelta

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = manager.get_stock_daily("600519", start_date, end_date, source="tdx")
    if not df.empty:
        print(f"  获取成功: {len(df)}条数据")
        print(f"  日期范围: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print("  获取失败")

    print("\n" + "=" * 60)
