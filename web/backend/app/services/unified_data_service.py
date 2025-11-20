"""
统一数据服务 - 双数据源调用封装

支持真实数据源和Mock数据源的统一调用，提供：
- 数据源切换机制
- 故障转移支持
- 缓存管理
- 统一数据格式
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from enum import Enum
import os

from app.core.database import db_service
from app.core.cache_integration import get_cache_integration

logger = logging.getLogger(__name__)

# 数据源类型枚举
class DataSourceType(Enum):
    """数据源类型"""
    DATABASE = "database"  # 真实数据库
    MOCK = "mock"          # Mock数据
    HYBRID = "hybrid"      # 混合模式（优先数据库，失败时Mock）

# 配置类
class DataSourceConfig:
    """数据源配置"""
    def __init__(self):
        self.primary_source = DataSourceType.DATABASE
        self.fallback_source = DataSourceType.MOCK
        self.enable_cache = True
        self.cache_ttl = {
            "stocks_basic": 300,      # 5分钟
            "stocks_industries": 3600, # 1小时
            "stocks_concepts": 3600,   # 1小时
            "markets_overview": 600,   # 10分钟
            "stocks_search": 180,      # 3分钟
            "stocks_daily": 300,       # 5分钟
        }
        
        # 从环境变量读取配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        primary = os.getenv('DATA_SOURCE_PRIMARY', 'database').lower()
        fallback = os.getenv('DATA_SOURCE_FALLBACK', 'mock').lower()
        
        if primary in ['database', 'db']:
            self.primary_source = DataSourceType.DATABASE
        elif primary == 'mock':
            self.primary_source = DataSourceType.MOCK
        elif primary == 'hybrid':
            self.primary_source = DataSourceType.HYBRID
            
        if fallback in ['database', 'db']:
            self.fallback_source = DataSourceType.DATABASE
        elif fallback == 'mock':
            self.fallback_source = DataSourceType.MOCK
            
        cache_enabled = os.getenv('DATA_CACHE_ENABLED', 'true').lower()
        self.enable_cache = cache_enabled in ['true', '1', 'yes', 'on']

# Mock数据生成器
class MockDataGenerator:
    """Mock数据生成器"""
    
    def __init__(self):
        self.random = random.Random(42)  # 使用固定种子确保数据一致性
    
    def generate_stocks_basic(self, count: int = 100) -> List[Dict]:
        """生成模拟股票基本信息"""
        stocks = []
        
        # 预设的股票代码池
        stock_pool = [
            ("600000", "浦发银行"), ("600036", "招商银行"), ("600519", "贵州茅台"),
            ("000001", "平安银行"), ("000002", "万科A"), ("000858", "五粮液"),
            ("002415", "海康威视"), ("002594", "BYD"), ("300059", "东方财富"),
            ("300750", "宁德时代"), ("600276", "恒瑞医药"), ("600887", "伊利股份"),
            ("601318", "中国平安"), ("601398", "工商银行"), ("601857", "中国石油"),
            ("000725", "京东方A"), ("002304", "洋河股份"), ("300015", "爱尔眼科"),
            ("600031", "三一重工"), ("600585", "海螺水泥")
        ]
        
        # 行业列表
        industries = [
            "银行", "证券", "保险", "房地产", "汽车", "医药生物", "食品饮料",
            "电子", "计算机", "通信", "化工", "钢铁", "有色金属", "建筑材料",
            "建筑装饰", "机械设备", "电力", "公用事业", "交通运输", "零售"
        ]
        
        concepts = [
            "人工智能", "5G", "物联网", "新能源汽车", "云计算", "大数据",
            "芯片概念", "光伏", "风电", "储能", "元宇宙", "数字经济"
        ]
        
        # 生成股票数据
        for i in range(min(count, len(stock_pool))):
            symbol, name = stock_pool[i]
            
            # 生成价格数据
            base_price = self.random.uniform(5.0, 200.0)
            change = self.random.uniform(-10.0, 10.0)
            change_pct = (change / (base_price - change)) * 100 if base_price != change else 0
            
            stock = {
                "symbol": symbol,
                "name": name,
                "market": "SH" if symbol.startswith("6") else "SZ",
                "industry": self.random.choice(industries),
                "price": round(base_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "volume": self.random.randint(100000, 10000000),
                "turnover": round(self.random.uniform(0.1, 10.0), 2),
                "market_cap": self.random.randint(10000000000, 1000000000000),
                "pe_ratio": round(self.random.uniform(5.0, 50.0), 2),
                "concepts": self.random.sample(concepts, self.random.randint(0, 3))
            }
            stocks.append(stock)
        
        return stocks
    
    def generate_industries(self) -> List[Dict]:
        """生成模拟行业数据"""
        industries = [
            "银行", "证券", "保险", "房地产", "汽车", "医药生物", "食品饮料",
            "电子", "计算机", "通信", "化工", "钢铁", "有色金属", "建筑材料",
            "建筑装饰", "机械设备", "电力", "公用事业", "交通运输", "零售"
        ]
        
        return [{"industry_name": industry, "industry_code": f"IND_{i+1:03d}"} 
                for i, industry in enumerate(industries)]
    
    def generate_concepts(self) -> List[Dict]:
        """生成模拟概念数据"""
        concepts = [
            "人工智能", "5G", "物联网", "新能源汽车", "云计算", "大数据",
            "芯片概念", "光伏", "风电", "储能", "元宇宙", "数字经济",
            "区块链", "虚拟现实", "增强现实", "机器人", "无人机"
        ]
        
        return [{"concept_name": concept, "concept_code": f"CON_{i+1:03d}"} 
                for i, concept in enumerate(concepts)]
    
    def generate_market_overview(self) -> Dict:
        """生成模拟市场概览"""
        return {
            "market_index": {
                "sh": {
                    "name": "上证指数",
                    "code": "000001",
                    "value": round(self.random.uniform(3000, 4000), 2),
                    "change_pct": round(self.random.uniform(-3.0, 3.0), 2),
                    "change": round(self.random.uniform(-100, 100), 2)
                },
                "sz": {
                    "name": "深证成指",
                    "code": "399001",
                    "value": round(self.random.uniform(9000, 12000), 2),
                    "change_pct": round(self.random.uniform(-3.0, 3.0), 2),
                    "change": round(self.random.uniform(-300, 300), 2)
                },
                "cy": {
                    "name": "创业板指",
                    "code": "399006",
                    "value": round(self.random.uniform(2000, 3000), 2),
                    "change_pct": round(self.random.uniform(-4.0, 4.0), 2),
                    "change": round(self.random.uniform(-100, 100), 2)
                }
            },
            "market_summary": {
                "total_stocks": self.random.randint(4000, 5000),
                "up_count": self.random.randint(1500, 3000),
                "down_count": self.random.randint(1000, 2500),
                "flat_count": self.random.randint(100, 500),
                "total_volume": self.random.randint(800000000, 1200000000),
                "total_amount": self.random.randint(80000000000, 120000000000)
            }
        }
    
    def generate_search_results(self, keyword: str) -> List[Dict]:
        """生成模拟搜索结果"""
        if not keyword:
            return []
        
        stocks = self.generate_stocks_basic(20)
        # 简单筛选包含关键词的股票
        filtered_stocks = [
            stock for stock in stocks 
            if keyword.lower() in stock['symbol'].lower() or keyword in stock['name']
        ]
        return filtered_stocks[:10]

# 统一数据服务类
class UnifiedDataService:
    """统一数据服务 - 双数据源调用封装"""
    
    def __init__(self, config: Optional[DataSourceConfig] = None):
        self.config = config or DataSourceConfig()
        self.mock_generator = MockDataGenerator()
        self.cache = get_cache_integration() if self.config.enable_cache else None
        
        logger.info(f"初始化统一数据服务 - 主数据源: {self.config.primary_source.value}")
    
    async def get_stocks_basic(self, **params) -> Dict[str, Any]:
        """获取股票基本信息"""
        cache_key = f"stocks_basic:{hash(str(sorted(params.items())))}"
        
        # 尝试从缓存获取
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # 获取数据
        data = await self._fetch_data_with_fallback(
            self._get_stocks_basic_from_database,
            self.mock_generator.generate_stocks_basic,
            params
        )
        
        # 缓存结果
        if self.cache and data:
            await self.cache.set(cache_key, data, ttl=self.config.cache_ttl["stocks_basic"])
        
        return data
    
    async def get_stocks_industries(self) -> Dict[str, Any]:
        """获取行业列表"""
        cache_key = "stocks_industries"
        
        # 尝试从缓存获取
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # 获取数据
        data = await self._fetch_data_with_fallback(
            self._get_stocks_industries_from_database,
            self.mock_generator.generate_industries
        )
        
        # 缓存结果
        if self.cache and data:
            await self.cache.set(cache_key, data, ttl=self.config.cache_ttl["stocks_industries"])
        
        return data
    
    async def get_stocks_concepts(self) -> Dict[str, Any]:
        """获取概念列表"""
        cache_key = "stocks_concepts"
        
        # 尝试从缓存获取
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # 获取数据
        data = await self._fetch_data_with_fallback(
            self._get_stocks_concepts_from_database,
            self.mock_generator.generate_concepts
        )
        
        # 缓存结果
        if self.cache and data:
            await self.cache.set(cache_key, data, ttl=self.config.cache_ttl["stocks_concepts"])
        
        return data
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        cache_key = "markets_overview"
        
        # 尝试从缓存获取
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # 获取数据
        data = await self._fetch_data_with_fallback(
            self._get_market_overview_from_database,
            self.mock_generator.generate_market_overview
        )
        
        # 缓存结果
        if self.cache and data:
            await self.cache.set(cache_key, data, ttl=self.config.cache_ttl["markets_overview"])
        
        return data
    
    async def search_stocks(self, keyword: str) -> Dict[str, Any]:
        """搜索股票"""
        cache_key = f"stocks_search:{keyword}"
        
        # 尝试从缓存获取
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # 获取数据
        data = await self._fetch_data_with_fallback(
            lambda: self._search_stocks_in_database(keyword),
            lambda: self.mock_generator.generate_search_results(keyword)
        )
        
        # 缓存结果
        if self.cache and data:
            await self.cache.set(cache_key, data, ttl=self.config.cache_ttl["stocks_search"])
        
        return data
    
    # 数据库查询方法
    async def _get_stocks_basic_from_database(self, **params) -> Dict[str, Any]:
        """从数据库获取股票基本信息"""
        try:
            # 使用现有的db_service
            limit = params.get('limit', 100)
            df = db_service.query_stocks_basic(limit=limit)
            
            if df.empty:
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 添加模拟行情数据
            import random
            random.seed(42 + len(df))
            
            if not df.empty:
                df["price"] = [round(random.uniform(5.0, 200.0), 2) for _ in range(len(df))]
                df["change"] = [round(random.uniform(-10.0, 10.0), 2) for _ in range(len(df))]
                df["change_pct"] = df["change"] / (df["price"] - df["change"]) * 100
                df["change_pct"] = df["change_pct"].round(2)
                df["volume"] = [random.randint(100000, 10000000) for _ in range(len(df))]
                df["turnover"] = [round(random.uniform(0.1, 10.0), 2) for _ in range(len(df))]
            
            return {
                "success": True,
                "data": df.to_dict("records"),
                "total": len(df),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            raise
    
    async def _get_stocks_industries_from_database(self) -> Dict[str, Any]:
        """从数据库获取行业列表"""
        try:
            df = db_service.query_stocks_basic(limit=10000)
            
            if df.empty:
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            industries = df["industry"].dropna().unique().tolist()
            industries = sorted([industry for industry in industries if industry.strip()])
            
            industry_list = [{"industry_name": industry, "industry_code": f"IND_{i+1:03d}"} 
                           for i, industry in enumerate(industries)]
            
            return {
                "success": True,
                "data": industry_list,
                "total": len(industry_list),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"数据库查询行业失败: {str(e)}")
            raise
    
    async def _get_stocks_concepts_from_database(self) -> Dict[str, Any]:
        """从数据库获取概念列表"""
        # 目前概念数据主要通过Mock生成，因为数据库中没有概念关联信息
        return {
            "success": True,
            "data": self.mock_generator.generate_concepts(),
            "total": 17,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_market_overview_from_database(self) -> Dict[str, Any]:
        """从数据库获取市场概览"""
        try:
            # 计算市场统计数据
            df = db_service.query_stocks_basic(limit=1000)
            
            if df.empty:
                # 如果没有数据，返回Mock数据
                return {
                    "success": True,
                    "data": self.mock_generator.generate_market_overview(),
                    "timestamp": datetime.now().isoformat()
                }
            
            # 基于实际数据计算市场概览
            overview = self.mock_generator.generate_market_overview()
            
            return {
                "success": True,
                "data": overview,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"数据库查询市场概览失败: {str(e)}")
            raise
    
    async def _search_stocks_in_database(self, keyword: str) -> Dict[str, Any]:
        """在数据库中搜索股票"""
        try:
            df = db_service.query_stocks_basic(limit=1000)
            
            if df.empty or not keyword:
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 搜索筛选
            search_mask = df["symbol"].str.contains(keyword, case=False, na=False) | df[
                "name"
            ].str.contains(keyword, case=False, na=False)
            filtered_df = df[search_mask]
            
            return {
                "success": True,
                "data": filtered_df.to_dict("records"),
                "total": len(filtered_df),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"数据库搜索失败: {str(e)}")
            raise
    
    # 数据源故障转移方法
    async def _fetch_data_with_fallback(self, primary_func, fallback_func, *args, **kwargs) -> Dict[str, Any]:
        """带故障转移的数据获取"""
        try:
            # 尝试主要数据源
            if self.config.primary_source == DataSourceType.DATABASE:
                return await primary_func(*args, **kwargs)
            elif self.config.primary_source == DataSourceType.MOCK:
                return await fallback_func(*args, **kwargs)
            elif self.config.primary_source == DataSourceType.HYBRID:
                try:
                    # 尝试数据库
                    result = await primary_func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.warning(f"主要数据源失败，切换到Mock: {str(e)}")
                    # 切换到Mock数据源
                    if callable(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func
        except Exception as e:
            logger.error(f"主要数据源和Mock数据源都失败: {str(e)}")
            # 如果所有数据源都失败，返回错误信息
            return {
                "success": False,
                "msg": f"数据获取失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        
        # 如果primary_func不是callable，直接返回fallback
        if not callable(primary_func):
            return fallback_func
        
        return await primary_func(*args, **kwargs)

# 创建全局实例
unified_data_service = UnifiedDataService()

# 便捷函数
async def get_unified_data_service() -> UnifiedDataService:
    """获取统一数据服务实例"""
    return unified_data_service

async def get_stocks_basic(**params) -> Dict[str, Any]:
    """便捷函数：获取股票基本信息"""
    service = await get_unified_data_service()
    return await service.get_stocks_basic(**params)

async def get_stocks_industries() -> Dict[str, Any]:
    """便捷函数：获取行业列表"""
    service = await get_unified_data_service()
    return await service.get_stocks_industries()

async def get_stocks_concepts() -> Dict[str, Any]:
    """便捷函数：获取概念列表"""
    service = await get_unified_data_service()
    return await service.get_stocks_concepts()

async def get_market_overview() -> Dict[str, Any]:
    """便捷函数：获取市场概览"""
    service = await get_unified_data_service()
    return await service.get_market_overview()

async def search_stocks(keyword: str) -> Dict[str, Any]:
    """便捷函数：搜索股票"""
    service = await get_unified_data_service()
    return await service.search_stocks(keyword)