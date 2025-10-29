# 数据集成示例：新增竞价抢筹数据展示

**场景**: 新功能 - 添加竞价抢筹 (Chip Race) 数据展示
**任务**: 从零开始实现完整的数据流: 数据库 → 后端 API → 前端 → UI
**时间**: 90 分钟 (包含完整 5 层验证)
**复杂度**: 中等 (涉及所有层)

---

## 📋 需求描述

### 功能需求
```
功能: 添加竞价抢筹数据展示页面
目的: 显示开盘竞价阶段大单抢筹的股票
数据源: cn_stock_chip_race_open 表
展示内容: 股票代码、名称、价格、抢筹金额、时间
```

### 验证标准

按照 5 层验证模型，确保:
1. **Layer 5**: 数据库有竞价抢筹数据
2. **Layer 2**: 后端 API 正确返回数据
3. **Layer 1**: 代码质量和单元测试通过
4. **Layer 3**: 集成测试验证数据流完整
5. **Layer 4**: UI 正确显示数据，无错误

---

## 🔍 5 层验证流程 (从底层到上层)

### Layer 5: 数据验证层 (确保数据源存在)

#### 5.1 连接数据库

```bash
source scripts/bash_aliases.sh
mt-db
```

#### 5.2 检查表是否存在

```sql
\dt cn_stock_chip_race_open
```

**输出**:
```
              List of relations
 Schema |          Name          | Type  |    Owner
--------+------------------------+-------+--------------
 public | cn_stock_chip_race_open | table | mystocks_user
(1 row)
```

✅ 表存在

#### 5.3 检查表结构

```sql
\d cn_stock_chip_race_open
```

**输出**:
```
                 Table "public.cn_stock_chip_race_open"
      Column      |         Type          | Collation | Nullable | Default
------------------+-----------------------+-----------+----------+---------
 stock_code       | character varying(10) |           | not null |
 stock_name       | character varying(50) |           |          |
 trade_date       | date                  |           | not null |
 open_price       | numeric(10,3)         |           |          |
 chip_amount      | numeric(15,2)         |           |          |
 chip_ratio       | numeric(5,2)          |           |          |
 created_at       | timestamp             |           |          | now()
```

✅ 表结构符合需求

#### 5.4 检查数据存在性

```sql
SELECT COUNT(*) as record_count FROM cn_stock_chip_race_open;
```

**输出**:
```
 record_count
--------------
          234
(1 row)
```

✅ 有数据

#### 5.5 检查数据时效性

```sql
SELECT MAX(trade_date) as latest_date FROM cn_stock_chip_race_open;
```

**输出**:
```
 latest_date
-------------
 2025-10-29
(1 row)
```

✅ 数据最新

#### 5.6 查看数据样本

```sql
SELECT
    stock_code,
    stock_name,
    trade_date,
    open_price,
    chip_amount / 10000 as chip_amount_万元,
    chip_ratio
FROM cn_stock_chip_race_open
WHERE trade_date = '2025-10-29'
ORDER BY chip_amount DESC
LIMIT 5;
```

**输出**:
```
 stock_code | stock_name | trade_date | open_price | chip_amount_万元 | chip_ratio
------------+------------+------------+------------+-----------------+------------
 000001     | 平安银行    | 2025-10-29 |      12.45 |         1234.56 |       5.67
 600519     | 贵州茅台    | 2025-10-29 |    1689.00 |         9876.54 |       3.21
 600036     | 招商银行    | 2025-10-29 |      45.78 |         5678.90 |       4.32
 000858     | 五粮液     | 2025-10-29 |     158.90 |         3456.78 |       2.89
 601318     | 中国平安    | 2025-10-29 |      68.12 |         2345.67 |       1.98
(5 rows)
```

✅ 数据合理

```sql
\q
```

**✅ Layer 5 通过** - 数据源准备就绪 (时间: 10 分钟)

---

### Layer 2: API 层验证 (创建并验证 API)

#### 2.1 创建后端 API

编辑 `web/backend/app/api/market_v3.py`:

