# 问财股票筛选功能集成规划

## 📋 文档信息

- **创建日期**: 2025-10-17
- **项目名称**: MyStocks - 问财筛选功能集成
- **目标**: 将AIstock项目的问财筛选功能集成到MyStocks Web后端的市场行情模块
- **状态**: 规划阶段

---

## 🎯 项目目标

将temp目录中的AIstock项目（问财股票筛选数据获取工具）集成到MyStocks Web后端，作为市场行情模块的二级页面功能。

### 核心功能
- 从问财(iwencai.com) Web API获取股票筛选结果
- 支持9个预定义查询语句（技术面、资金流、热度排行等）
- 智能去重和数据清理
- 存储到MySQL数据库
- 提供RESTful API供前端调用
- 支持定时自动刷新和后台任务调度

---

## 📊 现状分析

### AIstock项目特点

**优势**：
- ✅ 代码质量高（395行，完善的错误处理）
- ✅ 配置管理良好（环境变量驱动）
- ✅ 结构化日志系统
- ✅ 完整的数据清理和去重逻辑
- ✅ 9个经过验证的查询语句
- ✅ 完整的文档（README、QUICKSTART、IMPROVEMENTS）

**核心模块**：
1. `wencai_daily_run.py` (395行) - 主程序
   - `DBConfig` - 数据库配置管理
   - `get_wc_data()` - 问财API调用
   - `clean_column_names_and_values()` - 数据清理
   - `save_to_mysql()` - 数据存储（含去重）
   - `main()` - 主执行函数

2. `wencai_qs.py` - 查询语句库（9个查询）

### MyStocks Web后端架构

**技术栈**：
- FastAPI 0.115.0 + Uvicorn 0.30.0
- SQLAlchemy 2.0.35 (ORM)
- Pydantic 2.9.0 (数据验证)
- Celery 5.4.0 (异步任务)
- PostgreSQL + MySQL + TDengine + Redis

**现有市场行情模块**：
- 资金流向 (Fund Flow)
- ETF实时数据
- 竞价抢筹 (Chip Race)
- 龙虎榜 (Long Hu Bang)
- 实时行情 (Quotes)

**目录结构**：
```
web/backend/app/
├── api/              # API路由层
│   └── market.py     # 市场行情API（需扩展）
├── services/         # 业务逻辑层
│   └── market_data_service.py  # 市场数据服务（需扩展）
├── models/           # ORM模型
│   └── market_data.py  # 市场数据模型（需扩展）
├── schemas/          # Pydantic Schema
│   └── market_schemas.py  # 市场数据Schema（需扩展）
├── adapters/         # 数据源适配器
│   ├── akshare_extension.py
│   └── tqlex_adapter.py
└── tasks/            # 后台任务
    └── market_data.py  # 市场数据同步任务（需扩展）
```

---

## 🏗️ 集成架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Frontend                          │
│                    (市场行情二级页面)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (api/market.py)                           │   │
│  │  - GET  /api/market/wencai/queries                   │   │
│  │  - POST /api/market/wencai/query                     │   │
│  │  - GET  /api/market/wencai/results                   │   │
│  │  - POST /api/market/wencai/refresh/{query_name}      │   │
│  │  - GET  /api/market/wencai/history/{query_name}      │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Service Layer (services/wencai_service.py)          │   │
│  │  - fetch_wencai_data()                               │   │
│  │  - clean_and_deduplicate()                           │   │
│  │  - save_query_results()                              │   │
│  │  - get_query_history()                               │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Adapter Layer (adapters/wencai_adapter.py)          │   │
│  │  - WencaiDataSource (implements IDataSource)         │   │
│  │  - call_wencai_api()                                 │   │
│  │  - parse_response()                                  │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  ORM Models (models/wencai_data.py)                  │   │
│  │  - WencaiQuery (查询定义)                            │   │
│  │  - WencaiResult (查询结果)                           │   │
│  └──────────────────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Background Tasks (tasks/wencai_tasks.py)            │   │
│  │  - scheduled_wencai_refresh (Celery定时任务)         │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                      MySQL Database                          │
│  - wencai_queries (查询定义表)                               │
│  - wencai_qs_1 ~ wencai_qs_9 (9个结果表)                     │
└──────────────────────────────────────────────────────────────┘
```

### 2. 数据流

```
用户请求 → API端点 → Service层验证 → Adapter调用问财API
    → 数据清理 → 去重 → 存储MySQL → 返回结果
