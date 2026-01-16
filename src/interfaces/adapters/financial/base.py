"""
Financial DataSource基类

包含FinancialDataSource的基类定义、缓存逻辑和工具方法。
"""

import logging
from datetime import datetime


# 导入数据源接口
from src.interfaces import IDataSource

logger = logging.getLogger("FinancialDataSource")


class FinancialDataSource(IDataSource):
    """
    财务数据适配器 - 参考数据/基本面数据统一门户

    数据分类: DataClassification.FUNDAMENTAL_METRICS (第2类-参考数据-基本面数据)
    存储目标: MySQL/MariaDB
    数据特性: 低频、结构化、关系型

    多数据源整合:
    - 当前实现: efinance(主要) + easyquotation(备用)
    - 计划扩展: akshare、tushare、byapi、新浪财经爬虫

    核心能力:
    - 统一的财务数据获取接口
    - 多数据源自动降级切换
    - 数据验证和清洗
    - 智能缓存机制
    """


def __init__(self):
    """
    初始化财务数据适配器

    当前支持: efinance + easyquotation
    扩展计划: akshare、tushare、byapi、新浪财经爬虫
    """
    logger.info("初始化财务数据适配器...")
    # 当前实现的数据源
    self.efinance_available = False
    self.easyquotation_available = False
    # 计划扩展的数据源 (预留标志位)
    self.akshare_available = False
    self.tushare_available = False
    self.byapi_available = False
    self.sina_crawler_available = False
    # 初始化缓存字典
    self.data_cache = {}
    self._init_data_sources()
    logger.info(
        "数据源初始化完成 (efinance: '%s' if self.efinance_available else '不可用', "
        "easyquotation: '%s' if self.easyquotation_available else '不可用')"
    )


def _get_cache_key(self, symbol: str, data_type: str, **kwargs) -> str:
    """
    生成缓存键

    Args:
        symbol: 股票代码
        data_type: 数据类型
        **kwargs: 其他参数

    Returns:
        str: 缓存键
    """
    # 将参数转换为字符串并组合成键
    key_parts = [symbol, data_type]
    # 按键排序以确保相同参数生成相同的键
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    return "|".join(key_parts)


def _get_from_cache(self, cache_key: str):
    """
    从缓存中获取数据

    Args:
        cache_key: 缓存键

    Returns:
        缓存的数据，如果不存在或过期则返回None
    """
    if cache_key in self.data_cache:
        cached_item = self.data_cache[cache_key]
        # 检查缓存是否过期（这里设置为5分钟）
        if (datetime.now() - cached_item["timestamp"]).total_seconds() < 300:
            logger.info("使用缓存数据: %s", cache_key)
            return cached_item["data"]
        else:
            # 删除过期缓存
            del self.data_cache[cache_key]
    return None


def _save_to_cache(self, cache_key: str, data):
    """
    保存数据到缓存

    Args:
        cache_key: 缓存键
        data: 要缓存的数据
    """
    self.data_cache[cache_key] = {"data": data, "timestamp": datetime.now()}
    logger.info("数据已缓存: %s", cache_key)


def _init_data_sources(self):
    """
    初始化多数据源

    当前实现: efinance + easyquotation
    扩展计划: akshare、tushare、byapi、新浪财经爬虫
    """
    # 初始化efinance (当前主要数据源)
    try:
        import efinance as ef

        self.ef = ef
        self.efinance_available = True
        logger.info("efinance库导入成功")
    except ImportError:
        logger.warning("efinance库导入失败")
        self.efinance_available = False

    # 初始化easyquotation (当前备用数据源)
    try:
        import easyquotation as eq

        self.eq = eq
        self.easyquotation_available = True
        logger.info("easyquotation库导入成功")
    except ImportError:
        logger.warning("easyquotation库导入失败")
        self.easyquotation_available = False

    # - akshare: 财务报表、财务指标接口
    # - tushare: 专业财务数据接口(需token)
    # - byapi: 财务数据接口
    # - 新浪财经: 网页爬虫方法
    #
    # 已添加对akshare的支持，可以获取更全面的财务数据
    # 未来可考虑添加tushare等专业数据源支持
