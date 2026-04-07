# Real数据对接 - 核心原则与最佳实践

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


> **⚠️ 历史参考文档**
>
> 本文档已被更新的环境切换指南部分替代。建议优先阅读：
> - **[Mock/Real数据切换指南](./mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md)** - 完整的环境切换方案
> - **[环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)** - 技术实现细节
>
> 本文档保留作为架构原则的历史参考。

**制定日期**: 2025-12-04
**重要性**: 🔴 CRITICAL - 这些原则决定了整个Real数据对接项目的成败
**核心理念**: 并行开发Real数据 + 保留Mock的完整隔离 + 零风险切换

---

## 🎯 核心原则概览

```
┌─────────────────────────────────────────────────────────┐
│         Real 数据对接核心原则（4大支柱）                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣ 架构隔离                                             │
│     └─ Mock 与 Real 代码零耦合                           │
│     └─ 统一入口点控制数据源切换                           │
│     └─ 物理隔离 + 清晰边界标注                           │
│                                                         │
│  2️⃣ 兼容现有 API                                        │
│     └─ 100% 复用现有接口契约                             │
│     └─ 入参/出参格式完全一致                             │
│     └─ 仅替换 "数据来源"，不修改接口                     │
│                                                         │
│  3️⃣ 处理 Real 特性差异                                  │
│     └─ 异常场景兼容（超时、错误、为空）                  │
│     └─ 异步/同步差异适配                                │
│     └─ 权限/鉴权差异处理                                │
│     └─ 性能差异兜底                                    │
│                                                         │
│  4️⃣ 并行开发流程                                        │
│     └─ USE_MOCK 开关单一职责                            │
│     └─ Real 代码独立提交                                │
│     └─ 永远不删除 Mock 代码                             │
│     └─ 故障排查时保留 Mock 回退能力                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 架构隔离原则

### 1.1 核心要求

#### ❌ 错误做法（严禁）
```python
# ❌ WRONG: Mock/Real 逻辑混在接口里
@router.get("/api/v1/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    if os.getenv('USE_MOCK') == 'true':
        # Mock 逻辑
        return {"symbol": symbol, "price": 100.0}
    else:
        # Real 逻辑
        return await fetch_from_akshare(symbol)

# ❌ WRONG: 在多个地方重复判断 USE_MOCK
if USE_MOCK:
    # ... 10行 Mock 代码
else:
    # ... 15行 Real 代码
```

#### ✅ 正确做法
```python
# ✅ CORRECT: 统一入口点，工厂模式控制
from app.core.data_source_factory import get_data_source

@router.get("/api/v1/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    # 统一从工厂获取数据源，无需关心是 Mock 还是 Real
    data_source = get_data_source()
    return await data_source.get_stock_info(symbol)
```

### 1.2 实现策略

#### 数据源工厂模式
```python
# app/core/data_source_factory.py

from enum import Enum
from typing import Union
import os

class DataSourceType(Enum):
    MOCK = "mock"
    REAL = "real"

class IDataSource(ABC):
    """数据源统一接口"""

    @abstractmethod
    async def get_stock_info(self, symbol: str) -> dict:
        pass

    @abstractmethod
    async def fetch_ohlcv(self, symbols: list, ...) -> dict:
        pass

class MockDataSource(IDataSource):
    """Mock 数据源实现"""
    # 所有 Mock 逻辑集中在这个类
    pass

class RealDataSource(IDataSource):
    """Real 数据源实现"""
    # 所有 Real 逻辑集中在这个类
    pass

# 全局单例 - 统一控制切换入口
_current_source = None

def get_data_source() -> IDataSource:
    """获取当前数据源"""
    global _current_source

    if _current_source is None:
        use_mock = os.getenv('USE_MOCK', 'true').lower() == 'true'
        _current_source = MockDataSource() if use_mock else RealDataSource()

    return _current_source

def switch_data_source(source_type: DataSourceType):
    """手动切换数据源（用于测试）"""
    global _current_source
    _current_source = (
        MockDataSource() if source_type == DataSourceType.MOCK
        else RealDataSource()
    )
```

### 1.3 代码物理隔离

```
app/
├── api/                    # 接口层，与数据源无关
│   └── stock.py
│
├── services/               # 业务逻辑层，使用工厂获取数据源
│   └── stock_service.py
│
├── core/
│   ├── data_source_factory.py  # 🔑 统一入口点
│   └── interfaces/
│       └── data_source.py      # 数据源接口定义
│
└── data_sources/
    ├── __init__.py
    ├── mock/
    │   ├── __init__.py
    │   ├── timeseries_mock.py  # Mock 时序数据
    │   ├── stock_mock.py       # Mock 股票数据
    │   └── README.md           # Mock 数据说明
    │
    └── real/
        ├── __init__.py
        ├── akshare_adapter.py  # Real 数据源适配
        ├── tushare_adapter.py  # Real 数据源适配
        └── README.md           # Real 数据源说明
```

### 1.4 清晰边界标注

```python
# app/data_sources/mock/stock_mock.py

"""
=================================================================
🔴 MOCK DATA ONLY - DO NOT USE IN PRODUCTION
这是仅用于开发和测试的 Mock 数据模块

关键说明:
1. 所有数据都是模拟数据，不反映真实市场
2. 上线前必须切换到 Real 数据源（USE_MOCK=false）
3. 这个文件在 Mock 模式下线时可以删除，但开发期间必须保留
4. 不允许在业务逻辑中直接导入此模块
=================================================================
"""

class StockMockDataSource:
    """Mock 股票数据源"""

    # 所有 Mock 逻辑都在这里，不会污染其他代码

    async def get_stock_info(self, symbol: str) -> dict:
        """返回 Mock 股票信息"""
        return {
            "symbol": symbol,
            "name": f"Mock {symbol}",
            "price": 100.0,
            "source": "MOCK"  # 🔑 标记数据来源
        }
```

---

## 2️⃣ 兼容现有API原则

### 2.1 API 契约不变

#### 约束条件
- ✅ 请求参数格式完全相同
- ✅ 响应字段完全相同
- ✅ HTTP 状态码完全相同
- ✅ 错误消息格式完全相同
- ❌ 不修改接口路径
- ❌ 不修改请求方法
- ❌ 不修改响应结构

#### 实例对比

```python
# ==================== Mock 模式 ====================
# 请求
GET /api/v1/stock/AAPL/info
Authorization: Bearer token

# 响应 (200 OK)
{
    "code": "SUCCESS",
    "message": "Stock info fetched successfully",
    "data": {
        "symbol": "AAPL",
        "name": "Apple Inc",
        "price": 150.25,
        "change": 0.5,
        "change_percent": 0.33,
        "market_cap": 2500000000000,
        "pe_ratio": 25.5
    },
    "timestamp": "2025-12-04T10:00:00Z"
}

# ==================== Real 模式 ====================
# 完全相同的请求
GET /api/v1/stock/AAPL/info
Authorization: Bearer token

# 完全相同的响应格式（仅数据来源不同）
{
    "code": "SUCCESS",
    "message": "Stock info fetched successfully",
    "data": {
        "symbol": "AAPL",
        "name": "Apple Inc",
        "price": 150.35,      # 来自真实市场
        "change": 0.6,         # 来自真实市场
        "change_percent": 0.40,
        "market_cap": 2510000000000,
        "pe_ratio": 25.8
    },
    "timestamp": "2025-12-04T10:00:00Z"
}
```

### 2.2 数据适配层

```python
# app/data_sources/real/adapters/response_adapter.py

"""
Real 数据源响应适配层
将 Real API 的不同响应格式适配为统一的 API 格式
"""

class ResponseAdapter:
    """响应适配器 - 将 Real 数据转换为 API 格式"""

    @staticmethod
    def adapt_stock_info(real_data: dict) -> dict:
        """
        将 Akshare 响应适配为 API 格式

        Akshare 格式:
        {
            "ts_code": "000001.SZ",
            "name": "平安银行",
            "close": 10.5
        }

        API 格式:
        {
            "symbol": "000001",
            "name": "平安银行",
            "price": 10.5
        }
        """

        # 字段映射
        adapted = {
            "symbol": real_data.get("ts_code", "").split(".")[0],
            "name": real_data.get("name", ""),
            "price": float(real_data.get("close", 0)),
            # ... 其他字段映射
        }

        # 数据验证
        required_fields = ["symbol", "name", "price"]
        for field in required_fields:
            if not adapted.get(field):
                raise DataValidationError(f"Missing required field: {field}")

        return adapted
```

### 2.3 错误处理一致性

```python
# app/data_sources/real/error_handler.py

"""
Real 数据源错误处理 - 确保错误格式与 API 一致
"""

def handle_real_api_error(error: Exception) -> dict:
    """
    将 Real API 的错误转换为标准 API 错误格式
    """

    # 获取错误信息
    error_msg = str(error)

    # 映射到标准错误码
    error_code_map = {
        "timeout": "TIMEOUT_ERROR",
        "connection": "CONNECTION_ERROR",
        "authentication": "AUTH_ERROR",
        "not_found": "NOT_FOUND",
        "rate_limit": "RATE_LIMIT_EXCEEDED"
    }

    # 确定错误码
    api_error_code = "DATA_FETCH_ERROR"  # 默认
    for keyword, code in error_code_map.items():
        if keyword in error_msg.lower():
            api_error_code = code
            break

    # 返回标准格式的错误响应
    return {
        "code": api_error_code,
        "message": f"Failed to fetch data: {error_msg}",
        "data": None
    }
```

---

## 3️⃣ 处理Real特性差异原则

### 3.1 异常场景兼容

#### 网络超时
```python
# app/data_sources/real/resilience.py

class TimeoutHandler:
    """处理 Real API 超时"""

    def __init__(self, timeout_sec: int = 30):
        self.timeout_sec = timeout_sec

    async def fetch_with_timeout(self, api_call):
        """带超时的 API 调用"""
        try:
            return await asyncio.wait_for(api_call, timeout=self.timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"Real API timeout after {self.timeout_sec}s")

            # 降级策略1: 返回缓存数据
            cached = await self.get_cached_data()
            if cached:
                return cached

            # 降级策略2: 返回 Mock 数据
            return await self.get_mock_data()

            # 降级策略3: 返回标准错误
            # raise TimeoutError("API unavailable, using fallback")
```

#### 接口报错处理
```python
# app/data_sources/real/error_recovery.py

class ErrorRecovery:
    """Real API 错误恢复"""

    async def fetch_with_retry(self, fetch_func, max_retries=3):
        """带重试的 API 调用"""

        for attempt in range(max_retries):
            try:
                return await fetch_func()
            except APIError as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    # 指数退避重试
                    await asyncio.sleep(2 ** attempt)
                    continue

                # 所有重试都失败，使用降级
                logger.warning(f"All {max_retries} attempts failed, using fallback")
                return await self.fallback_fetch()

    async def fallback_fetch(self):
        """降级策略"""
        # 1. 尝试缓存
        cached = await self.get_cached_data()
        if cached:
            return cached

        # 2. 使用 Mock 数据
        return await self.get_mock_data()
```

#### 数据为空处理
```python
# app/data_sources/real/data_validation.py

class DataValidator:
    """数据有效性验证"""

    def validate_response(self, data: dict, required_fields: list) -> bool:
        """验证响应数据"""

        # 检查必需字段
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False

        # 检查数据完整性
        if len(data) == 0:
            logger.warning("Empty data response")
            return False

        # 检查数据合理性（如价格为负）
        if isinstance(data.get("price"), (int, float)) and data["price"] < 0:
            logger.warning(f"Invalid price: {data['price']}")
            return False

        return True

    def get_safe_response(self, real_data: dict, fallback_data: dict) -> dict:
        """获取安全的响应"""

        if self.validate_response(real_data, ["symbol", "price"]):
            return real_data
        else:
            logger.info("Using fallback data")
            return fallback_data
```

### 3.2 异步/同步适配

```python
# app/data_sources/real/async_adapter.py

class AsyncSyncAdapter:
    """异步/同步适配层"""

    def __init__(self):
        self.event_loop = asyncio.new_event_loop()

    def sync_fetch(self, async_func, *args, **kwargs):
        """
        将异步函数适配为同步调用
        用于与 Mock 的同步接口兼容
        """
        return self.event_loop.run_until_complete(
            async_func(*args, **kwargs)
        )
```

### 3.3 权限/鉴权差异

```python
# app/data_sources/real/authentication.py

class RealAPIAuth:
    """Real API 鉴权处理"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self) -> dict:
        """获取包含鉴权的请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def fetch_with_auth(self, url: str, params: dict):
        """带鉴权的 API 调用"""
        try:
            headers = self.get_headers()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key")

                    return await response.json()
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            # 返回标准错误格式
            return {"code": "AUTH_ERROR", "message": str(e), "data": None}
```

### 3.4 性能差异兜底

```python
# app/data_sources/real/performance_handling.py

class PerformanceHandler:
    """处理 Real API 性能差异"""

    def __init__(self, cache_ttl: int = 3600):
        self.cache = {}
        self.cache_ttl = cache_ttl

    async def fetch_with_cache(self, key: str, fetch_func, use_cache=True):
        """带缓存的 API 调用"""

        # 检查缓存
        if use_cache and key in self.cache:
            cached_data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Using cached data for {key}")
                return cached_data

        # 获取新数据
        try:
            data = await fetch_func()
            # 缓存数据
            self.cache[key] = (data, time.time())
            return data
        except Exception as e:
            logger.warning(f"Fetch failed: {e}, trying cache")

            # 如果获取失败，返回过期缓存（如果存在）
            if key in self.cache:
                cached_data, _ = self.cache[key]
                logger.info(f"Using expired cache for {key}")
                return cached_data

            # 如果没有缓存，返回错误
            raise
```

---

## 4️⃣ 并行开发流程原则

### 4.1 开发流程

```
开发周期:

Mock 模式 (USE_MOCK=true)
  ├─ 周期1: Real 代码开发 (branch: feature/real-data-*)
  │  ├─ 实现 Real 数据源适配
  │  ├─ 编写 Real 相关测试
  │  └─ Real 代码单独提交 (git commit)
  │
  ├─ 周期2: 本地验证
  │  ├─ USE_MOCK=false 切换到 Real 模式
  │  ├─ 验证 Real 数据正常工作
  │  ├─ 对比 Mock 与 Real 的差异
  │  └─ 修复发现的问题
  │
  └─ 周期3: 集成到 Mock 模式
     ├─ USE_MOCK=true 回到 Mock 模式
     ├─ 验证 Mock 仍然正常工作
     ├─ Real 代码不影响 Mock
     └─ 提交 (Ready for Production)
```

### 4.2 USE_MOCK 开关的单一职责

```python
# app/core/config.py

import os

class Config:
    """全局配置"""

    # 🔑 单一职责: 仅用于控制数据源切换
    USE_MOCK = os.getenv('USE_MOCK', 'true').lower() == 'true'

    # ❌ 严禁添加其他用途的判断
    # 不允许:
    # if USE_MOCK:
    #     LOG_LEVEL = 'DEBUG'
    # else:
    #     LOG_LEVEL = 'INFO'
```

### 4.3 版本控制规范

#### 分支命名
```bash
# Real 数据相关开发
git checkout -b feature/real-data-akshare
git checkout -b feature/real-data-error-handling
git checkout -b feature/real-data-caching

# 修复 Real 相关问题
git checkout -b fix/real-data-timeout-handling
git checkout -b fix/real-data-validation
```

#### 提交消息规范
```bash
# Real 数据相关提交需要明确标注
git commit -m "feat(real-data): implement Akshare data source adapter"
git commit -m "feat(real-data): add error recovery for API timeouts"
git commit -m "test(real-data): write integration tests for Real mode"

# 不允许将 Real 和 Mock 改动混在一起
❌ git commit -m "feat: add real data and fix mock bug"
✅ git commit -m "feat(real-data): add Akshare adapter"
   git commit -m "fix(mock): fix mock data generation"
```

### 4.4 永不删除Mock代码

```python
# ❌ 错误: 即使 Real 完成也删除 Mock
git rm -r app/data_sources/mock/  # 严禁!

# ✅ 正确: 保留 Mock 代码，永远不删除
# 保留原因:
# 1. 故障时可快速回退
# 2. 新功能开发时可用 Mock 测试
# 3. CI/CD 流程中可用 Mock 验证
# 4. 历史参考和文档价值
```

### 4.5 本地开发工作流

```bash
# 1️⃣ 开发环境配置 (保留 Mock 开关)
cat > .env.local << 'EOF'
USE_MOCK=true          # 开发时默认使用 Mock
AKSHARE_ENABLED=false  # Real 数据源关闭
TUSHARE_ENABLED=false
EOF

# 2️⃣ 开发 Real 代码
# - 编写 Real 数据源适配
# - 编写相关测试
# - Mock 模式下验证不影响现有功能

# 3️⃣ 切换到 Real 模式验证 (本地测试)
cat > .env.local << 'EOF'
USE_MOCK=false         # 临时切换到 Real
AKSHARE_ENABLED=true   # 启用 Real 数据源
TUSHARE_ENABLED=true
EOF

# 运行测试验证 Real 数据
pytest tests/ -v

# 4️⃣ 切回 Mock 模式 (再次确认)
cat > .env.local << 'EOF'
USE_MOCK=true
AKSHARE_ENABLED=false
TUSHARE_ENABLED=false
EOF

# 5️⃣ 提交代码
git add -A
git commit -m "feat(real-data): implement data source adapter"
git push origin feature/real-data-*
```

---

## 📋 保证 Real 与 API 数据对齐的方案

### 1. 前置: 明确数据契约基准

```python
# docs/DATA_CONTRACT.md

"""
API 数据契约文档

所有接口的出参格式基于 Mock 数据生成的此契约
Real 数据必须完全符合此契约

示例: /api/v1/stock/{symbol}/info

模拟数据格式:
{
    "code": "SUCCESS",          # 状态码(必需)
    "message": "...",           # 消息(必需)
    "data": {
        "symbol": "AAPL",       # 股票代码(必需, string)
        "name": "Apple Inc",    # 公司名称(必需, string)
        "price": 150.25,        # 现价(必需, float)
        "change": 0.5,          # 涨跌(必需, float)
        "change_percent": 0.33, # 涨跌%(必需, float)
        "market_cap": 2.5e12,   # 市值(必需, float)
        "pe_ratio": 25.5        # PE(可选, float)
    },
    "timestamp": "2025-12-04T10:00:00Z"
}

Real 数据必须:
✅ 返回相同的字段
✅ 字段类型完全一致
✅ 必需字段非空
✅ 可选字段允许缺失(用 None/null)
✅ 使用相同的命名规范

Real 与 Mock 差异允许:
✅ 字段值不同（来自不同数据源）
✅ 时间戳更新到最新
✅ 部分字段可能缺失（用默认值替代）
"""
```

### 2. 开发中: 多层校验

#### 单元测试校验
```python
# tests/test_data_source_alignment.py

def test_real_vs_mock_structure():
    """验证 Real 与 Mock 的数据结构一致"""

    # 获取 Mock 数据
    mock_source = MockDataSource()
    mock_data = mock_source.get_stock_info("AAPL")

    # 获取 Real 数据
    real_source = RealDataSource()
    real_data = real_source.get_stock_info("AAPL")

    # 比较字段
    mock_fields = set(mock_data["data"].keys())
    real_fields = set(real_data["data"].keys())

    # Real 必须包含所有 Mock 的必需字段
    required_fields = {"symbol", "name", "price", "change", "change_percent"}
    assert required_fields.issubset(real_fields), \
        f"Missing fields in Real: {required_fields - real_fields}"

    # 比较字段类型
    for field in required_fields:
        mock_type = type(mock_data["data"][field])
        real_type = type(real_data["data"][field])
        assert mock_type == real_type, \
            f"Type mismatch for {field}: Mock={mock_type}, Real={real_type}"
```

#### 集成测试校验
```python
# tests/test_api_response_alignment.py

def test_api_response_same_in_mock_and_real():
    """验证 API 响应格式在 Mock 和 Real 模式下一致"""

    client = TestClient(app)

    # 1. Mock 模式请求
    os.environ['USE_MOCK'] = 'true'
    mock_response = client.get("/api/v1/stock/AAPL/info")
    mock_data = mock_response.json()

    # 2. Real 模式请求
    os.environ['USE_MOCK'] = 'false'
    real_response = client.get("/api/v1/stock/AAPL/info")
    real_data = real_response.json()

    # 3. 比较响应结构
    # 顶级字段必须相同
    assert set(mock_data.keys()) == set(real_data.keys()), \
        f"Response structure mismatch"

    # data 字段结构必须相同
    mock_data_fields = set(mock_data["data"].keys())
    real_data_fields = set(real_data["data"].keys())
    assert mock_data_fields == real_data_fields, \
        f"Data field mismatch: {mock_data_fields ^ real_data_fields}"

    # 恢复到 Mock 模式
    os.environ['USE_MOCK'] = 'true'
```

### 3. 自动化保障: CI/CD 集成

```yaml
# .github/workflows/data-alignment-check.yml

name: Data Alignment Check

on: [push, pull_request]

jobs:
  data-alignment:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Run Mock vs Real validation
        run: |
          pytest tests/test_data_source_alignment.py -v
          pytest tests/test_api_response_alignment.py -v

      - name: Generate alignment report
        run: |
          python scripts/generate_alignment_report.py

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: alignment-report
          path: reports/alignment_report.json
```

### 4. 异常兜底: 错误处理

```python
# app/data_sources/real/error_standardization.py

class ErrorStandardizer:
    """确保错误格式与 API 标准一致"""

    STANDARD_ERROR_FORMAT = {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "data": None
    }

    @staticmethod
    def standardize_error(error: Exception) -> dict:
        """将任何错误转换为标准格式"""

        error_code = "DATA_FETCH_ERROR"  # 默认错误码
        error_msg = str(error)

        # 根据错误类型映射到标准错误码
        error_mapping = {
            TimeoutError: "TIMEOUT_ERROR",
            ConnectionError: "CONNECTION_ERROR",
            ValueError: "VALIDATION_ERROR",
            AuthenticationError: "AUTH_ERROR",
            RateLimitError: "RATE_LIMIT_EXCEEDED"
        }

        for exc_type, code in error_mapping.items():
            if isinstance(error, exc_type):
                error_code = code
                break

        # 返回标准化错误响应
        return {
            "code": error_code,
            "message": error_msg,
            "data": None
        }
```

---

## ✅ 检查清单

在启动 Real 数据对接之前，确保所有这些检查都通过：

### 架构隔离
- [ ] 数据源工厂已实现（`data_source_factory.py`）
- [ ] Mock 和 Real 代码物理隔离在不同目录
- [ ] 接口都通过工厂获取数据源，无零散 if-else
- [ ] 所有 Mock 代码有清晰的边界注释

### API 兼容性
- [ ] 数据契约文档已准备（`DATA_CONTRACT.md`）
- [ ] Real 数据适配层已实现（response adapter）
- [ ] 错误处理格式与 API 标准一致
- [ ] 测试覆盖 Mock vs Real 数据格式

### Real 特性处理
- [ ] 超时处理已实现
- [ ] 错误恢复（重试+降级）已实现
- [ ] 数据验证层已实现
- [ ] 缓存策略已确定

### 开发流程
- [ ] 分支命名规范定义
- [ ] 提交消息规范定义
- [ ] USE_MOCK 开关只用于数据源切换
- [ ] Mock 代码删除清单已禁止

### 测试和验证
- [ ] 单元测试验证数据结构
- [ ] 集成测试验证 API 响应
- [ ] CI/CD pipeline 配置了对齐检查
- [ ] 手动测试流程文档化

---

## 🎯 立即行动

1. **制定团队规范**
   - 确认这些原则
   - 制定团队开发协议
   - 进行技术培训

2. **建立基础设施**
   - 实现数据源工厂
   - 准备数据契约文档
   - 配置 CI/CD 流程

3. **启动开发**
   - 第一阶段: 实现 Real 数据源适配
   - 第二阶段: 完整的错误处理和降级
   - 第三阶段: 充分的测试验证

4. **持续监控**
   - 定期检查 Mock/Real 对齐
   - 收集 Real 数据的问题反馈
   - 持续优化降级策略

---

**关键记住**:
🔑 **Mock 与 Real 完全隔离，通过工厂模式统一控制**
🔑 **API 契约100%不变，仅替换数据来源**
🔑 **并行开发，永远保留 Mock 回退能力**

*最后更新: 2025-12-04*