```

---

## 📂 新增文件清单

### 1. 适配器层
**文件**: `web/backend/app/adapters/wencai_adapter.py`
```python
"""
问财数据源适配器
实现IDataSource接口，提供统一的数据访问层
"""
class WencaiDataSource:
    - call_wencai_api(query: str, pages: int) -> pd.DataFrame
    - clean_column_names(data: pd.DataFrame) -> pd.DataFrame
    - parse_response(response: dict) -> pd.DataFrame
```

**依赖**:
- `interfaces/data_source.py` (IDataSource接口)
- `requests` (HTTP调用)
- `pandas` (数据处理)

---

### 2. 服务层
**文件**: `web/backend/app/services/wencai_service.py`
```python
"""
问财数据服务
业务逻辑：数据获取、清理、去重、存储
"""
class WencaiService:
    - fetch_and_save(query_name: str, pages: int = 1) -> Dict[str, Any]
    - get_query_results(query_name: str, limit: int = 100) -> List[Dict]
    - get_all_queries() -> List[Dict]
    - refresh_query(query_name: str) -> bool
    - get_query_history(query_name: str, days: int = 7) -> pd.DataFrame
```

**依赖**:
- `adapters/wencai_adapter.py`
- `models/wencai_data.py`
- SQLAlchemy Session

---

### 3. 数据模型
**文件**: `web/backend/app/models/wencai_data.py`
```python
"""
问财数据ORM模型
"""
class WencaiQuery(Base):
    """查询定义表"""
    __tablename__ = 'wencai_queries'

    id: int
    query_name: str          # qs_1 ~ qs_9
    query_text: str          # 查询语句
    description: str         # 查询说明
    is_active: bool          # 是否启用
    created_at: datetime
    updated_at: datetime

class WencaiResultBase(Base):
    """查询结果基类（动态表）"""
    __abstract__ = True

    id: int
    fetch_time: datetime     # 获取时间
    取数区间: str            # 查询时间区间
    # ... 动态字段（根据问财返回）
```

---

### 4. Pydantic Schema
**文件**: `web/backend/app/schemas/wencai_schemas.py`
```python
"""
问财API请求/响应Schema
"""
class WencaiQueryRequest(BaseModel):
    query_name: str          # qs_1 ~ qs_9
    pages: int = 1           # 获取页数

class WencaiQueryResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    total_records: int
    new_records: int
    duplicate_records: int

class WencaiResultItem(BaseModel):
    股票代码: str
    股票简称: str
    # ... 动态字段
    fetch_time: datetime

class WencaiQueryInfo(BaseModel):
    query_name: str
    query_text: str
    description: str
    is_active: bool
    last_fetch_time: Optional[datetime]
```

---

### 5. API路由
**文件**: `web/backend/app/api/wencai.py` (新文件)
```python
"""
问财API路由
"""
router = APIRouter(prefix="/api/market/wencai", tags=["wencai"])

@router.get("/queries")
async def get_all_queries() -> List[WencaiQueryInfo]:
    """获取所有可用查询列表"""

@router.post("/query")
async def execute_query(request: WencaiQueryRequest) -> WencaiQueryResponse:
    """执行指定查询并返回结果"""

@router.get("/results/{query_name}")
async def get_query_results(query_name: str, limit: int = 100):
    """获取指定查询的最新结果"""

@router.post("/refresh/{query_name}")
async def refresh_query(query_name: str, background_tasks: BackgroundTasks):
    """刷新指定查询的数据（后台任务）"""

@router.get("/history/{query_name}")
async def get_query_history(query_name: str, days: int = 7):
    """获取指定查询的历史数据"""
```

**扩展现有文件**: `web/backend/app/api/market.py`
```python
# 在现有market.py中添加问财相关端点的引用
from .wencai import router as wencai_router
app.include_router(wencai_router)
```

---

### 6. 后台任务
**文件**: `web/backend/app/tasks/wencai_tasks.py`
```python
"""
问财数据后台任务
"""
from celery import shared_task

