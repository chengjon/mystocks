# 智能量化监控系统 - 快速参考卡片

> **版本**: v1.0 | **日期**: 2026-01-08

---

## 🚀 快速开始 (3分钟上手)

### 1. 数据库初始化

```bash
# 初始化监控数据库表结构
PGPASSWORD=c790414J psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks \
  -f scripts/migrations/001_monitoring_tables.sql
```

**预期结果**:
- ✅ 3个表创建成功 (`monitoring_watchlists`, `monitoring_watchlist_stocks`, `monitoring_health_scores`)
- ✅ 18个示例清单插入
- ✅ 5只示例股票插入

### 2. API测试

```bash
# 获取所有清单
curl -X GET "http://localhost:8000/api/v1/monitoring/watchlists?user_id=1"

# 获取单个清单
curl -X GET "http://localhost:8000/api/v1/monitoring/watchlists/1?user_id=1"

# 获取清单股票
curl -X GET "http://localhost:8000/api/v1/monitoring/watchlists/1/stocks?user_id=1"
```

---

## 📋 API端点清单

### 清单管理 (9个端点)

| 端点 | 方法 | 功能 | 测试命令 |
|------|------|------|----------|
| `/api/v1/monitoring/watchlists` | GET | 获取所有清单 | `curl "http://localhost:8000/api/v1/monitoring/watchlists?user_id=1"` |
| `/api/v1/monitoring/watchlists` | POST | 创建清单 | 见下方示例 |
| `/api/v1/monitoring/watchlists/{id}` | GET | 获取单个清单 | `curl "http://localhost:8000/api/v1/monitoring/watchlists/1?user_id=1"` |
| `/api/v1/monitoring/watchlists/{id}` | PUT | 更新清单 | - |
| `/api/v1/monitoring/watchlists/{id}` | DELETE | 删除清单 | 见下方示例 |
| `/api/v1/monitoring/watchlists/{id}/stocks` | GET | 获取清单股票 | `curl "http://localhost:8000/api/v1/monitoring/watchlists/1/stocks?user_id=1"` |
| `/api/v1/monitoring/watchlists/{id}/stocks` | POST | 添加股票 | 见下方示例 |
| `/api/v1/monitoring/watchlists/{id}/stocks/{code}` | DELETE | 移除股票 | 见下方示例 |

### 组合分析 (8个端点)

| 端点 | 方法 | 功能 | 测试命令 |
|------|------|------|----------|
| `/api/v1/monitoring/analysis/portfolio/{id}/summary` | GET | 获取组合概要 | `curl "http://localhost:8000/api/v1/monitoring/analysis/portfolio/1/summary"` |
| `/api/v1/monitoring/analysis/portfolio/{id}/health` | GET | 获取健康度详情 | - |
| `/api/v1/monitoring/analysis/portfolio/{id}/alerts` | GET | 获取预警列表 | - |
| `/api/v1/monitoring/analysis/portfolio/{id}/rebalance` | GET | 获取再平衡建议 | - |
| `/api/v1/monitoring/analysis/calculate` | POST | 计算健康度 | - |

---

## 📝 常用操作示例

### 创建清单

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring/watchlists?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "科技龙头精选",
    "watchlist_type": "manual",
    "risk_profile": {
      "risk_tolerance": "high",
      "max_drawdown_limit": 0.2
    }
  }'
```

### 添加股票到清单

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring/watchlists/1/stocks?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519.SH",
    "entry_price": 1850.00,
    "entry_reason": "macd_gold_cross",
    "stop_loss_price": 1750.00,
    "target_price": 2000.00,
    "weight": 0.30
  }'
```

### 删除清单

```bash
curl -X DELETE "http://localhost:8000/api/v1/monitoring/watchlists/18?user_id=1"
```

### 移除股票

```bash
curl -X DELETE "http://localhost:8000/api/v1/monitoring/watchlists/1/stocks/600519.SH?user_id=1"
```

---

## 🗄️ 数据库表结构

