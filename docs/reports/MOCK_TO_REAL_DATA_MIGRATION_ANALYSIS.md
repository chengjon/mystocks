# Mock数据到真实数据迁移分析报告

**生成日期**: 2026-01-20
**分析范围**: 后端API + 前端页面
**目标**: 将所有Mock数据替换为真实API数据

---

## 📊 执行摘要

### 当前状态
- ✅ **环境配置**: `USE_MOCK_DATA=false` 已正确设置
- ✅ **Market V2 API**: 已使用真实数据（EastMoney + PostgreSQL）
- ❌ **Dashboard API**: 使用MockBusinessDataSource（硬编码数据）
- ❌ **其他API**: 16个文件仍在使用Mock数据

### 关键发现
1. **358个API端点**已注册在FastAPI中
2. **16个后端文件**仍在使用Mock数据
3. **10个前端文件**调用了Mock数据相关的API

---

## 🔍 详细分析

### 1. 后端API Mock数据使用情况

| 文件 | Mock类型 | 严重性 | 影响范围 |
|------|---------|--------|----------|
| **dashboard.py** | MockBusinessDataSource | 🔴 P0 | Dashboard首页 |
| **market.py** | mock.unified_mock_data | 🔴 P0 | 市场行情数据 |
| **monitoring.py** | mock.unified_mock_data | 🟡 P1 | 监控数据 |
| **stock_search.py** | mock.unified_mock_data | 🟡 P1 | 股票搜索 |
| **tradingview.py** | mock.unified_mock_data | 🟡 P1 | TradingView组件 |
| **wencai.py** | mock.unified_mock_data | 🟡 P2 | 问财选股 |
| **strategy_management.py** | mock.unified_mock_data | 🟡 P2 | 策略管理 |
| **其他9个文件** | 少量Mock使用 | 🟢 P3 | 影响较小 |

**详细统计**:
```
总计16个文件使用Mock数据:
- MockBusinessDataSource类: 1个文件
- mock.unified_mock_data导入: 9个文件
- USE_MOCK_DATA检查: 8个文件
- 硬编码股票数据: 8个文件
```

### 2. 前端页面API调用情况

| 文件 | 调用的API | 使用Mock数据 |
|------|-----------|-------------|
| `src/views/EnhancedDashboard.vue` | `/api/dashboard/market-overview` | ✅ 是 |
| `src/views/artdeco-pages/ArtDecoTradingCenter.vue` | `/api/dashboard/summary` | ✅ 是 |
| `src/views/demo/Phase4Dashboard.vue` | dashboard APIs | ✅ 是 |
| `src/views/SmartDataSourceTest.vue` | 测试多种API | ⚠️ 部分是 |
| `src/views/converted.archive/dashboard.vue` | dashboard APIs | ✅ 是（已归档） |

### 3. API端点数据来源验证

#### ✅ 使用真实数据的API
| API端点 | 数据来源 | 验证方法 |
|---------|---------|----------|
| `/api/market/v2/etf/list` | PostgreSQL + EastMoney | ✅ 有id和created_at |
| `/api/market/v2/fund-flow` | PostgreSQL + EastMoney | ✅ 数据库记录 |
| `/api/market/v2/lhb` | PostgreSQL + EastMoney | ✅ 数据库记录 |
| `/api/announcement/list` | 真实公告数据 | ✅ API响应 |
| `/api/cache/*` | Redis缓存 | ✅ 缓存系统 |

#### ❌ 使用Mock数据的API
| API端点 | Mock来源 | 需要替换 |
|---------|---------|----------|
| `/api/dashboard/market-overview` | MockBusinessDataSource | ✅ 需要Market V2 API |
| `/api/dashboard/summary` | MockBusinessDataSource | ✅ 需要多个真实API |
| `/api/market/sectors` | mock.unified_mock_data | ✅ 需要真实行业数据 |
| `/api/indicators/registry` | 硬编码指标列表 | ✅ 需要数据库查询 |
| 其他监控类API | mock.unified_mock_data | ⚠️ 待确认 |

---

## 🎯 迁移计划

### 阶段1: Dashboard API迁移（P0 - 最高优先级）

**目标**: 替换Dashboard API中的MockBusinessDataSource

**文件**: `web/backend/app/api/dashboard.py`

**当前实现**:
```python
class MockBusinessDataSource:
    def get_dashboard_summary(self, user_id: int, trade_date: Optional[date] = None):
        return {
            "data_source": "mock_composite",
            "market_overview": { ... }  # 硬编码数据
        }
```

**迁移方案**:

#### 1.1 Market Overview数据迁移
```python
# 替换为:
async def get_market_overview_real() -> dict:
    """从真实API获取市场概览数据"""
    # 调用market_v2 API获取ETF数据作为市场概览
    from app.services.market_data_service_v2 import get_market_data_service_v2

    service = get_market_data_service_v2()

    # 获取主要指数（从ETF或专门指数API）
    # 需要实现: get_major_indices() 方法

    return real_data
```