@shared_task(name="wencai.refresh_query")
def refresh_wencai_query(query_name: str, pages: int = 1) -> Dict[str, Any]:
    """后台刷新指定查询"""

@shared_task(name="wencai.scheduled_refresh_all")
def scheduled_refresh_all_queries() -> Dict[str, int]:
    """定时刷新所有查询（每日9:00）"""

@shared_task(name="wencai.cleanup_old_data")
def cleanup_old_wencai_data(days: int = 30) -> int:
    """清理30天前的旧数据"""
```

**Celery Beat调度配置** (添加到 `celeryconfig.py`):
```python
beat_schedule = {
    'refresh-wencai-qs9-daily': {
        'task': 'wencai.scheduled_refresh_all',
        'schedule': crontab(hour=9, minute=0),  # 每天9:00
    },
    'cleanup-old-wencai-data': {
        'task': 'wencai.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 每天2:00
    },
}
```

---

### 7. 配置文件
**更新**: `web/backend/app/core/config.py`
```python
class Settings(BaseSettings):
    # ... 现有配置

    # 问财API配置
    WENCAI_TIMEOUT: int = 30
    WENCAI_RETRY_COUNT: int = 3
    WENCAI_DEFAULT_PAGES: int = 1
    WENCAI_API_URL: str = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"

    # 问财数据库配置（使用MySQL）
    WENCAI_DB_ENABLED: bool = True
    WENCAI_AUTO_REFRESH: bool = True
```

---

### 8. 数据库迁移脚本
**文件**: `web/backend/migrations/wencai_init.sql`
```sql
-- 创建问财查询定义表
CREATE TABLE IF NOT EXISTS wencai_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_name VARCHAR(20) NOT NULL UNIQUE,
    query_text TEXT NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_query_name (query_name),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入9个预定义查询
INSERT INTO wencai_queries (query_name, query_text, description) VALUES
('qs_1', '请列举出20天内出现过涨停，量比大于1.5倍以上，换手率大于3%，振幅小于5%，流通市值小于200亿的股票', '涨停+量比+换手率筛选'),
('qs_2', '请列出近2周内资金流入持续5天为正，且涨幅不超过5%的股票', '资金流入持续为正'),
('qs_3', '请列出近3个月内出现过5日平均换手率大于30%的股票', '高换手率'),
('qs_4', '20日涨跌幅小于10%，换手率小于10%，市值小于100亿元，周成交量环比增长率大于100%前20名，当日涨幅＜4%，排除ST', '成交量放量'),
('qs_5', '请列出2024年1月1日以来上市满10个月的股票里，平均换手率大于40%或者换手率标准差大于15%的股票', '新股高换手'),
('qs_6', '请列出现近1周内板块资金流入持续为正的板块名称', '板块资金流向'),
('qs_7', '请列出现价小于30元、平均换手率大于20%、交易天数不少于250天的股票', '低价活跃股'),
('qs_8', '今日热度前300', '热度排行'),
('qs_9', '请列出均线多头排列，10天内有过涨停板，非ST，日线MACD金叉且日线KDJ金叉的股票', '技术形态筛选');

-- 注意：wencai_qs_1 ~ wencai_qs_9 表会在首次查询时自动创建
```

---

### 9. 单元测试
**文件**: `web/backend/tests/test_wencai_service.py`
```python
"""
问财服务单元测试
"""
import pytest
from app.services.wencai_service import WencaiService
from app.adapters.wencai_adapter import WencaiDataSource

def test_fetch_wencai_data():
    """测试问财数据获取"""

def test_clean_and_deduplicate():
    """测试数据清理和去重"""

def test_save_query_results():
    """测试查询结果保存"""

def test_get_all_queries():
    """测试获取所有查询列表"""