### monitoring_watchlists (清单主表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| user_id | INTEGER | 用户ID |
| name | VARCHAR(100) | 清单名称 |
| type | VARCHAR(20) | 类型: manual/strategy/benchmark |
| risk_profile | JSONB | 风控配置 |
| is_active | BOOLEAN | 是否激活 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### monitoring_watchlist_stocks (清单成员表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| watchlist_id | INTEGER | 清单ID |
| stock_code | VARCHAR(20) | 股票代码 |
| entry_price | DECIMAL(10,2) | 入库价格 |
| entry_at | TIMESTAMP | 入库时间 |
| entry_reason | VARCHAR(50) | 入库理由 |
| stop_loss_price | DECIMAL(10,2) | 止损价格 |
| target_price | DECIMAL(10,2) | 止盈价格 |
| weight | DECIMAL(5,4) | 权重 |
| is_active | BOOLEAN | 是否激活 |

### monitoring_health_scores (健康度评分表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| score_date | DATE | 评分日期 |
| total_score | DECIMAL(5,2) | 综合评分 |
| radar_scores | JSONB | 五维雷达分 |
| sortino_ratio | DECIMAL(10,4) | Sortino比率 |
| calmar_ratio | DECIMAL(10,4) | Calmar比率 |
| max_drawdown | DECIMAL(5,4) | 最大回撤 |
| max_drawdown_duration | INTEGER | 回撤持续期 |
| downside_deviation | DECIMAL(10,4) | 下行标准差 |
| market_regime | VARCHAR(20) | 市场环境 |

---

## 🐍 Python集成

```python
import asyncio
from src.monitoring.infrastructure.postgresql_async_v3 import (
    initialize_postgres_async,
    get_postgres_async
)

async def example():
    # 初始化连接
    await initialize_postgres_async()

    # 获取实例
    db = get_postgres_async()

    # 查询清单
    watchlists = await db.get_user_watchlists(user_id=1)
    for w in watchlists:
        print(f"{w['name']}: {w['type']}")

        # 查询股票
        stocks = await db.get_watchlist_stocks(w['id'])
        for s in stocks:
            print(f"  - {s['stock_code']} @ {s['entry_price']}")

asyncio.run(example())
```

---

## 🎨 Vue.js集成

```javascript
import axios from 'axios'

const API_BASE = '/api/v1/monitoring'

// 获取所有清单
const getWatchlists = async (userId = 1) => {
  const res = await axios.get(`${API_BASE}/watchlists`, {
    params: { user_id: userId }
  })
  return res.data.data
}

// 创建清单
const createWatchlist = async (data) => {
  const res = await axios.post(`${API_BASE}/watchlists`, data, {
    params: { user_id: 1 }
  })
  return res.data.data
}

// 添加股票
const addStock = async (watchlistId, stockData) => {
  const res = await axios.post(
    `${API_BASE}/watchlists/${watchlistId}/stocks`,
    stockData,
    { params: { user_id: 1 } }
  )
  return res.data.data
}
```

---

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `9002: 数据库未连接` | 监控数据库未初始化 | 重启后端服务 |
| `9000: 'MonitoringPostgreSQLAccess' object has no attribute 'xxx'` | 方法名错误 | 检查方法名拼写 |
| `403 Forbidden` | 缺少认证 | 添加Authorization头 |

---

## 📊 测试数据

系统已预置18个示例清单和5只股票：

**清单**:
- 核心科技股 (高风险, 最大回撤20%)
- 金融蓝筹 (中等风险, 最大回撤15%)
- 成长股精选 (低风险, 最大回撤25%)

**股票**:
- 600519.SH @ 1850.00 (贵州茅台)
- 000001.SZ @ 15.00 (平安银行)
- 000002.SZ @ 30.00 (万科A)
- 000333.SZ @ 8.50 (美的集团)
- 600000.SH @ 12.50 (浦发银行)

---

## 🔗 相关链接

- **完整文档**: `docs/reports/PORTFOLIO_MANAGEMENT_REDESIGN_SUMMARY.md`
- **数据库脚本**: `scripts/migrations/001_monitoring_tables.sql`
- **API文档**: `http://localhost:8000/api/docs`
- **前端页面**: `http://localhost:3000/#/portfolio`

---

**快速参考** | **完整指南**: 见详细文档 | **问题反馈**: 创建GitHub Issue
