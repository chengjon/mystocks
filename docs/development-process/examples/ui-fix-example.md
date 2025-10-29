# UI 修复示例：前端无法显示 ETF 数据

**场景**: ETF 数据页面无法显示数据，Console 有错误
**问题**: 用户访问 ETF 数据页面，看到错误提示和空白页面
**根因**: 前端代码访问了未定义的属性，导致渲染失败
**修复时间**: 40 分钟 (包含完整 5 层验证)

---

## 📋 问题描述

### 用户报告
```
问题: ETF 数据页面无法显示
URL: http://localhost:8000/market/etf-data
错误: TypeError: Cannot read property 'fund_name' of undefined
期望: 显示 ETF 基金列表
实际: 页面空白，Console 有红色错误
```

### 初步排查

**打开 DevTools Console (F12)**:
```
❌ TypeError: Cannot read property 'fund_name' of undefined
    at ETFDataView.vue:45
    at Array.map (native)
```

**Network 检查**:
- API 请求: `GET /api/market/etf-data` → **200 OK**
- 响应数据: `{"data": [...]}`  ← 数据存在

**结论**: 后端 API 正常，问题在前端代码

---

## 🔍 5 层验证流程

### Layer 2: API 层验证 (确认后端正常)

#### 2.1 验证 API 返回数据

```bash
source scripts/bash_aliases.sh
mt-api /api/market/etf-data?limit=5
```

**输出**:
```json
HTTP/1.1 200 OK

{
    "data": [
        {
            "stock_code": "510050",
            "stock_name": "50ETF",        # ← 注意：字段名是 stock_name
            "trade_date": "2025-10-29",
            "close_price": 3.456,
            "change_percent": 1.23
        },
        {
            "stock_code": "510300",
            "stock_name": "沪深300ETF",
            "trade_date": "2025-10-29",
            "close_price": 4.567,
            "change_percent": -0.45
        }
    ]
}
```

**发现**:
- ✅ API 返回 200
- ✅ 数据存在
- ⚠️ 字段名是 `stock_name`，不是 `fund_name`

**✅ Layer 2 通过** - 后端 API 正常 (时间: 5 分钟)

---

### Layer 4: UI 层验证 (发现问题)

#### 4.1 检查 Console 错误

**打开浏览器**: `http://localhost:8000/market/etf-data`

**F12 → Console**:
```javascript
❌ TypeError: Cannot read property 'fund_name' of undefined
    at Proxy.render (ETFDataView.vue:45:28)
    at renderComponentRoot (runtime-core.esm-bundler.js:896:44)
    at componentUpdateFn (runtime-core.esm-bundler.js:5121:57)
```

**截图**: `docs/verification-screenshots/etf-fix-20251029-console-error.png`

![Console 错误截图示意](此处应有截图)
```
[Console 面板]
❌ TypeError: Cannot read property 'fund_name' of undefined
   at ETFDataView.vue:45

Stack trace:
- ETFDataView.vue:45 (renderList)
- runtime-core.esm-bundler.js:896 (renderComponentRoot)
```

#### 4.2 检查 Network

**F12 → Network → 刷新页面**

| 请求 | 状态 | 类型 | 响应数据 |
|------|------|------|----------|
| `/api/market/etf-data` | 200 | xhr | `{"data": [...]}` |

**点击请求 → Response 标签**:
```json
{
  "data": [
    {
      "stock_code": "510050",
      "stock_name": "50ETF",  # ← 字段名
      ...
    }
  ]
}
```

**截图**: `docs/verification-screenshots/etf-fix-20251029-network-before.png`

---

### Layer 1: 代码层验证 (修复前端)

#### 1.1 定位问题代码

查看前端文件 `web/frontend/src/views/ETFDataView.vue`:

```vue
<!-- ❌ 错误代码 -->
<template>
  <div class="etf-data">
    <h2>ETF 数据</h2>
    <table>
      <thead>
        <tr>
          <th>代码</th>
          <th>名称</th>
          <th>价格</th>
          <th>涨跌幅</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in etfData" :key="item.stock_code">
          <td>{{ item.stock_code }}</td>
          <td>{{ item.fund_name }}</td>  <!-- ❌ 错误：应该是 stock_name -->
          <td>{{ item.close_price }}</td>
          <td :class="item.change_percent > 0 ? 'positive' : 'negative'">
            {{ item.change_percent }}%
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      etfData: []
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      const response = await fetch('/api/market/etf-data?limit=10')
      const result = await response.json()
      this.etfData = result.data
    }
  }
}
</script>
```

**问题分析**:
- 第 20 行: `{{ item.fund_name }}`
- API 返回的字段名是 `stock_name`
- 访问不存在的属性 `fund_name` 导致 `undefined`

#### 1.2 修复代码