**需要的API端点**:
- ✅ `/api/market/v2/etf/list` - 已有
- ❌ `/api/market/v2/indices/list` - **缺失，需要补充**
- ❌ `/api/market/v2/market-stats` - **缺失，需要补充**

#### 1.2 Watchlist数据迁移
```python
# 替换为:
async def get_watchlist_real(user_id: int) -> list:
    """从数据库获取用户自选股"""
    from app.api.monitoring_watchlists import get_watchlist_service

    service = get_watchlist_service()
    return await service.get_user_watchlist(user_id)
```

**需要的API端点**:
- ✅ `/api/v1/watchlists/{user_id}` - 已有（monitoring_watchlists.py）

#### 1.3 Portfolio数据迁移
```python
# 替换为:
async def get_portfolio_real(user_id: int) -> dict:
    """从数据库获取用户持仓"""
    # 调用持仓相关API
    pass
```

**需要的API端点**:
- ❌ `/api/v1/portfolio/{user_id}` - **缺失，需要补充**

#### 1.4 Risk Alerts数据迁移
```python
# 替换为:
async def get_risk_alerts_real(user_id: int) -> list:
    """从数据库获取风险预警"""
    from app.api.risk_management import get_alert_service

    service = get_alert_service()
    return await service.get_user_alerts(user_id)
```

**需要的API端点**:
- ✅ `/api/v1/risk/alerts` - 已有（risk_management.py）

### 阶段2: Market API迁移（P0）

**目标**: 替换market.py中的mock.unified_mock_data

**文件**: `web/backend/app/api/market.py`

**迁移方案**:
- 删除 `from app.mock.unified_mock_data import get_mock_data`
- 改为调用 `MarketDataServiceV2` 或创建真实的服务方法
- 使用已有的Market V2 API端点

### 阶段3: 其他API迁移（P1-P2）

**按优先级顺序**:
1. **monitoring.py** - 监控数据（P1）
2. **stock_search.py** - 股票搜索（P1）
3. **tradingview.py** - TradingView（P1）
4. **strategy_management.py** - 策略管理（P2）
5. **wencai.py** - 问财选股（P2）

---

## 🚨 缺失的API端点清单

### 需要补充的API端点

| 优先级 | API端点 | 功能 | 建议 |
|--------|---------|------|------|
| **P0** | `GET /api/market/v2/indices/list` | 获取主要指数列表 | 新增，复用MarketDataServiceV2 |
| **P0** | `GET /api/market/v2/market-stats` | 获取市场统计数据 | 新增，聚合计算 |
| **P0** | `GET /api/v1/portfolio/{user_id}` | 获取用户持仓 | 新增或启用已存在代码 |
| **P1** | `GET /api/analysis/industry/list` | 获取行业列表 | 检查是否已实现 |
| **P1** | `GET /api/analysis/concept/list` | 获取概念列表 | 检查是否已实现 |
| **P2** | `GET /api/strategy/{user_id}/active` | 获取用户活跃策略 | 新增 |
| **P2** | `GET /api/stock/search` | 股票搜索 | 检查是否已有实现 |

### 现有可用API（可直接使用）

| API端点 | 功能 | 数据来源 |
|---------|------|----------|
| `/api/market/v2/etf/list` | ETF列表 | ✅ Real |
| `/api/market/v2/fund-flow` | 资金流向 | ✅ Real |
| `/api/market/v2/lhb` | 龙虎榜 | ✅ Real |
| `/api/v1/watchlists/*` | 自选股管理 | ✅ Real |
| `/api/announcement/list` | 公告列表 | ✅ Real |
| `/api/v1/risk/*` | 风险管理 | ✅ Real |

---

## 📋 实施步骤

### Step 1: 补充缺失的API端点
1. 创建 `/api/market/v2/indices/list` 端点
2. 创建 `/api/market/v2/market-stats` 端点
3. 启用或创建 `/api/v1/portfolio/{user_id}` 端点
4. 验证行业和概念列表API

### Step 2: 重构Dashboard API
1. 修改 `dashboard.py` 中的 `get_data_source()`
2. 替换 `MockBusinessDataSource` 为真实数据服务
3. 更新 `get_dashboard_summary()` 调用真实API
4. 测试Dashboard页面功能

### Step 3: 迁移Market API
1. 移除 `market.py` 中的mock导入
2. 替换 `get_mock_data()` 调用为真实服务
3. 验证市场行情数据正确显示

### Step 4: 迁移其他API
1. 按优先级逐个迁移
2. 监控 → 股票搜索 → TradingView → 策略管理
3. 每个API迁移后进行测试

### Step 5: 清理Mock代码
1. 删除 `app/mock/unified_mock_data.py`
2. 删除或Mock相关的测试文件
3. 更新文档

---

## ⚙️ 技术实现细节

### 新增API端点示例