```python
from fastapi import APIRouter, Query
from typing import List, Optional
from app.database import get_db_connection

router = APIRouter()

@router.get("/chip-race")
async def get_chip_race_data(
    limit: int = Query(default=10, ge=1, le=100),
    trade_date: Optional[str] = None
):
    """
    获取竞价抢筹数据

    Args:
        limit: 返回记录数 (1-100)
        trade_date: 交易日期 (YYYY-MM-DD)，默认最新

    Returns:
        竞价抢筹数据列表
    """
    conn = await get_db_connection()

    # 构建查询
    if trade_date:
        query = """
            SELECT
                stock_code,
                stock_name,
                trade_date,
                open_price,
                chip_amount,
                chip_ratio
            FROM cn_stock_chip_race_open
            WHERE trade_date = %s
            ORDER BY chip_amount DESC
            LIMIT %s;
        """
        params = (trade_date, limit)
    else:
        query = """
            SELECT
                stock_code,
                stock_name,
                trade_date,
                open_price,
                chip_amount,
                chip_ratio
            FROM cn_stock_chip_race_open
            WHERE trade_date = (
                SELECT MAX(trade_date) FROM cn_stock_chip_race_open
            )
            ORDER BY chip_amount DESC
            LIMIT %s;
        """
        params = (limit,)

    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()

    # 转换为字典列表
    data = [dict(zip(columns, row)) for row in results]

    return {"data": data}
```

#### 2.2 添加路由

编辑 `web/backend/app/main.py`:

```python
from fastapi import FastAPI
from app.api import market_v3

app = FastAPI()

# 注册路由
app.include_router(market_v3.router, prefix="/api/market/v3", tags=["market"])
```

#### 2.3 重启后端

```bash
# 后端自动重载 (--reload 模式)
# 或手动重启
cd web/backend
python -m uvicorn app.main:app --reload
```

#### 2.4 测试 API

```bash
source scripts/bash_aliases.sh
mt-api /api/market/v3/chip-race?limit=5
```

**输出**:
```json
HTTP/1.1 200 OK

{
    "data": [
        {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_date": "2025-10-29",
            "open_price": 12.45,
            "chip_amount": 12345600.00,
            "chip_ratio": 5.67
        },
        {
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "trade_date": "2025-10-29",
            "open_price": 1689.00,
            "chip_amount": 98765400.00,
            "chip_ratio": 3.21
        }
        // ... 更多数据
    ]
}
```

#### 2.5 验证数据不为空

```bash
mt-test-api /api/market/v3/chip-race?limit=5
```

**输出**:
```
Testing: /api/market/v3/chip-race?limit=5
✅ PASS
```

#### 2.6 验证参数验证

```bash
# 测试 limit 参数
http GET http://localhost:8000/api/market/v3/chip-race?limit=150
```

**期望**: 返回 422 (limit 最大 100)

```bash
# 测试 trade_date 参数
mt-api /api/market/v3/chip-race?trade_date=2025-10-28&limit=5
```

**期望**: 返回指定日期的数据

**✅ Layer 2 通过** - API 正确返回数据 (时间: 25 分钟)

---

### Layer 1: 代码层验证 (代码质量)

#### 1.1 编写单元测试

创建 `tests/unit/test_chip_race_api.py`:

```python
import pytest
from app.api.market_v3 import get_chip_race_data

@pytest.mark.asyncio
async def test_chip_race_returns_data():
    """测试竞价抢筹 API 返回数据"""
    result = await get_chip_race_data(limit=5)

    # 验证返回结构
    assert "data" in result
    assert isinstance(result["data"], list)

    # 验证数据不为空
    assert len(result["data"]) > 0
    assert len(result["data"]) <= 5

    # 验证数据字段完整
    first_item = result["data"][0]
    required_fields = [
        "stock_code", "stock_name", "trade_date",
        "open_price", "chip_amount", "chip_ratio"
    ]
    for field in required_fields:
        assert field in first_item, f"Missing field: {field}"

@pytest.mark.asyncio
async def test_chip_race_with_date():
    """测试带日期参数的竞价抢筹 API"""
    result = await get_chip_race_data(limit=10, trade_date="2025-10-29")

    assert "data" in result
    assert len(result["data"]) <= 10

    # 验证所有数据都是指定日期
    for item in result["data"]:
        assert item["trade_date"] == "2025-10-29"
```