```vue
<!-- ✅ 修复后的代码 -->
<template>
  <div class="etf-data">
    <h2>ETF 数据</h2>
    <table>
      <thead>
        <tr>
          <th>代码</th>
          <th>名称</th>
          <th>价格</th>
          <th>涨跌幅</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in etfData" :key="item.stock_code">
          <td>{{ item.stock_code }}</td>
          <td>{{ item.stock_name }}</td>  <!-- ✅ 修复：使用正确的字段名 -->
          <td>{{ item.close_price.toFixed(3) }}</td>  <!-- 格式化价格 -->
          <td :class="getChangeClass(item.change_percent)">
            {{ formatPercent(item.change_percent) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      etfData: []
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const response = await fetch('/api/market/etf-data?limit=10')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result = await response.json()
        this.etfData = result.data || []  // 添加默认值
      } catch (error) {
        console.error('Failed to fetch ETF data:', error)
        this.etfData = []
      }
    },
    getChangeClass(percent) {
      return percent > 0 ? 'positive' : percent < 0 ? 'negative' : ''
    },
    formatPercent(value) {
      const sign = value > 0 ? '+' : ''
      return `${sign}${value.toFixed(2)}%`
    }
  }
}
</script>

<style scoped>
.positive { color: #e74c3c; }  /* 红色 (涨) */
.negative { color: #27ae60; }  /* 绿色 (跌) */
</style>
```

**修复说明**:
1. 修正字段名: `fund_name` → `stock_name`
2. 添加错误处理: `try-catch`
3. 添加默认值: `result.data || []`
4. 格式化数字: `toFixed()`
5. 改进样式: 涨跌颜色

#### 1.3 重新编译前端

```bash
cd web/frontend
npm run build
```

**输出**:
```
✓ building for production...
✓ built in 2.34s
```

**✅ Layer 1 通过** (时间: 15 分钟)

---

### Layer 4: UI 层验证 (验证修复)

#### 4.1 刷新页面

访问: `http://localhost:8000/market/etf-data`

#### 4.2 检查 Console

**F12 → Console**:
```
✅ 无错误
✅ 无警告
```

**截图**: `docs/verification-screenshots/etf-fix-20251029-console-fixed.png`

![Console 修复后截图示意](此处应有截图)
```
[Console 面板]
> GET /api/market/etf-data?limit=10 200 (156ms)
✅ 无错误
```

#### 4.3 检查 Network

**F12 → Network**

| 请求 | 状态 | 类型 | 大小 | 时间 |
|------|------|------|------|------|
| `/api/market/etf-data?limit=10` | 200 | xhr | 3.2 KB | 156 ms |

**响应数据正确**:
```json
{
  "data": [
    {"stock_code": "510050", "stock_name": "50ETF", ...},
    {"stock_code": "510300", "stock_name": "沪深300ETF", ...}
  ]
}
```

**截图**: `docs/verification-screenshots/etf-fix-20251029-network-fixed.png`

#### 4.4 检查数据显示

**页面显示**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETF 数据
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 代码   | 名称       | 价格  | 涨跌幅   |
|--------|-----------|-------|---------|
| 510050 | 50ETF     | 3.456 | +1.23%  |
| 510300 | 沪深300ETF | 4.567 | -0.45%  |
| 510500 | 中证500ETF | 6.789 | +2.11%  |
| ...    | ...       | ...   | ...     |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**验证项**:
- ✅ 数据正确显示
- ✅ ETF 名称显示为中文
- ✅ 价格格式: 3 位小数
- ✅ 涨跌幅格式: +/-符号 + 2 位小数
- ✅ 涨跌颜色: 红色 (涨) / 绿色 (跌)

**截图**: `docs/verification-screenshots/etf-fix-20251029-ui-fixed.png`

![UI 修复后截图示意](此处应有截图)

#### 4.5 测试交互功能

- ✅ 页面刷新: 数据重新加载
- ✅ 点击 ETF 名称: 跳转到详情页 (如已实现)

**✅ Layer 4 通过** (时间: 10 分钟)

---

### Layer 3: 集成层验证

#### 3.1 创建集成测试

创建文件 `tests/integration/test_etf_data_display.py`:

```python
import pytest
from playwright.sync_api import Page, expect

def test_etf_data_display(page: Page):
    """验证 ETF 数据页面显示正常"""

    # 访问 ETF 数据页面
    page.goto("http://localhost:8000/market/etf-data")

    # 等待数据加载
    page.wait_for_selector("table", timeout=5000)

    # Layer 4: 检查 Console 无错误
    logs = []
    page.on("console", lambda msg: logs.append(msg))
    page.reload()  # 重新加载以捕获日志

    # 等待数据加载完成
    page.wait_for_selector("table tbody tr", timeout=5000)

    # 验证无 Console 错误
    errors = [log for log in logs if log.type == "error"]
    assert len(errors) == 0, f"Console 有错误: {errors}"

    # Layer 4: 检查数据表渲染
    table = page.locator("table")
    assert table.count() > 0, "UI Layer Failed: 数据表未渲染"

    # 验证至少有一行数据
    rows = page.locator("table tbody tr")
    assert rows.count() > 0, "UI Layer Failed: 表格无数据行"

    # 验证第一行数据内容
    first_row = rows.first
    expect(first_row).to_contain_text("510050")  # 代码
    expect(first_row).to_contain_text("ETF")     # 名称包含 "ETF"

    # 验证价格格式 (应该是数字)
    price_cell = first_row.locator("td").nth(2)
    price_text = price_cell.text_content()
    assert "." in price_text, "价格应该包含小数点"

    # 验证涨跌幅格式 (应该包含 %)
    change_cell = first_row.locator("td").nth(3)
    change_text = change_cell.text_content()
    assert "%" in change_text, "涨跌幅应该包含 % 符号"
```

