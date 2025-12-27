"""
Mock关系数据源实现

本模块实现IRelationalDataSource接口的Mock版本，用于开发和测试。
使用内存存储模拟PostgreSQL数据库，支持完整的CRUD操作。

核心特性:
1. 内存存储 - 使用字典和列表模拟数据库表
2. 事务支持 - 简化的事务管理（回滚恢复快照）
3. 关联查询 - 支持外键关联（模拟joinedload）
4. 数据持久化 - 可选的JSON文件持久化

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import uuid
import copy
from typing import List, Dict, Optional, Any
from datetime import datetime
from faker import Faker

from src.interfaces.relational_data_source import IRelationalDataSource
from src.core.exceptions import DataSourceException, DataSourceDataNotFound


class MockRelationalDataSource(IRelationalDataSource):
    """
    Mock关系数据源实现

    使用内存存储模拟PostgreSQL关系数据库。
    所有数据存储在内存中，重启后数据会丢失（除非启用持久化）。
    """

    def __init__(self, seed: Optional[int] = None, locale: str = "zh_CN"):
        """
        初始化Mock关系数据源

        Args:
            seed: 随机种子，设置后每次生成相同数据
            locale: 语言区域，默认中文
        """
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)

        # 内存存储
        self._watchlist: Dict[int, List[Dict]] = {}  # {user_id: [watchlist_items]}
        self._strategies: Dict[int, List[Dict]] = {}  # {user_id: [strategies]}
        self._risk_alerts: Dict[int, List[Dict]] = {}  # {user_id: [alerts]}
        self._user_preferences: Dict[int, Dict] = {}  # {user_id: preferences}
        self._stocks: List[Dict] = []  # 股票基本信息
        self._industries: List[Dict] = []  # 行业列表
        self._concepts: List[Dict] = []  # 概念列表
        self._stock_industry_map: Dict[str, str] = {}  # {symbol: industry_code}
        self._stock_concept_map: Dict[str, List[str]] = {}  # {symbol: [concept_codes]}

        # 事务管理
        self._in_transaction = False
        self._transaction_snapshot: Optional[Dict] = None

        # 初始化基础数据
        self._initialize_mock_data()

    def _initialize_mock_data(self):
        """初始化Mock数据"""
        # 生成100只股票
        for i in range(100):
            symbol = f"6{str(i).zfill(5)}" if i % 2 == 0 else f"0{str(i).zfill(5)}"
            self._stocks.append(
                {
                    "symbol": symbol,
                    "name": self.fake.company(),
                    "industry": f"IND{(i % 20):02d}",
                    "market": "上海A股" if symbol.startswith("6") else "深圳A股",
                    "list_date": self.fake.date_between(start_date="-10y", end_date="today").isoformat(),
                    "total_shares": self.fake.random_int(min=100000000, max=10000000000),
                    "float_shares": self.fake.random_int(min=50000000, max=5000000000),
                }
            )

        # 生成20个行业
        industry_names = [
            "银行",
            "证券",
            "保险",
            "房地产",
            "建筑材料",
            "钢铁",
            "煤炭",
            "石油",
            "化工",
            "医药",
            "电子",
            "计算机",
            "通信",
            "汽车",
            "家电",
            "食品饮料",
            "农业",
            "纺织服装",
            "轻工制造",
            "公用事业",
        ]
        for i, name in enumerate(industry_names):
            self._industries.append({"code": f"IND{i:02d}", "name": name, "stock_count": 5})

        # 生成30个概念
        concept_names = [
            "5G",
            "人工智能",
            "云计算",
            "大数据",
            "物联网",
            "新能源",
            "光伏",
            "风电",
            "锂电池",
            "储能",
            "芯片",
            "半导体",
            "软件",
            "游戏",
            "电商",
            "在线教育",
            "医疗器械",
            "生物医药",
            "新冠疫苗",
            "口罩",
            "军工",
            "航空",
            "高铁",
            "新基建",
            "智能制造",
            "工业互联网",
            "区块链",
            "数字货币",
            "元宇宙",
            "碳中和",
        ]
        for i, name in enumerate(concept_names):
            self._concepts.append(
                {
                    "code": f"CON{i:02d}",
                    "name": name,
                    "stock_count": self.fake.random_int(min=5, max=50),
                }
            )

        # 建立股票-行业映射
        for stock in self._stocks:
            self._stock_industry_map[stock["symbol"]] = stock["industry"]

        # 建立股票-概念映射（每只股票随机关联2-5个概念）
        for stock in self._stocks:
            num_concepts = self.fake.random_int(min=2, max=5)
            concepts = self.fake.random_elements(
                elements=[c["code"] for c in self._concepts],
                length=num_concepts,
                unique=True,
            )
            self._stock_concept_map[stock["symbol"]] = concepts

    # ==================== 自选股管理 ====================

    def get_watchlist(self, user_id: int, group_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户自选股列表"""
        if user_id not in self._watchlist:
            return []

        watchlist = self._watchlist[user_id]

        # 如果指定了分组，过滤
        if group_name:
            watchlist = [item for item in watchlist if item.get("group_name") == group_name]

        # 关联股票基本信息（模拟joinedload）
        result = []
        for item in watchlist:
            stock_info = next((s for s in self._stocks if s["symbol"] == item["symbol"]), None)
            if stock_info:
                result.append(
                    {
                        **item,
                        "stock_name": stock_info["name"],
                        "industry": stock_info["industry"],
                        "market": stock_info["market"],
                    }
                )

        return result

    def add_to_watchlist(
        self,
        user_id: int,
        symbol: str,
        group_name: str = "默认分组",
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """添加股票到自选股"""
        # 检查股票是否存在
        stock_info = next((s for s in self._stocks if s["symbol"] == symbol), None)
        if not stock_info:
            raise DataSourceDataNotFound(
                f"Stock {symbol} not found",
                source_type="mock",
                query_params={"symbol": symbol},
            )

        # 初始化用户自选股列表
        if user_id not in self._watchlist:
            self._watchlist[user_id] = []

        # 检查是否已存在
        existing = next(
            (item for item in self._watchlist[user_id] if item["symbol"] == symbol),
            None,
        )
        if existing:
            raise DataSourceException(f"Stock {symbol} already in watchlist", error_code="DUPLICATE_ENTRY")

        # 添加到自选股
        watchlist_item = {
            "id": len(self._watchlist[user_id]) + 1,
            "user_id": user_id,
            "symbol": symbol,
            "group_name": group_name,
            "note": note,
            "add_time": datetime.now().isoformat(),
            "stock_name": stock_info["name"],
        }
        self._watchlist[user_id].append(watchlist_item)

        return watchlist_item

    def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """从自选股中删除股票"""
        if user_id not in self._watchlist:
            return False

        original_len = len(self._watchlist[user_id])
        self._watchlist[user_id] = [item for item in self._watchlist[user_id] if item["symbol"] != symbol]

        return len(self._watchlist[user_id]) < original_len

    def update_watchlist_note(self, user_id: int, symbol: str, note: str) -> bool:
        """更新自选股备注"""
        if user_id not in self._watchlist:
            return False

        for item in self._watchlist[user_id]:
            if item["symbol"] == symbol:
                item["note"] = note
                item["update_time"] = datetime.now().isoformat()
                return True

        return False

    # ==================== 策略配置 ====================

    def get_strategy_configs(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户策略配置列表"""
        if user_id not in self._strategies:
            return []

        strategies = self._strategies[user_id]

        # 如果指定了状态，过滤
        if status:
            strategies = [s for s in strategies if s.get("status") == status]

        return strategies

    def save_strategy_config(
        self,
        user_id: int,
        strategy_name: str,
        strategy_type: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """保存策略配置"""
        # 初始化用户策略列表
        if user_id not in self._strategies:
            self._strategies[user_id] = []

        # 创建策略配置
        strategy_id = str(uuid.uuid4())
        strategy = {
            "id": strategy_id,
            "user_id": user_id,
            "strategy_name": strategy_name,
            "strategy_type": strategy_type,
            "parameters": parameters,
            "description": description,
            "status": "active",
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat(),
        }

        self._strategies[user_id].append(strategy)

        return strategy

    def update_strategy_status(self, user_id: int, strategy_id: str, status: str) -> bool:
        """更新策略状态"""
        if user_id not in self._strategies:
            return False

        for strategy in self._strategies[user_id]:
            if strategy["id"] == strategy_id:
                strategy["status"] = status
                strategy["update_time"] = datetime.now().isoformat()
                return True

        return False

    def delete_strategy_config(self, user_id: int, strategy_id: str) -> bool:
        """删除策略配置"""
        if user_id not in self._strategies:
            return False

        original_len = len(self._strategies[user_id])
        self._strategies[user_id] = [s for s in self._strategies[user_id] if s["id"] != strategy_id]

        return len(self._strategies[user_id]) < original_len

    # ==================== 风险预警 ====================

    def get_risk_alerts(
        self,
        user_id: int,
        alert_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户风险预警列表"""
        if user_id not in self._risk_alerts:
            return []

        alerts = self._risk_alerts[user_id]

        # 过滤
        if alert_type:
            alerts = [a for a in alerts if a.get("alert_type") == alert_type]
        if is_active is not None:
            alerts = [a for a in alerts if a.get("is_active") == is_active]

        return alerts

    def save_risk_alert(
        self,
        user_id: int,
        alert_type: str,
        alert_name: str,
        condition: Dict[str, Any],
        notification_methods: List[str],
    ) -> Dict[str, Any]:
        """保存风险预警配置"""
        # 初始化用户预警列表
        if user_id not in self._risk_alerts:
            self._risk_alerts[user_id] = []

        # 创建预警
        alert_id = str(uuid.uuid4())
        alert = {
            "id": alert_id,
            "user_id": user_id,
            "alert_type": alert_type,
            "alert_name": alert_name,
            "condition": condition,
            "notification_methods": notification_methods,
            "is_active": True,
            "create_time": datetime.now().isoformat(),
            "last_trigger_time": None,
        }

        self._risk_alerts[user_id].append(alert)

        return alert

    def toggle_risk_alert(self, user_id: int, alert_id: str, is_active: bool) -> bool:
        """切换风险预警状态"""
        if user_id not in self._risk_alerts:
            return False

        for alert in self._risk_alerts[user_id]:
            if alert["id"] == alert_id:
                alert["is_active"] = is_active
                alert["update_time"] = datetime.now().isoformat()
                return True

        return False

    # ==================== 用户偏好 ====================

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        if user_id not in self._user_preferences:
            # 返回默认偏好
            return {
                "theme": "light",
                "language": "zh_CN",
                "timezone": "Asia/Shanghai",
                "default_market": "A股",
                "chart_type": "candlestick",
                "show_volume": True,
                "show_ma": True,
                "ma_periods": [5, 10, 20, 60],
                "default_interval": "1d",
                "notification_enabled": True,
                "email_notification": False,
                "wechat_notification": False,
            }

        return self._user_preferences[user_id]

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户偏好设置"""
        # 获取当前偏好
        current = self.get_user_preferences(user_id)

        # 合并更新
        current.update(preferences)
        current["update_time"] = datetime.now().isoformat()

        # 保存
        self._user_preferences[user_id] = current

        return current

    # ==================== 股票信息 ====================

    def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        stock = next((s for s in self._stocks if s["symbol"] == symbol), None)

        if not stock:
            raise DataSourceDataNotFound(
                f"Stock {symbol} not found",
                source_type="mock",
                query_params={"symbol": symbol},
            )

        # 添加关联的行业和概念信息
        industry_code = self._stock_industry_map.get(symbol)
        industry = next((i for i in self._industries if i["code"] == industry_code), None)

        concept_codes = self._stock_concept_map.get(symbol, [])
        concepts = [c for c in self._concepts if c["code"] in concept_codes]

        return {
            **stock,
            "industry_name": industry["name"] if industry else None,
            "concepts": [c["name"] for c in concepts],
        }

    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索股票"""
        keyword_lower = keyword.lower()

        # 搜索股票代码或名称
        results = []
        for stock in self._stocks:
            if keyword_lower in stock["symbol"].lower() or keyword_lower in stock["name"].lower():
                results.append(
                    {
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "market": stock["market"],
                        "industry": stock["industry"],
                    }
                )

                if len(results) >= limit:
                    break

        return results

    # ==================== 行业概念 ====================

    def get_industry_list(self) -> List[Dict[str, Any]]:
        """获取行业列表"""
        return copy.deepcopy(self._industries)

    def get_concept_list(self) -> List[Dict[str, Any]]:
        """获取概念列表"""
        return copy.deepcopy(self._concepts)

    def get_stocks_by_industry(self, industry_code: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指定行业的股票列表"""
        stocks = [stock for stock in self._stocks if stock["industry"] == industry_code]

        return stocks[:limit]

    def get_stocks_by_concept(self, concept_code: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指定概念的股票列表"""
        # 找到所有属于该概念的股票
        symbols = [symbol for symbol, concepts in self._stock_concept_map.items() if concept_code in concepts]

        stocks = [stock for stock in self._stocks if stock["symbol"] in symbols]

        return stocks[:limit]

    # ==================== 事务管理 ====================

    def begin_transaction(self) -> None:
        """开始事务"""
        if self._in_transaction:
            raise DataSourceException("Transaction already started", error_code="TRANSACTION_ERROR")

        # 创建快照
        self._transaction_snapshot = {
            "watchlist": copy.deepcopy(self._watchlist),
            "strategies": copy.deepcopy(self._strategies),
            "risk_alerts": copy.deepcopy(self._risk_alerts),
            "user_preferences": copy.deepcopy(self._user_preferences),
        }
        self._in_transaction = True

    def commit_transaction(self) -> None:
        """提交事务"""
        if not self._in_transaction:
            raise DataSourceException("No active transaction", error_code="TRANSACTION_ERROR")

        # 清除快照
        self._transaction_snapshot = None
        self._in_transaction = False

    def rollback_transaction(self) -> None:
        """回滚事务"""
        if not self._in_transaction:
            raise DataSourceException("No active transaction", error_code="TRANSACTION_ERROR")

        # 恢复快照
        if self._transaction_snapshot:
            self._watchlist = self._transaction_snapshot["watchlist"]
            self._strategies = self._transaction_snapshot["strategies"]
            self._risk_alerts = self._transaction_snapshot["risk_alerts"]
            self._user_preferences = self._transaction_snapshot["user_preferences"]

        self._transaction_snapshot = None
        self._in_transaction = False

    # ==================== 健康检查 ====================

    def health_check(self) -> Dict[str, Any]:
        """关系数据源健康检查"""
        return {
            "status": "healthy",
            "data_source_type": "mock",
            "response_time_ms": self.fake.random_int(min=1, max=10),
            "connection_status": "connected",
            "statistics": {
                "total_users": len(self._watchlist),
                "total_watchlist_items": sum(len(items) for items in self._watchlist.values()),
                "total_strategies": sum(len(items) for items in self._strategies.values()),
                "total_risk_alerts": sum(len(items) for items in self._risk_alerts.values()),
                "total_stocks": len(self._stocks),
                "total_industries": len(self._industries),
                "total_concepts": len(self._concepts),
            },
        }
