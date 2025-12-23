"""
关系数据源抽象接口

本模块定义关系数据源的统一接口，所有关系数据源（Mock、PostgreSQL等）必须实现此接口。
关系数据主要包括：自选股配置、策略参数、用户设置、风险配置等结构化关系数据。

适用数据库: PostgreSQL (关系型数据库)
适用场景: 用户配置、策略管理、系统设置

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class IRelationalDataSource(ABC):
    """
    关系数据源抽象接口

    所有关系数据源实现必须遵循此接口规范，确保：
    1. 方法签名一致
    2. 返回数据格式统一
    3. 支持事务操作
    4. 异常处理规范

    实现类:
    - MockRelationalDataSource: Mock数据实现（开发测试）
    - PostgreSQLRelationalDataSource: PostgreSQL数据库实现（生产）
    """

    # ==================== 自选股管理 ====================

    @abstractmethod
    def get_watchlist(
        self, user_id: int, list_type: str = "favorite", include_stock_info: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取自选股列表

        Args:
            user_id: 用户ID
            list_type: 列表类型
                      - "favorite": 自选股
                      - "strategy": 策略选股
                      - "industry": 行业选股
                      - "concept": 概念选股
            include_stock_info: 是否包含股票基础信息

        Returns:
            List[Dict]: 自选股列表

        示例返回:
            [
                {
                    "id": 1,
                    "user_id": 1001,
                    "symbol": "600000",
                    "list_type": "favorite",
                    "added_at": "2025-10-15 10:30:00",
                    "note": "长期持有",
                    "stock_info": {  # include_stock_info=True时包含
                        "name": "浦发银行",
                        "industry": "银行",
                        "market": "上海"
                    }
                },
                ...
            ]

        性能要求:
            - 不含股票信息: < 50ms
            - 含股票信息: < 150ms (使用joinedload避免N+1查询)

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    @abstractmethod
    def add_to_watchlist(
        self,
        user_id: int,
        symbol: str,
        list_type: str = "favorite",
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        添加股票到自选列表

        Args:
            user_id: 用户ID
            symbol: 股票代码
            list_type: 列表类型
            note: 备注信息

        Returns:
            Dict: 添加成功的记录

        示例返回:
            {
                "id": 123,
                "user_id": 1001,
                "symbol": "600000",
                "list_type": "favorite",
                "added_at": "2025-11-21 14:30:00",
                "note": "长期持有"
            }

        性能要求: < 100ms

        Raises:
            DataSourceException: 添加失败
            ValueError: 股票代码无效或已存在
        """
        pass

    @abstractmethod
    def remove_from_watchlist(
        self, user_id: int, symbol: str, list_type: Optional[str] = None
    ) -> bool:
        """
        从自选列表移除股票

        Args:
            user_id: 用户ID
            symbol: 股票代码
            list_type: 列表类型，None表示删除所有类型的记录

        Returns:
            bool: 是否删除成功

        性能要求: < 80ms

        Raises:
            DataSourceException: 删除失败
        """
        pass

    @abstractmethod
    def update_watchlist_note(
        self, user_id: int, symbol: str, list_type: str, note: str
    ) -> bool:
        """
        更新自选股备注

        Args:
            user_id: 用户ID
            symbol: 股票代码
            list_type: 列表类型
            note: 新的备注

        Returns:
            bool: 是否更新成功

        性能要求: < 80ms

        Raises:
            DataSourceException: 更新失败
        """
        pass

    # ==================== 策略配置管理 ====================

    @abstractmethod
    def get_strategy_configs(
        self,
        user_id: int,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取策略配置列表

        Args:
            user_id: 用户ID
            strategy_type: 策略类型过滤
                          - "momentum": 动量策略
                          - "mean_reversion": 均值回归
                          - "grid": 网格交易
                          - "arbitrage": 套利策略
            status: 状态过滤
                   - "active": 激活
                   - "inactive": 未激活
                   - "backtesting": 回测中

        Returns:
            List[Dict]: 策略配置列表

        示例返回:
            [
                {
                    "id": 1,
                    "user_id": 1001,
                    "name": "动量策略001",
                    "strategy_type": "momentum",
                    "status": "active",
                    "parameters": {
                        "lookback_period": 20,
                        "entry_threshold": 0.02,
                        "exit_threshold": -0.01
                    },
                    "created_at": "2025-10-01 10:00:00",
                    "updated_at": "2025-11-15 14:30:00",
                    "description": "20日动量突破策略"
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def save_strategy_config(
        self,
        user_id: int,
        name: str,
        strategy_type: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        保存策略配置

        Args:
            user_id: 用户ID
            name: 策略名称
            strategy_type: 策略类型
            parameters: 策略参数（JSON格式）
            description: 策略描述

        Returns:
            Dict: 保存成功的策略配置

        性能要求: < 150ms

        Raises:
            DataSourceException: 保存失败
            ValueError: 参数验证失败
        """
        pass

    @abstractmethod
    def update_strategy_status(
        self, strategy_id: int, user_id: int, status: str
    ) -> bool:
        """
        更新策略状态

        Args:
            strategy_id: 策略ID
            user_id: 用户ID（权限验证）
            status: 新状态 (active/inactive/backtesting)

        Returns:
            bool: 是否更新成功

        性能要求: < 80ms

        Raises:
            DataSourceException: 更新失败
            PermissionError: 用户无权限
        """
        pass

    @abstractmethod
    def delete_strategy_config(self, strategy_id: int, user_id: int) -> bool:
        """
        删除策略配置

        Args:
            strategy_id: 策略ID
            user_id: 用户ID（权限验证）

        Returns:
            bool: 是否删除成功

        性能要求: < 100ms

        Raises:
            DataSourceException: 删除失败
            PermissionError: 用户无权限
        """
        pass

    # ==================== 风险管理配置 ====================

    @abstractmethod
    def get_risk_alerts(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        alert_type: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        获取风险预警配置

        Args:
            user_id: 用户ID
            symbol: 股票代码过滤
            alert_type: 预警类型
                       - "price": 价格预警
                       - "change": 涨跌幅预警
                       - "volume": 成交量预警
                       - "position": 持仓风险
            enabled_only: 是否只返回启用的预警

        Returns:
            List[Dict]: 风险预警配置列表

        示例返回:
            [
                {
                    "id": 1,
                    "user_id": 1001,
                    "symbol": "600000",
                    "alert_type": "price",
                    "condition": ">=",
                    "threshold": 12.0,
                    "enabled": True,
                    "notification_methods": ["email", "sms"],
                    "created_at": "2025-11-01 10:00:00"
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def save_risk_alert(
        self,
        user_id: int,
        symbol: str,
        alert_type: str,
        condition: str,
        threshold: float,
        notification_methods: List[str],
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        保存风险预警配置

        Args:
            user_id: 用户ID
            symbol: 股票代码
            alert_type: 预警类型
            condition: 条件 (>=, <=, >, <, ==)
            threshold: 阈值
            notification_methods: 通知方式 ["email", "sms", "webhook"]
            enabled: 是否启用

        Returns:
            Dict: 保存的预警配置

        性能要求: < 120ms

        Raises:
            DataSourceException: 保存失败
            ValueError: 参数验证失败
        """
        pass

    @abstractmethod
    def toggle_risk_alert(self, alert_id: int, user_id: int, enabled: bool) -> bool:
        """
        启用/禁用风险预警

        Args:
            alert_id: 预警ID
            user_id: 用户ID（权限验证）
            enabled: 是否启用

        Returns:
            bool: 是否更新成功

        性能要求: < 80ms

        Raises:
            DataSourceException: 更新失败
            PermissionError: 用户无权限
        """
        pass

    # ==================== 用户配置管理 ====================

    @abstractmethod
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户偏好设置

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户偏好设置

        示例返回:
            {
                "user_id": 1001,
                "display_settings": {
                    "theme": "dark",
                    "language": "zh_CN",
                    "chart_type": "candle"
                },
                "notification_settings": {
                    "email_enabled": True,
                    "sms_enabled": False,
                    "push_enabled": True
                },
                "trading_settings": {
                    "default_order_type": "limit",
                    "confirm_before_trade": True
                },
                "updated_at": "2025-11-15 10:30:00"
            }

        性能要求: < 80ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def update_user_preferences(
        self, user_id: int, preferences: Dict[str, Any]
    ) -> bool:
        """
        更新用户偏好设置

        Args:
            user_id: 用户ID
            preferences: 新的偏好设置（部分更新）

        Returns:
            bool: 是否更新成功

        性能要求: < 100ms

        Raises:
            DataSourceException: 更新失败
            ValueError: 设置格式无效
        """
        pass

    # ==================== 股票基础信息 ====================

    @abstractmethod
    def get_stock_basic_info(
        self,
        symbols: Optional[List[str]] = None,
        market: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取股票基础信息

        Args:
            symbols: 股票代码列表，None表示获取全部
            market: 市场过滤 (上海/深圳)
            industry: 行业过滤

        Returns:
            List[Dict]: 股票基础信息列表

        示例返回:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "market": "上海",
                    "industry": "银行",
                    "sector": "金融",
                    "list_date": "1999-11-10",
                    "total_shares": 29352000000,
                    "float_shares": 29352000000
                },
                ...
            ]

        性能要求:
            - 单个股票: < 50ms
            - 批量查询(100个): < 200ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索股票

        Args:
            keyword: 关键词（支持代码、名称、拼音首字母）
            limit: 返回数量限制

        Returns:
            List[Dict]: 搜索结果

        示例返回:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "pinyin": "PFYH",
                    "market": "上海",
                    "match_type": "name"  # code/name/pinyin
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 搜索失败
        """
        pass

    # ==================== 行业概念板块 ====================

    @abstractmethod
    def get_industry_list(self, classification: str = "sw") -> List[Dict[str, Any]]:
        """
        获取行业分类列表

        Args:
            classification: 分类标准
                           - "sw": 申万行业
                           - "csrc": 证监会行业
                           - "zjh": 中金行业

        Returns:
            List[Dict]: 行业列表

        示例返回:
            [
                {
                    "code": "801010",
                    "name": "农林牧渔",
                    "level": 1,
                    "parent_code": None,
                    "stock_count": 123
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def get_concept_list(self) -> List[Dict[str, Any]]:
        """
        获取概念板块列表

        Returns:
            List[Dict]: 概念列表

        示例返回:
            [
                {
                    "code": "BK0001",
                    "name": "人工智能",
                    "stock_count": 234,
                    "updated_at": "2025-11-21"
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def get_stocks_by_industry(self, industry_code: str) -> List[str]:
        """
        获取行业成分股

        Args:
            industry_code: 行业代码

        Returns:
            List[str]: 股票代码列表

        性能要求: < 120ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def get_stocks_by_concept(self, concept_code: str) -> List[str]:
        """
        获取概念成分股

        Args:
            concept_code: 概念代码

        Returns:
            List[str]: 股票代码列表

        性能要求: < 120ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    # ==================== 数据库操作辅助 ====================

    @abstractmethod
    def begin_transaction(self) -> Any:
        """
        开始事务

        Returns:
            事务对象

        用于需要原子性操作的场景，例如批量更新
        """
        pass

    @abstractmethod
    def commit_transaction(self, transaction: Any) -> None:
        """
        提交事务

        Args:
            transaction: 事务对象
        """
        pass

    @abstractmethod
    def rollback_transaction(self, transaction: Any) -> None:
        """
        回滚事务

        Args:
            transaction: 事务对象
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        关系数据源健康检查

        Returns:
            Dict: 健康状态

        示例返回:
            {
                "status": "healthy",
                "data_source_type": "postgresql",
                "response_time_ms": 25,
                "connection_pool": {
                    "size": 20,
                    "in_use": 5,
                    "available": 15
                },
                "last_query": "2025-11-21 14:59:58",
                "metrics": {
                    "total_queries_today": 8765,
                    "avg_response_time_ms": 32,
                    "slow_queries_count": 5
                }
            }

        Raises:
            DataSourceException: 健康检查失败
        """
        pass