#### 1.2 运行测试

```bash
pytest tests/unit/test_chip_race_api.py -v
```

**输出**:
```
tests/unit/test_chip_race_api.py::test_chip_race_returns_data PASSED      [50%]
tests/unit/test_chip_race_api.py::test_chip_race_with_date PASSED        [100%]

=============================== 2 passed in 0.45s ===============================
```

#### 1.3 代码质量检查

```bash
black web/backend/app/api/market_v3.py
flake8 web/backend/app/api/market_v3.py
```

**输出**:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

**✅ Layer 1 通过** - 代码质量和测试通过 (时间: 15 分钟)

---

### Layer 4: 用户界面层 (创建前端页面)

#### 4.1 创建前端组件

创建 `web/frontend/src/views/ChipRaceView.vue`:

```vue
<template>
  <div class="chip-race">
    <h2>竞价抢筹</h2>
    <p class="description">开盘竞价阶段大单抢筹的股票</p>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <table v-else class="chip-race-table">
      <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>开盘价</th>
          <th>抢筹金额 (万元)</th>
          <th>抢筹占比 (%)</th>
          <th>日期</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in chipData" :key="item.stock_code">
          <td>{{ item.stock_code }}</td>
          <td>{{ item.stock_name }}</td>
          <td>{{ formatPrice(item.open_price) }}</td>
          <td class="chip-amount">{{ formatAmount(item.chip_amount) }}</td>
          <td>{{ formatRatio(item.chip_ratio) }}</td>
          <td>{{ item.trade_date }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="chipData.length === 0 && !loading && !error" class="no-data">
      暂无数据
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChipRaceView',
  data() {
    return {
      chipData: [],
      loading: false,
      error: null
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/market/v3/chip-race?limit=20')

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        this.chipData = result.data || []

        if (this.chipData.length === 0) {
          this.error = '暂无竞价抢筹数据'
        }
      } catch (error) {
        console.error('Failed to fetch chip race data:', error)
        this.error = '加载数据失败，请稍后重试'
        this.chipData = []
      } finally {
        this.loading = false
      }
    },
    formatPrice(value) {
      return value ? value.toFixed(2) : '-'
    },
    formatAmount(value) {
      // 转换为万元
      return value ? (value / 10000).toFixed(2) : '-'
    },
    formatRatio(value) {
      return value ? value.toFixed(2) : '-'
    }
  }
}
</script>

<style scoped>
.chip-race {
  padding: 20px;
}

.description {
  color: #666;
  margin-bottom: 20px;
}

.chip-race-table {
  width: 100%;
  border-collapse: collapse;
}

.chip-race-table th,
.chip-race-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

.chip-race-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.chip-amount {
  color: #e74c3c;  /* 红色强调抢筹金额 */
  font-weight: bold;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}

.error {
  color: #e74c3c;
}
</style>
```

#### 4.2 添加路由

编辑 `web/frontend/src/router/index.js`:

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import ChipRaceView from '../views/ChipRaceView.vue'

