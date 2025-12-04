# Real数据对接完整路线图 - 8周实现计划

**目标**: 从Mock数据平滑过渡到Real数据，实现数据源自动切换
**周期**: 8周 (从Week 1开始，Week 0为准备周)
**成功指标**: 可用性>99.9%, 错误率<0.1%, P95响应时间<500ms

---

## 📋 完整里程碑

```
Week 0: 准备期（当前）
  ├─ ✅ 架构评审完成 (backend-architect完成)
  ├─ ✅ P0改进计划制定 (4项关键改进)
  └─ ⏳ P0改进执行 (启动)

Week 1-2: P0改进 + 基础准备
  ├─ Task 1: CSRF保护启用
  ├─ Task 2: Pydantic数据验证
  ├─ Task 3: 熔断器+降级策略
  ├─ Task 4: 测试覆盖率30%
  └─ Real Prep: 数据验证层 + DataSourceFactory

Week 3-4: 数据同步基础
  ├─ 增量同步机制实现
  ├─ 数据源切换框架
  ├─ 实时数据流处理
  └─ 数据质量监控

Week 5-6: 验证和优化
  ├─ 集成测试 (>80%覆盖)
  ├─ 性能测试和优化
  ├─ 监控告警配置
  └─ 灰度发布准备

Week 7-8: 上线和稳定
  ├─ 灰度发布 (10% → 50% → 100%)
  ├─ 7x24监控
  ├─ 问题修复和优化
  └─ Mock数据完全下线
```

---

## 🎯 Week 0: 准备期（当前）

### 目标
- ✅ 完成架构评审 (已完成)
- ✅ 制定P0改进计划 (已完成)
- ⏳ 启动P0改进执行
- ⏳ 准备Real数据源

### 关键活动

#### 1. 了解现有数据源

```python
# 研究项目已支持的数据源
# web/backend/app/services/data_service.py

# 支持的数据源：
# 1. Akshare - 免费金融数据
# 2. Tushare - 专业金融数据
# 3. Yahoo Finance - 国际股票数据
# 4. Mock数据 - 开发测试用

# 数据源配置
DATASOURCES = {
    "akshare": {
        "name": "Akshare免费数据",
        "priority": 1,
        "cost": "免费",
        "latency": "2-5秒",
        "coverage": "国内A股 + 期货"
    },
    "tushare": {
        "name": "Tushare专业数据",
        "priority": 2,
        "cost": "按量收费",
        "latency": "<1秒",
        "coverage": "全球股票 + 实时报价"
    },
    "mock": {
        "name": "Mock测试数据",
        "priority": 0,
        "cost": "免费",
        "latency": "<10ms",
        "coverage": "测试覆盖"
    }
}
```

#### 2. 准备Real数据源API密钥

```bash
# 获取API密钥（如果使用收费源）
# Akshare: https://akshare.akfamily.xyz/
#   - 无需注册，免费使用
#   - 速率限制: 100请求/分钟

# Tushare: https://tushare.pro/
#   - 注册账户
#   - 专业版收费：按量或订阅
#   - 速率限制: 20000请求/天

# 更新 .env 配置
cat > .env.real << 'EOF'
# Real数据源配置
AKSHARE_ENABLED=true
TUSHARE_ENABLED=true
TUSHARE_TOKEN=${TUSHARE_TOKEN}  # 从https://tushare.pro获取
TUSHARE_QPS_LIMIT=20  # 查询频率限制（次/秒）

# 数据库配置（不变）
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

# 缓存配置
REDIS_URL=${REDIS_URL}
CACHE_TTL=86400  # 24小时

# 特性开关
USE_REAL_DATA=false  # Week 0仍使用Mock
USE_FALLBACK=true    # 启用降级策略
CIRCUIT_BREAKER_ENABLED=true
EOF
```

#### 3. 研究现有API端点

```python
# 查看需要Real数据的关键端点
# web/backend/app/api/

# 关键端点分析：
REAL_DATA_ENDPOINTS = {
    "market_data": {
        "endpoint": "/api/v1/market/fetch-data",
        "method": "POST",
        "current_source": "Mock",
        "target_source": ["Akshare", "Tushare"],
        "priority": "P0",
        "data_type": "OHLCV (Open/High/Low/Close/Volume)"
    },
    "stock_info": {
        "endpoint": "/api/v1/stock/info",
        "method": "GET",
        "current_source": "Mock",
        "target_source": ["Akshare"],
        "priority": "P0",
        "data_type": "Stock基本信息"
    },
    "market_overview": {
        "endpoint": "/api/v1/market/overview",
        "method": "GET",
        "current_source": "Mock",
        "target_source": ["Akshare"],
        "priority": "P1",
        "data_type": "市场总览（指数、行情热点）"
    },
    "sector_analysis": {
        "endpoint": "/api/v1/market/sectors",
        "method": "GET",
        "current_source": "Mock",
        "target_source": ["Akshare"],
        "priority": "P1",
        "data_type": "板块分析数据"
    }
}
```

