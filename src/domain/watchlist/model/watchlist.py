"""
Watchlist Aggregate Root
自选股聚合根

管理自选股清单，包含股票列表和配置。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from uuid import uuid4

from src.domain.watchlist.value_objects import WatchlistType, StockCode, StockName, WatchlistConfig, AlertCondition
from .watchlist_stock import WatchlistStock


@dataclass
class Watchlist:
    """
    自选股聚合根

    职责：
    - 管理自选股清单的基本信息
    - 管理清单内的股票列表
    - 管理预警条件
    - 管理快照策略
    """

    id: str
    name: str
    watchlist_type: WatchlistType
    description: str = ""
    stocks: Dict[str, WatchlistStock] = field(default_factory=dict)
    config: WatchlistConfig = field(default_factory=WatchlistConfig)
    alert_conditions: List[AlertCondition] = field(default_factory=list)
    color_tag: str = "#3498db"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls, name: str, watchlist_type: WatchlistType, description: str = "", color_tag: str = "#3498db"
    ) -> "Watchlist":
        """工厂方法：创建新的自选股"""
        return cls(
            id=str(uuid4()), name=name, watchlist_type=watchlist_type, description=description, color_tag=color_tag
        )

    def add_stock(
        self, stock_code: str, stock_name: str = "", notes: str = "", tags: List[str] = None
    ) -> WatchlistStock:
        """添加股票到自选股"""
        if stock_code in self.stocks:
            raise ValueError(f"股票 {stock_code} 已在自选股中")

        if len(self.stocks) >= self.config.max_stocks_per_watchlist:
            raise ValueError(f"自选股已达最大股票数量限制 ({self.config.max_stocks_per_watchlist})")

        stock = WatchlistStock.create(
            watchlist_id=self.id, stock_code=stock_code, stock_name=stock_name, notes=notes, tags=tags or []
        )
        self.stocks[stock_code] = stock
        self.updated_at = datetime.now()
        return stock

    def remove_stock(self, stock_code: str) -> bool:
        """从自选股移除股票"""
        if stock_code in self.stocks:
            del self.stocks[stock_code]
            self.updated_at = datetime.now()
            return True
        return False

    def get_stock(self, stock_code: str) -> Optional[WatchlistStock]:
        """获取指定股票"""
        return self.stocks.get(stock_code)

    def contains_stock(self, stock_code: str) -> bool:
        """检查是否包含指定股票"""
        return stock_code in self.stocks

    def get_all_stock_codes(self) -> List[str]:
        """获取所有股票代码"""
        return list(self.stocks.keys())

    def update_config(self, config: WatchlistConfig) -> None:
        """更新配置"""
        self.config = config
        self.updated_at = datetime.now()

    def add_alert_condition(self, condition: AlertCondition) -> None:
        """添加预警条件"""
        self.alert_conditions.append(condition)

    def remove_alert_condition(self, condition_type: str) -> None:
        """移除指定类型的预警条件"""
        self.alert_conditions = [c for c in self.alert_conditions if c.condition_type != condition_type]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "watchlist_id": self.id,
            "watchlist_name": self.name,
            "stock_count": len(self.stocks),
            "type": self.watchlist_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def rename(self, new_name: str) -> None:
        """重命名自选股"""
        self.name = new_name
        self.updated_at = datetime.now()

    def update_color_tag(self, color_tag: str) -> None:
        """更新颜色标签"""
        self.color_tag = color_tag
        self.updated_at = datetime.now()

    def check_alerts(self, stock_code: str, current_value: float, condition_type: str) -> List[bool]:
        """检查预警条件"""
        results = []
        for condition in self.alert_conditions:
            if condition.condition_type == condition_type and condition.enabled:
                results.append(condition.matches(current_value))
        return results

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.watchlist_type.value,
            "description": self.description,
            "color_tag": self.color_tag,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