```

---

## 🔄 集成步骤

### Phase 1: 基础集成（核心功能）

#### Step 1.1: 创建适配器层
- [ ] 创建 `adapters/wencai_adapter.py`
- [ ] 实现 `WencaiDataSource` 类
- [ ] 迁移 `get_wc_data()` 和 `clean_column_names_and_values()` 函数
- [ ] 添加错误处理和重试机制

#### Step 1.2: 创建数据模型
- [ ] 创建 `models/wencai_data.py`
- [ ] 定义 `WencaiQuery` 和 `WencaiResultBase` 模型
- [ ] 创建数据库迁移脚本

#### Step 1.3: 创建服务层
- [ ] 创建 `services/wencai_service.py`
- [ ] 实现 `WencaiService` 类
- [ ] 实现数据获取、清理、去重、存储逻辑

#### Step 1.4: 创建Pydantic Schema
- [ ] 创建 `schemas/wencai_schemas.py`
- [ ] 定义请求/响应Schema

#### Step 1.5: 创建API路由
- [ ] 创建 `api/wencai.py`
- [ ] 实现5个核心API端点
- [ ] 添加到主应用路由

---

### Phase 2: 后台任务集成

#### Step 2.1: 创建Celery任务
- [ ] 创建 `tasks/wencai_tasks.py`
- [ ] 实现3个后台任务

#### Step 2.2: 配置任务调度
- [ ] 更新 `celeryconfig.py`
- [ ] 添加定时任务配置（每日9:00刷新）

---

### Phase 3: 前端集成（可选，如有前端）

#### Step 3.1: 创建问财查询页面
- [ ] 创建查询列表页面
- [ ] 创建查询结果展示页面
- [ ] 添加手动刷新按钮

#### Step 3.2: 集成到市场行情模块
- [ ] 在市场行情导航中添加"问财筛选"入口
- [ ] 添加页面路由

---

### Phase 4: 测试和文档

#### Step 4.1: 单元测试
- [ ] 编写适配器测试
- [ ] 编写服务层测试
- [ ] 编写API端点测试

#### Step 4.2: 集成测试
- [ ] 端到端测试（API → Service → Adapter → 数据库）
- [ ] 后台任务测试

#### Step 4.3: 文档编写
- [ ] API文档（Swagger）
- [ ] 使用指南
- [ ] 开发者文档

---

## 📋 依赖管理

### 新增Python依赖

**已包含在requirements.txt中**（无需新增）：
- `requests>=2.28.0` ✅
- `pandas>=1.3.0` ✅
- `sqlalchemy>=2.0.35` ✅
- `pymysql>=1.1.0` ✅
- `python-dotenv>=0.19.0` ✅
- `celery>=5.4.0` ✅

### 配置环境变量

添加到 `.env` 文件：
```env
# 问财API配置
WENCAI_TIMEOUT=30
WENCAI_RETRY_COUNT=3
WENCAI_DEFAULT_PAGES=1
WENCAI_AUTO_REFRESH=true
```

---

## 🗄️ 数据库设计

### 表结构

#### 1. `wencai_queries` - 查询定义表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| query_name | VARCHAR(20) | 查询名称 (qs_1~qs_9) |
| query_text | TEXT | 查询语句 |
| description | VARCHAR(255) | 查询说明 |
| is_active | BOOLEAN | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### 2. `wencai_qs_1` ~ `wencai_qs_9` - 查询结果表（动态创建）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| fetch_time | TIMESTAMP | 获取时间 |
| 取数区间 | VARCHAR(50) | 查询时间区间 |
| ... | ... | 动态字段（根据问财返回） |

**索引策略**：
- `idx_fetch_time` - 查询时间索引（用于历史数据查询）
- `idx_stock_code` - 股票代码索引（如果包含）

---

## 🔐 安全和性能考虑

### 安全性

1. **API限流**: 添加问财API调用频率限制
   ```python
   from slowapi import Limiter

   @router.post("/query")
   @limiter.limit("10/minute")
   async def execute_query(...):
       ...
   ```

2. **认证和授权**: 继承现有的JWT认证机制
   ```python
   @router.post("/query", dependencies=[Depends(get_current_user)])
   async def execute_query(...):
       ...
   ```

3. **输入验证**: 使用Pydantic严格验证所有输入参数

### 性能优化

1. **缓存策略**: Redis缓存查询结果（15分钟）
   ```python
   @cache(expire=900)  # 15分钟缓存
   async def get_query_results(query_name: str):
       ...
   ```

2. **异步处理**: 使用FastAPI的后台任务处理长时间查询
   ```python
   @router.post("/refresh/{query_name}")
   async def refresh_query(background_tasks: BackgroundTasks):
       background_tasks.add_task(wencai_service.fetch_and_save, query_name)
       return {"status": "refreshing"}
   ```

3. **数据库优化**:
   - 使用批量插入（`chunksize=1000`）
   - 添加适当索引
   - 定期清理旧数据

---

## 📊 监控和日志

### 日志策略

继承现有的`structlog`配置：
```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("wencai_query_executed",
    query_name=query_name,
    total_records=len(data),
    new_records=len(new_data),
    duration=duration
)
```

### 监控指标

添加Prometheus指标：
```python
from prometheus_client import Counter, Histogram

