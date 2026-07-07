"""OpenStock 数据网关客户端.

本项目通过此模块统一访问所有 A 股市场/基本面/财务/公告/资金流/板块/龙虎榜/
跨市场数据。OpenStock 服务部署在 NAS Docker (192.168.123.104:8040),对外暴露
70 个 source-neutral data_category,自带 5 秒 TTL 缓存、熔断器、自动 failover、
字段 normalize、X-API-Key 鉴权。

本模块仅做轻量 HTTP 客户端:超时 + 单次重试,不复刻 OpenStock 内部能力。
"""

from src.services.openstock.client import (
    OpenStockClient,
    OpenStockError,
    OpenStockProviderUnavailable,
)
from src.services.openstock.category_mapping import DataCategory

__all__ = [
    "OpenStockClient",
    "OpenStockError",
    "OpenStockProviderUnavailable",
    "DataCategory",
]