### 交付物
- ✅ 架构评审报告 (docs/architecture/ARCHITECTURE_REVIEW_REPORT_2025-12-04.md)
- ✅ P0实施计划 (docs/guides/P0_IMPLEMENTATION_PLAN_2025-12-04.md)
- ✅ Real数据对接路线图 (本文档)
- ✅ Real数据源研究报告 (准备中)

---

## 🔄 Week 1-2: P0改进 + 基础准备

### P0改进任务（见P0_IMPLEMENTATION_PLAN）

1. **Task 1: CSRF保护** (2-3天)
2. **Task 2: Pydantic数据验证** (3-5天)
3. **Task 3: 错误处理** (3-5天)
4. **Task 4: 测试覆盖** (5-7天)

### Real数据对接基础准备

#### 准备1: 数据验证层

```python
# web/backend/app/core/data_validation.py

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any

class OHLCVDataModel(BaseModel):
    """OHLCV数据验证模型"""
    symbol: str = Field(..., description="股票代码")
    timestamp: str = Field(..., description="数据时间戳 (YYYY-MM-DD HH:MM:SS)")
    open: float = Field(..., gt=0, description="开盘价")
    high: float = Field(..., gt=0, description="最高价")
    low: float = Field(..., gt=0, description="最低价")
    close: float = Field(..., gt=0, description="收盘价")
    volume: int = Field(..., ge=0, description="成交量")

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """验证时间戳格式"""
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('时间戳格式必须为 YYYY-MM-DD HH:MM:SS')
        return v

    @validator('high')
    def validate_high_vs_low(cls, v, values):
        """验证最高价 >= 最低价"""
        if 'low' in values and v < values['low']:
            raise ValueError('最高价必须 >= 最低价')
        return v

    @validator('close')
    def validate_close_range(cls, v, values):
        """验证收盘价在合理范围"""
        if 'high' in values and 'low' in values:
            if v > values['high'] or v < values['low']:
                raise ValueError('收盘价必须在最高价和最低价之间')
        return v

    class Config:
        str_strip_whitespace = True
```

#### 准备2: DataSourceFactory实现