const routes = [
  // ... 其他路由
  {
    path: '/market/chip-race',
    name: 'chip-race',
    component: ChipRaceView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

#### 4.3 重新编译前端

```bash
cd web/frontend
npm run build
```

#### 4.4 验证 UI 显示

**访问页面**: `http://localhost:8000/market/chip-race`

**检查 Console (F12)**:
```
✅ 无错误
> GET /api/market/v3/chip-race?limit=20 200 (234ms)
```

**截图**: `docs/verification-screenshots/chip-race-20251029-console.png`

**检查 Network**:
| 请求 | 状态 | 类型 | 大小 | 时间 |
|------|------|------|------|------|
| `/api/market/v3/chip-race?limit=20` | 200 | xhr | 5.6 KB | 234 ms |

**截图**: `docs/verification-screenshots/chip-race-20251029-network.png`

**检查数据显示**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
竞价抢筹
开盘竞价阶段大单抢筹的股票
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 股票代码 | 股票名称 | 开盘价   | 抢筹金额(万元) | 抢筹占比 | 日期       |
|---------|---------|---------|---------------|---------|-----------|
| 000001  | 平安银行 | 12.45   | 1234.56       | 5.67%   | 2025-10-29|
| 600519  | 贵州茅台 | 1689.00 | 9876.54       | 3.21%   | 2025-10-29|
| 600036  | 招商银行 | 45.78   | 5678.90       | 4.32%   | 2025-10-29|
| ...     | ...     | ...     | ...           | ...     | ...       |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**截图**: `docs/verification-screenshots/chip-race-20251029-ui.png`

**✅ Layer 4 通过** - UI 正常显示 (时间: 30 分钟)

---

### Layer 3: 集成层验证 (端到端测试)

#### 3.1 创建集成测试

创建 `tests/integration/test_chip_race_integration.py`:

```python
import pytest
from playwright.sync_api import Page, expect
import psycopg2
import requests

def test_chip_race_full_integration(page: Page):
    """验证竞价抢筹完整数据流: 数据库 → API → 前端 → UI"""

    # ===== Layer 5: 数据库检查 =====
    conn = psycopg2.connect(
        host="localhost",
        user="mystocks_user",
        password="mystocks2025",
        database="mystocks"
    )
    cursor = conn.cursor()

    # 检查数据存在
    cursor.execute("SELECT COUNT(*) FROM cn_stock_chip_race_open;")
    count = cursor.fetchone()[0]
    assert count > 0, "Data Layer Failed: 数据库无数据"

    # 检查最新数据
    cursor.execute("SELECT MAX(trade_date) FROM cn_stock_chip_race_open;")
    latest_date = cursor.fetchone()[0]
    assert latest_date is not None, "Data Layer Failed: 无最新数据"

    # 获取样本数据用于验证
    cursor.execute("""
        SELECT stock_code, stock_name, chip_amount
        FROM cn_stock_chip_race_open
        WHERE trade_date = %s
        ORDER BY chip_amount DESC
        LIMIT 1;
    """, (latest_date,))
    top_stock = cursor.fetchone()
    assert top_stock is not None, "Data Layer Failed: 无样本数据"

    top_code, top_name, top_amount = top_stock
    cursor.close()
    conn.close()

    # ===== Layer 2: API 检查 =====
    response = requests.get("http://localhost:8000/api/market/v3/chip-race?limit=20")
    assert response.status_code == 200, \
        f"API Layer Failed: 状态码 {response.status_code}"

    api_data = response.json()["data"]
    assert len(api_data) > 0, "API Layer Failed: API 返回空数据"

    # 验证 API 数据与数据库一致
    assert api_data[0]["stock_code"] == top_code, \
        "API Layer Failed: API 数据与数据库不一致"

    # ===== Layer 4: UI 检查 =====
    page.goto("http://localhost:8000/market/chip-race")

    # 等待数据加载
    page.wait_for_selector("table", timeout=5000)

    # 检查 Console 无错误
    logs = []
    page.on("console", lambda msg: logs.append(msg))
    page.reload()
    page.wait_for_selector("table tbody tr", timeout=5000)

    errors = [log for log in logs if log.type == "error"]
    assert len(errors) == 0, f"UI Layer Failed: Console 有错误 {errors}"

    # 验证数据表渲染
    table = page.locator("table.chip-race-table")
    assert table.count() > 0, "UI Layer Failed: 数据表未渲染"

    # 验证至少有一行数据
    rows = page.locator("table tbody tr")
    assert rows.count() > 0, "UI Layer Failed: 表格无数据行"

    # 验证第一行数据与数据库一致
    first_row = rows.first
    expect(first_row).to_contain_text(top_code)  # 股票代码
    expect(first_row).to_contain_text(top_name)  # 股票名称

    # 验证抢筹金额显示 (转换为万元)
    expected_amount = f"{(top_amount / 10000):.2f}"
    expect(first_row).to_contain_text(expected_amount)

    print(f"✅ 完整数据流验证通过: {top_code} {top_name}")
```

#### 3.2 运行集成测试

```bash
pytest tests/integration/test_chip_race_integration.py -v
```

**输出**:
```
tests/integration/test_chip_race_integration.py::test_chip_race_full_integration PASSED [100%]
✅ 完整数据流验证通过: 000001 平安银行

=============================== 1 passed in 4.56s ===============================
```

**✅ Layer 3 通过** - 端到端数据流完整 (时间: 10 分钟)

---

## ✅ 验证总结

### 完成状态

| Layer | 状态 | 时间 | 备注 |
|-------|------|------|------|
| Layer 5: 数据层 | ✅ 通过 | 10 min | 数据存在且时效性良好 |
| Layer 2: API 层 | ✅ 通过 | 25 min | API 正确返回数据 |
| Layer 1: 代码层 | ✅ 通过 | 15 min | 单元测试通过，代码质量合格 |
| Layer 4: UI 层 | ✅ 通过 | 30 min | UI 正常显示，无错误 |
| Layer 3: 集成层 | ✅ 通过 | 10 min | 端到端数据流完整 |
| **总计** | **✅ 完成** | **90 min** | 所有层验证通过 |

### 截图清单

- ✅ `chip-race-20251029-console.png`: Console 无错误
- ✅ `chip-race-20251029-network.png`: Network 请求成功
- ✅ `chip-race-20251029-ui.png`: UI 正常显示数据

---

## 📝 经验教训

### 验证顺序的重要性

**本示例验证顺序**: Layer 5 → 2 → 1 → 4 → 3

**为什么这个顺序更高效？**

1. **Layer 5 先行**: 确保数据源存在，避免后续无用功
2. **Layer 2 紧随**: 验证 API 能正确读取数据
3. **Layer 1 质量**: 确保代码可维护性
4. **Layer 4 用户**: 最终用户体验验证
5. **Layer 3 集成**: 全链路验证，确保无断点

**对比旧流程**:

旧流程: Layer 1 → 部署 → 用户发现问题
- ❌ 浪费时间: 写完代码才发现数据不存在
- ❌ 返工成本高: 修改多层代码

新流程: Layer 5 → 2 → 1 → 4 → 3
- ✅ 早发现问题: 5 分钟就知道数据是否存在
- ✅ 减少返工: 每层验证通过再继续下一层

### 数据流完整性的关键点

**断点 1: 数据库 → API**
- 问题: SQL 查询错误
- 验证: Layer 2 API 测试
- 工具: httpie, jq

**断点 2: API → 前端**
- 问题: 前端未调用 API 或调用错误 API
- 验证: Layer 4 Network 检查
- 工具: Chrome DevTools

**断点 3: 前端 → UI**
- 问题: 前端拿到数据但未渲染
- 验证: Layer 4 Console 检查
- 工具: Chrome DevTools

**断点 4: 完整流程**
- 问题: 各层单独正常，组合起来有问题
- 验证: Layer 3 Playwright 集成测试
- 工具: Playwright

### 关键学习点

1. **从底层开始验证**: 确保数据源存在是第一步
2. **每层独立验证**: 不要跳层，逐层验证
3. **自动化关键路径**: Playwright 集成测试覆盖完整数据流
4. **截图保存证据**: 方便后续复盘和知识积累
5. **错误处理必不可少**: 每层都要有 error handling

---

## 🔗 相关资源

- [Definition of Done](../definition-of-done.md)
- [手动验证指南](../manual-verification-guide.md)
- [API Fix Example](api-fix-example.md) - 后端 API 修复
- [UI Fix Example](ui-fix-example.md) - 前端 UI 修复
- [SQL 查询模板](../../../scripts/sql_templates.sql)

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，展示完整数据流的端到端验证