#### 3.2 运行集成测试

```bash
pytest tests/integration/test_etf_data_display.py -v
```

**输出**:
```
tests/integration/test_etf_data_display.py::test_etf_data_display PASSED [100%]

=============================== 1 passed in 2.67s ===============================
```

**✅ Layer 3 通过** (时间: 8 分钟)

---

### Layer 5: 数据验证层

#### 5.1 连接数据库

```bash
mt-db
```

#### 5.2 验证数据存在

```sql
SELECT COUNT(*) as record_count FROM cn_etf_spot;
```

**输出**:
```
 record_count
--------------
          156
(1 row)
```

✅ 数据存在

#### 5.3 验证最新数据

```sql
SELECT MAX(trade_date) as latest_date FROM cn_etf_spot;
```

**输出**:
```
 latest_date
-------------
 2025-10-29
(1 row)
```

✅ 数据最新

#### 5.4 查看数据样本

```sql
SELECT stock_code, stock_name, close_price, change_percent
FROM cn_etf_spot
WHERE trade_date = '2025-10-29'
ORDER BY change_percent DESC
LIMIT 5;
```

**输出**:
```
 stock_code | stock_name   | close_price | change_percent
------------+--------------+-------------+----------------
 510050     | 50ETF        |       3.456 |           1.23
 510500     | 中证500ETF    |       6.789 |           2.11
 510300     | 沪深300ETF    |       4.567 |          -0.45
 159915     | 创业板ETF     |       2.345 |           0.89
 512880     | 证券ETF      |       1.234 |          -0.12
(5 rows)
```

✅ 数据合理

```sql
\q
```

**✅ Layer 5 通过** (时间: 5 分钟)

---

## ✅ 验证总结

### 完成状态

| Layer | 状态 | 时间 | 备注 |
|-------|------|------|------|
| Layer 1: 代码层 | ✅ 通过 | 15 min | 修正字段名，添加错误处理 |
| Layer 2: API 层 | ✅ 通过 | 5 min | API 正常返回数据 |
| Layer 3: 集成层 | ✅ 通过 | 8 min | Playwright 测试通过 |
| Layer 4: UI 层 | ✅ 通过 | 10 min | Console 无错误，数据正常显示 |
| Layer 5: 数据层 | ✅ 通过 | 5 min | 数据库有数据，数据完整 |
| **总计** | **✅ 完成** | **43 min** | 所有层验证通过 |

### 截图清单

**修复前**:
- ✅ `etf-fix-20251029-console-error.png`: Console 错误截图
- ✅ `etf-fix-20251029-network-before.png`: Network 请求成功但 UI 报错

**修复后**:
- ✅ `etf-fix-20251029-console-fixed.png`: Console 无错误
- ✅ `etf-fix-20251029-network-fixed.png`: Network 正常
- ✅ `etf-fix-20251029-ui-fixed.png`: UI 正常显示数据

---

## 📝 经验教训

### 问题根因

**前端代码问题**:
```vue
<!-- ❌ 错误: 使用了不存在的字段名 -->
<td>{{ item.fund_name }}</td>

<!-- ✅ 正确: 使用 API 返回的正确字段名 -->
<td>{{ item.stock_name }}</td>
```

### 为什么 Console 错误这么重要？

**案例对比**:

**如果只看 Network**:
- ✅ API 请求 200 OK
- ✅ 响应数据存在
- ❓ 为什么页面空白？ → 不知道原因

**如果检查 Console**:
- ❌ TypeError: Cannot read property 'fund_name' of undefined
- 💡 立即知道问题：访问了不存在的属性
- ⚡ 快速修复：修正字段名

### 关键学习点

1. **Layer 4 验证是必须的**: 即使 API 正常，前端可能有错误
2. **Console 错误必须修复**: 不允许有任何红色错误
3. **字段名要一致**: 前后端 API 契约必须明确
4. **添加错误处理**: `try-catch` 和默认值防止崩溃
5. **截图对比**: 修复前后的对比截图帮助理解问题

### 防止类似问题的建议

1. **使用 TypeScript**: 类型检查可以在编译时发现字段名错误
2. **API 文档**: 明确定义 API 响应结构
3. **前端测试**: 添加单元测试验证组件渲染
4. **代码审查**: PR 时检查 Console 是否有错误

---

## 🔗 相关资源

- [Definition of Done](../definition-of-done.md)
- [手动验证指南](../manual-verification-guide.md) - Layer 4 详细步骤
- [API Fix Example](api-fix-example.md) - 后端 API 修复示例

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，展示前端 UI 问题的完整修复流程