wencai_query_total = Counter('wencai_query_total', 'Total Wencai queries')
wencai_query_duration = Histogram('wencai_query_duration_seconds', 'Wencai query duration')
```

---

## 🧪 测试策略

### 单元测试覆盖率目标: 80%

1. **适配器层**: Mock问财API响应
2. **服务层**: Mock适配器和数据库
3. **API层**: 使用TestClient测试端点

### 集成测试

使用pytest fixtures创建测试数据库：
```python
@pytest.fixture
def test_db():
    # 创建临时测试数据库
    yield db
    # 清理测试数据
```

---

## 📅 时间估算

| 阶段 | 任务 | 估算时间 |
|------|------|---------|
| Phase 1 | 基础集成（适配器+服务+API） | 6-8小时 |
| Phase 2 | 后台任务集成 | 2-3小时 |
| Phase 3 | 前端集成（如需） | 4-6小时 |
| Phase 4 | 测试和文档 | 3-4小时 |
| **总计** | | **15-21小时** |

---

## 🚀 部署清单

### 部署前检查

- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] API文档更新
- [ ] 环境变量配置完成
- [ ] 数据库迁移脚本准备好
- [ ] Celery任务配置完成

### 部署步骤

1. **数据库迁移**
   ```bash
   mysql -u root -p wencai < migrations/wencai_init.sql
   ```

2. **更新后端代码**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **重启服务**
   ```bash
   systemctl restart mystocks-backend
   systemctl restart celery-worker
   systemctl restart celery-beat
   ```

4. **验证部署**
   ```bash
   curl http://localhost:8020/api/market/wencai/queries
   ```

---

## 📚 参考文档

### 原始项目文档
- `/opt/claude/mystocks_spec/temp/README.md`
- `/opt/claude/mystocks_spec/temp/QUICKSTART.md`
- `/opt/claude/mystocks_spec/temp/IMPROVEMENTS.md`

### MyStocks现有文档
- `/opt/claude/mystocks_spec/web/backend/BACKEND_IMPLEMENTATION_SUMMARY.md`
- `/opt/claude/mystocks_spec/CLAUDE.md`

### API文档
- Swagger UI: `http://localhost:8020/api/docs`
- ReDoc: `http://localhost:8020/api/redoc`

---

## 🔄 后续改进建议

### 短期（1-2周）
- [ ] 添加更多查询语句（qs_10 ~ qs_20）
- [ ] 实现查询结果导出（Excel/CSV）
- [ ] 添加查询结果对比功能

### 中期（1-3个月）
- [ ] 支持自定义查询语句
- [ ] 集成同花顺问财（wenda.tdx.com.cn）
- [ ] 实现查询结果可视化图表

### 长期（3-6个月）
- [ ] AI辅助生成查询语句
- [ ] 回测系统集成
- [ ] 策略推荐引擎

---

## ✅ 验收标准

### 功能验收
- [ ] 9个预定义查询均可正常执行
- [ ] 数据去重逻辑正确工作
- [ ] API所有端点正常响应
- [ ] 后台任务正常调度
- [ ] 错误处理和日志完整

### 性能验收
- [ ] 单次查询响应时间 < 5秒
- [ ] API端点响应时间 < 200ms（缓存命中）
- [ ] 数据库写入速度 > 1000条/秒

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] 无严重安全漏洞
- [ ] 代码通过pylint检查
- [ ] API文档完整准确

---

## 📞 联系和支持

- **开发团队**: MyStocks Backend Team
- **文档维护**: Claude Code
- **问题反馈**: GitHub Issues

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2025-10-17 | 1.0.0 | 初始版本，完整的集成规划 | Claude Code |

---

**文档状态**: ✅ 已完成
**下一步**: 开始Phase 1 - 基础集成