#### 1. 指数列表API
```python
# 在 market_v2.py 中添加

@router.get("/indices/list", summary="获取主要指数列表")
async def get_indices_list(
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    获取上证指数、深证成指、创业板指等主要指数实时行情

    Returns:
        指数列表数据
    """
    try:
        service = get_market_data_service_v2()

        # 方法需要实现: query_major_indices()
        results = service.query_major_indices(limit)

        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. 市场统计API
```python
@router.get("/market-stats", summary="获取市场统计数据")
async def get_market_stats():
    """
    获取市场整体统计数据：上涨/下跌/平盘数量、成交额等

    Returns:
        市场统计数据
    """
    try:
        service = get_market_data_service_v2()

        # 方法需要实现: get_market_statistics()
        stats = service.get_market_statistics()

        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### MarketDataServiceV2 需要新增的方法

```python
# 在 market_data_service_v2.py 中添加

def query_major_indices(self, limit: int = 10) -> List[Dict]:
    """
    查询主要指数行情

    需要实现的指数:
    - 000001: 上证指数
    - 399001: 深证成指
    - 399006: 创业板指
    - 000300: 沪深300
    - 000016: 上证50
    """
    # TODO: 从EastMoney或数据库获取指数数据
    pass

def get_market_statistics(self) -> Dict:
    """
    获取市场统计数据

    Returns:
        {
            "up_count": 上涨数量,
            "down_count": 下跌数量,
            "flat_count": 平盘数量,
            "total_volume": 总成交量,
            "total_turnover": 总成交额,
            "limit_up": 涨停数量,
            "limit_down": 跌停数量
        }
    """
    # TODO: 从数据库聚合计算
    pass
```

---

## 🎯 预期成果

### 完成迁移后
- ✅ **0个** 文件使用MockBusinessDataSource
- ✅ **0个** 文件导入mock.unified_mock_data
- ✅ **100%** Dashboard数据来自真实API
- ✅ **100%** Market数据来自真实API
- ✅ **配置驱动**: 通过 `USE_MOCK_DATA=false` 完全禁用Mock数据

### 性能影响
- ⚠️ **响应时间**: 可能略微增加（需测试）
- ✅ **数据新鲜度**: 显著提升（实时数据）
- ✅ **数据准确性**: 显著提升（真实市场数据）

---

## 📞 需要用户补充的内容

根据以上分析，以下API端点**需要您补充**：

### 🔴 P0 - 最高优先级（Dashboard必需）

1. **指数列表API**
   - 路径: `/api/market/v2/indices/list`
   - 功能: 返回上证指数、深证成指、创业板指等主要指数
   - 数据来源: 建议从EastMoney获取，或从TDengine/PostgreSQL查询

2. **市场统计API**
   - 路径: `/api/market/v2/market-stats`
   - 功能: 返回上涨/下跌/平盘股票数量、总成交额等
   - 数据来源: 从PostgreSQL市场数据表聚合计算

3. **用户持仓API**
   - 路径: `/api/v1/portfolio/{user_id}`
   - 功能: 返回用户持仓数据
   - 数据来源: PostgreSQL持仓表

### 🟡 P1 - 高优先级（功能增强）

4. **行业列表API验证**
   - 路径: `/api/analysis/industry/list`
   - 当前状态: 端点存在但返回空数据
   - 需要: 验证实现或补充数据

5. **概念列表API验证**
   - 路径: `/api/analysis/concept/list`
   - 当前状态: 端点存在但返回空数据
   - 需要: 验证实现或补充数据

### 🟢 P2 - 中等优先级（锦上添花）

6. **策略列表API**
   - 路径: `/api/strategy/{user_id}/active`
   - 功能: 返回用户活跃策略
   - 数据来源: PostgreSQL策略表

---

## 📊 迁移进度跟踪

| 阶段 | 任务 | 状态 | 预计工作量 |
|------|------|------|-----------|
| P0 | 补充指数列表API | ⏳ 待开始 | 2-3小时 |
| P0 | 补充市场统计API | ⏳ 待开始 | 2-3小时 |
| P0 | 补充用户持仓API | ⏳ 待开始 | 3-4小时 |
| P0 | 重构Dashboard API | ⏳ 待开始 | 4-5小时 |
| P1 | 迁移Market API | ⏳ 待开始 | 2-3小时 |
| P1 | 迁移Monitoring API | ⏳ 待开始 | 2-3小时 |
| P2 | 迁移其他API | ⏳ 待开始 | 4-6小时 |
| - | 清理Mock代码 | ⏳ 待开始 | 1-2小时 |
| - | 测试和验证 | ⏳ 待开始 | 3-4小时 |

**总计估计**: 23-33小时（约3-4个工作日）

---

## 🔗 相关文档

- API端点统计报告: `docs/guides/API_ENDPOINTS_STATISTICS_REPORT.md`
- 数据源管理工具: `docs/guides/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`
- Mock数据使用规则: `docs/guides/MOCK_DATA_USAGE_RULES.md`
- 前端API文档: `web/frontend/src/api/types/`

---

**报告生成**: 2026-01-20
**分析工具**: Python脚本自动化分析
**下一步**: 等待用户确认补充API端点后开始实施