```python
# web/backend/app/core/data_source.py

from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """数据源类型"""
    MOCK = "mock"
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    YAHOO = "yahoo"

class IDataSource(ABC):
    """数据源接口"""

    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取OHLCV数据"""
        pass

    @abstractmethod
    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        pass

class MockDataSource(IDataSource):
    """Mock数据源实现"""

    async def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """从Mock数据返回"""
        # ... Mock数据逻辑
        return []

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """返回Mock股票信息"""
        return {}

class AkshareDataSource(IDataSource):
    """Akshare数据源实现"""

    async def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """从Akshare获取Real数据"""
        try:
            import akshare as ak

            # 转换symbol格式（AAPL -> aapl）
            ak_symbol = symbol.lower()

            # 获取数据
            df = ak.stock_zh_a_hist(
                symbol=ak_symbol,
                period="daily",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", "")
            )

            # 转换为OHLCV格式
            return self._format_to_ohlcv(df, symbol)

        except Exception as e:
            logger.error(f"Akshare数据获取失败 ({symbol})", error=str(e))
            raise

    def _format_to_ohlcv(self, df, symbol: str):
        """转换DataFrame为OHLCV格式"""
        ohlcv = []
        for _, row in df.iterrows():
            ohlcv.append({
                "symbol": symbol,
                "timestamp": row['日期'],
                "open": float(row['开盘']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "close": float(row['收盘']),
                "volume": int(row['成交量'])
            })
        return ohlcv

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        # ... 实现逻辑
        return {}

class TushareDataSource(IDataSource):
    """Tushare数据源实现"""

    def __init__(self, token: str):
        """初始化Tushare数据源"""
        import tushare as ts
        self.pro = ts.pro_api(token)

    async def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """从Tushare获取Real数据"""
        try:
            # 转换symbol格式
            ts_symbol = f"{symbol.upper()}.US"  # 美股格式

            # 获取数据
            df = self.pro.daily(
                ts_code=ts_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", "")
            )

            return self._format_to_ohlcv(df, symbol)

        except Exception as e:
            logger.error(f"Tushare数据获取失败 ({symbol})", error=str(e))
            raise

    def _format_to_ohlcv(self, df, symbol: str):
        """转换DataFrame为OHLCV格式"""
        ohlcv = []
        for _, row in df.iterrows():
            ohlcv.append({
                "symbol": symbol,
                "timestamp": row['trade_date'],
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['vol'])
            })
        return ohlcv

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        # ... 实现逻辑
        return {}

class DataSourceFactory:
    """数据源工厂"""

    def __init__(self):
        self.sources: Dict[DataSourceType, IDataSource] = {}
        self.current_source_type: DataSourceType = DataSourceType.MOCK
        self._initialize_sources()

    def _initialize_sources(self):
        """初始化所有数据源"""
        # Mock数据源（总是可用）
        self.sources[DataSourceType.MOCK] = MockDataSource()

        # Real数据源（根据配置启用）
        import os

        if os.getenv('AKSHARE_ENABLED', 'false').lower() == 'true':
            self.sources[DataSourceType.AKSHARE] = AkshareDataSource()
            logger.info("✅ Akshare数据源已初始化")

        if os.getenv('TUSHARE_ENABLED', 'false').lower() == 'true':
            token = os.getenv('TUSHARE_TOKEN')
            if token:
                self.sources[DataSourceType.TUSHARE] = TushareDataSource(token)
                logger.info("✅ Tushare数据源已初始化")

    def set_source(self, source_type: DataSourceType):
        """切换数据源"""
        if source_type not in self.sources:
            raise ValueError(f"数据源 {source_type.value} 未初始化")

        self.current_source_type = source_type
        logger.info(f"数据源已切换: {source_type.value}")

    def get_source(self) -> IDataSource:
        """获取当前数据源"""
        return self.sources[self.current_source_type]

    async def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取OHLCV数据（自动使用当前数据源）"""
        source = self.get_source()
        data = await source.fetch_ohlcv(symbol, start_date, end_date, interval)

        # 验证数据
        validated = []
        for item in data:
            try:
                validated_item = OHLCVDataModel(**item)
                validated.append(validated_item.model_dump())
            except Exception as e:
                logger.warning(f"数据验证失败: {item}, 错误: {str(e)}")
                continue

        return validated

# 全局数据源工厂实例
data_source_factory = DataSourceFactory()
```

### 交付物
- ✅ P0改进全部完成（4项Task）
- ✅ 数据验证层完整实现
- ✅ DataSourceFactory框架完成
- ✅ 测试覆盖率达到30%

---

## 🔄 Week 3-4: 数据同步基础

### 目标
- 实现Mock ↔ Real数据自动切换
- 增量同步机制
- 数据质量监控

### 关键实现

#### 实现1: 增量同步管理器

```python
# web/backend/app/core/incremental_sync.py

class IncrementalSyncManager:
    """增量同步管理器"""

    def __init__(self):
        self.sync_state = {}  # 记录每个symbol的同步状态

    async def sync_incremental(self, symbol: str):
        """增量同步数据"""
        # 1. 查询本地最新数据时间
        last_local_timestamp = await self.get_last_local_timestamp(symbol)

        # 2. 从Real数据源获取增量数据
        incremental_data = await data_source_factory.fetch_ohlcv(
            symbol=symbol,
            start_date=last_local_timestamp,
            end_date=datetime.now().strftime('%Y-%m-%d')
        )

        # 3. 验证数据完整性
        validated_data = await self.validate_data(incremental_data)

        # 4. 保存到数据库
        await self.save_to_database(symbol, validated_data)

        # 5. 更新同步状态
        self.sync_state[symbol] = {
            "last_sync": datetime.now(),
            "records_synced": len(validated_data),
            "status": "success"
        }
```

### 交付物
- ✅ 增量同步机制完整
- ✅ 数据源切换框架
- ✅ 实时数据流处理
- ✅ 数据质量监控系统

---

## ✅ Week 5-6: 验证和优化

### 目标
- 集成测试覆盖率>80%
- 性能优化
- 灰度发布准备

### 关键活动
1. 端到端集成测试
2. 性能基准测试
3. 压力测试（模拟高并发）
4. 监控告警配置

### 交付物
- ✅ 集成测试全部通过
- ✅ 性能基准报告
- ✅ 监控告警系统配置
- ✅ 灰度发布文档

---

## 🚀 Week 7-8: 上线和稳定

### 目标
- 灰度发布从10% → 100%
- 稳定性验证
- Mock数据完全下线

### 灰度发布计划

```
Day 1-2: 灰度10%
  ├─ 10%用户使用Real数据
  ├─ 90%用户继续使用Mock数据
  ├─ 7x24监控关键指标
  └─ 预期成功率>99.9%

Day 3-4: 灰度50%
  ├─ 50%用户切换到Real数据
  ├─ 性能和可靠性验证
  ├─ 收集用户反馈
  └─ 预期成功率>99.95%

Day 5-7: 灰度100%
  ├─ 所有用户完全切换到Real数据
  ├─ Mock数据服务下线
  ├─ 清理Mock数据逻辑
  └─ 最终性能和稳定性验证

Day 8: 总结
  ├─ 性能基准对比
  ├─ 问题修复总结
  ├─ 优化建议
  └─ 项目总结报告
```

### 成功指标

| 指标 | 目标 | 验收 |
|------|------|------|
| **可用性** | >99.9% | P99延迟 < 1s |
| **错误率** | <0.1% | 任何单一故障时间 < 5分钟 |
| **响应时间** | P95 < 500ms | 与Mock数据延迟一致 |
| **数据准确率** | >99.99% | 数据验证无异常 |
| **用户反馈** | NPS > 8 | 无重大投诉 |

### 交付物
- ✅ Real数据对接完全上线
- ✅ 7x24监控系统运行
- ✅ Mock数据完全下线
- ✅ 性能优化报告
- ✅ 项目总结和lessons learned

---

## 📊 整体时间表

```
Week 0: 准备期 (当前)
  ├─ ✅ 架构评审完成
  ├─ ✅ 改进计划制定
  └─ ⏳ 启动P0改进

Week 1-2: P0改进 + 基础准备
  ├─ 4项P0改进全部完成
  ├─ 数据验证层实现
  ├─ DataSourceFactory完成
  └─ 测试覆盖率30%+

Week 3-4: 数据同步基础
  ├─ 增量同步机制
  ├─ 数据源切换框架
  └─ 实时数据流处理

Week 5-6: 验证和优化
  ├─ 集成测试>80%
  ├─ 性能测试和优化
  └─ 灰度发布准备

Week 7-8: 上线和稳定
  ├─ 灰度10% → 50% → 100%
  ├─ 稳定性验证
  └─ 项目完成
```

---

## 🎯 关键里程碑检查点

| 周期 | 里程碑 | 验收条件 |
|------|--------|----------|
| **Week 0** | 架构评审+计划制定 | ✅ 完成 |
| **Week 2** | P0改进完成 | 所有4项Task完成 |
| **Week 4** | Real数据同步就绪 | 增量同步通过测试 |
| **Week 6** | 性能优化完成 | P95 < 500ms |
| **Week 8** | 完全上线 | Mock数据下线 |

---

## 💡 风险管理

### Risk 1: Real数据质量不稳定
- **影响**: 下游分析和交易决策错误
- **缓解**:
  - 多层数据验证（格式→完整性→业务规则）
  - 多数据源交叉验证
  - 异常值检测和告警

### Risk 2: 数据源API限流或故障
- **影响**: 服务中断或性能下降
- **缓解**:
  - 熔断器 + 降级策略 (P0已实现)
  - 本地缓存 (24小时)
  - 多数据源冗余

### Risk 3: 数据库性能瓶颈
- **影响**: 大量数据写入时延迟增加
- **缓解**:
  - 批量写入（1000条/批）
  - 异步写入队列
  - 读写分离架构

### Risk 4: 数据同步延迟过大
- **影响**: 用户看到过期数据
- **缓解**:
  - 实时增量同步
  - WebSocket推送
  - 数据新鲜度指示

---

## 📞 联系和支持

- **架构设计**: Backend Architecture Team
- **数据同步**: Data Engineering Team
- **监控告警**: DevOps Team
- **测试验证**: QA Team

---

**项目状态**: Week 0准备中
**计划启动**: 下一个工作周
**预期完成**: Week 8（8周）

*最后更新: 2025-12-04*
