# API 修复示例：Dashboard API 返回空数据

**场景**: Dashboard 页面无法显示数据，API 返回空数组
**问题**: 用户打开仪表板页面，看到"暂无数据"提示
**根因**: 后端 API 查询逻辑错误，导致返回空数据
**修复时间**: 45 分钟 (包含完整 5 层验证)

---

## 📋 问题描述

### 用户报告
```
问题: Dashboard 页面显示"暂无数据"
URL: http://localhost:8000/dashboard
期望: 显示龙虎榜、资金流向等数据
实际: 页面空白，无任何数据
```

### 初步排查
- 前端代码正常 (Console 无错误)
- Network 显示 API 返回 200
- API 响应: `{"data": []}`  ← 问题在这里！

---

## 🔍 5 层验证流程

### Layer 1: 代码层验证

#### 1.1 发现问题

查看后端代码 `web/backend/app/api/data.py`:

```python
# ❌ 错误代码
@router.get("/dashboard/summary")
async def get_dashboard_summary():
    query = """
    SELECT * FROM cn_stock_top
    WHERE trade_date = CURRENT_DATE;  -- 问题：如果今天不是交易日，返回空数据
    """
    result = await db.execute(query)
    return {"data": result}
```

**问题分析**:
- 查询条件 `trade_date = CURRENT_DATE` 太严格
- 如果今天不是交易日（周末、节假日），查询结果为空
- 应该查询最新交易日的数据

#### 1.2 修复代码

```python
# ✅ 修复后的代码
@router.get("/dashboard/summary")
async def get_dashboard_summary():
    query = """
    SELECT * FROM cn_stock_top
    WHERE trade_date = (
        SELECT MAX(trade_date) FROM cn_stock_top
    )
    LIMIT 100;
    """
    result = await db.execute(query)
    return {"data": result}
```

**修复说明**:
- 使用子查询获取最新交易日
- 无论今天是否交易日，都能返回最新数据
- 添加 `LIMIT 100` 限制返回数量

#### 1.3 单元测试

创建测试文件 `tests/unit/test_dashboard_api.py`:

```python
import pytest
from app.api.data import get_dashboard_summary

@pytest.mark.asyncio
async def test_dashboard_summary_returns_data():
    """测试 dashboard summary 返回数据"""
    result = await get_dashboard_summary()

    # 验证返回结构
    assert "data" in result
    assert isinstance(result["data"], list)

    # 验证数据不为空
    assert len(result["data"]) > 0

    # 验证数据字段完整
    first_item = result["data"][0]
    assert "stock_code" in first_item
    assert "stock_name" in first_item
    assert "trade_date" in first_item
```

运行测试:

```bash
pytest tests/unit/test_dashboard_api.py -v
```

**输出**:
```
tests/unit/test_dashboard_api.py::test_dashboard_summary_returns_data PASSED [100%]

=============================== 1 passed in 0.23s ===============================
```

#### 1.4 代码质量检查

```bash
# 格式化代码
black web/backend/app/api/data.py

# 代码风格检查
flake8 web/backend/app/api/data.py
```

**输出**:
```
reformatted web/backend/app/api/data.py
All done! ✨ 🍰 ✨
1 file reformatted.
```

**✅ Layer 1 通过** (时间: 10 分钟)

---

### Layer 2: API 层验证

#### 2.1 启动后端服务

```bash
cd web/backend
python -m uvicorn app.main:app --reload
```

**输出**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 2.2 获取访问 Token

```bash
source /opt/claude/mystocks_spec/scripts/bash_aliases.sh
TOKEN=$(mt-token)
echo $TOKEN
```

**输出**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2MTQ0MDAwMH0.xxx
```

#### 2.3 验证 API 返回数据

```bash
# 方法 1: 使用快捷命令
mt-api /api/data/dashboard/summary

# 方法 2: 使用 httpie
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN"
```

**输出**:
```json
HTTP/1.1 200 OK
content-type: application/json

{
    "data": [
        {
            "stock_code": "000001",
            "stock_name": "平安银行",
            "trade_date": "2025-10-29",
            "close_price": 12.34,
            "change_percent": 3.45,
            "turnover_rate": 2.1
        },
        {
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "trade_date": "2025-10-29",
            "close_price": 1678.90,
            "change_percent": -1.23,
            "turnover_rate": 0.8
        }
        // ... 更多数据
    ]
}
```

#### 2.4 验证数据不为空

```bash
mt-test-api /api/data/dashboard/summary
```

**输出**:
```
Testing: /api/data/dashboard/summary
✅ PASS
```

#### 2.5 验证错误场景

```bash
# 测试无效 token
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer invalid_token"
```

**输出**:
```
HTTP/1.1 401 Unauthorized
{
    "detail": "Invalid authentication credentials"
}
```

**✅ Layer 2 通过** (时间: 12 分钟)

---

### Layer 3: 集成层验证

#### 3.1 创建集成测试

创建文件 `tests/integration/test_dashboard_data_display.py`:

```python
import pytest
from playwright.sync_api import Page, expect
import requests

@pytest.fixture
def api_token():
    """获取 API token"""
    response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]

def test_dashboard_data_display(page: Page, api_token: str):
    """验证仪表板数据显示的完整流程"""

    # Layer 5: 数据库检查
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        user="mystocks_user",
        password="mystocks2025",
        database="mystocks"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cn_stock_top;")
    count = cursor.fetchone()[0]
    assert count > 0, "Data Layer Failed: 数据库无数据"

    # Layer 2: API 检查
    response = requests.get(
        "http://localhost:8000/api/data/dashboard/summary",
        headers={"Authorization": f"Bearer {api_token}"}
    )
    assert response.status_code == 200, \
        f"API Layer Failed: 状态码 {response.status_code}"

    data = response.json()["data"]
    assert len(data) > 0, "API Layer Failed: API 返回空数据"

    # Layer 4: UI 检查
    page.goto("http://localhost:8000/dashboard")

    # 等待数据加载
    page.wait_for_selector("[data-testid='dashboard-summary']", timeout=5000)

    # 验证数据表渲染
    table = page.locator("[data-testid='data-table']")
    assert table.count() > 0, "UI Layer Failed: 数据表未渲染"

    # 验证至少有一行数据
    rows = page.locator("table tbody tr")
    assert rows.count() > 0, "UI Layer Failed: 表格无数据行"

    # 验证数据内容
    first_row = rows.first
    expect(first_row).to_contain_text("平安银行")  # 验证股票名称显示
```

#### 3.2 运行集成测试

```bash
pytest tests/integration/test_dashboard_data_display.py -v
```

**输出**:
```
tests/integration/test_dashboard_data_display.py::test_dashboard_data_display PASSED [100%]

=============================== 1 passed in 3.45s ===============================
```

**✅ Layer 3 通过** (时间: 8 分钟)

---

### Layer 4: 用户界面层验证

#### 4.1 访问页面

打开浏览器，访问:
```
http://localhost:8000/dashboard
```

#### 4.2 检查 Console

按 `F12` 打开 DevTools → Console 标签

**结果**:
```
✅ 无红色错误
⚠️ 1 warning: "[Vue warn] Component mounted" (可忽略)
```

**截图**: `docs/verification-screenshots/dashboard-fix-20251029-console.png`

![Console 截图示意](此处应有截图)
```
[控制台显示]
> GET /api/data/dashboard/summary 200 (234ms)
✅ 无错误
```

#### 4.3 检查 Network

切换到 Network 标签，刷新页面 (F5)

**API 请求列表**:
| 请求 | 状态 | 类型 | 大小 | 时间 |
|------|------|------|------|------|
| `/api/data/dashboard/summary` | 200 | xhr | 8.5 KB | 234 ms |
| `/static/css/main.css` | 200 | css | 12 KB | 45 ms |
| `/static/js/app.js` | 200 | js | 156 KB | 123 ms |

**详细检查 API 响应**:
1. 点击 `/api/data/dashboard/summary`
2. 切换到 "Response" 标签
3. 验证数据结构正确，数据不为空

**截图**: `docs/verification-screenshots/dashboard-fix-20251029-network.png`

![Network 截图示意](此处应有截图)
```
[Network 面板显示]
Name: dashboard/summary
Status: 200
Type: xhr
Size: 8.5 KB
Time: 234 ms

Response:
{
  "data": [
    {"stock_code": "000001", "stock_name": "平安银行", ...},
    {"stock_code": "600519", "stock_name": "贵州茅台", ...},
    ...
  ]
}
```

#### 4.4 检查数据显示

**验证内容**:
- ✅ 页面显示数据表格
- ✅ 表格至少有 10 行数据
- ✅ 股票代码格式正确 (6 位数字)
- ✅ 股票名称显示为中文
- ✅ 价格和涨跌幅格式正确

**截图**: `docs/verification-screenshots/dashboard-fix-20251029-ui.png`

![UI 截图示意](此处应有截图)
```
[Dashboard 页面]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 股票代码 | 股票名称 | 收盘价 | 涨跌幅 |
|---------|---------|--------|--------|
| 000001  | 平安银行 | 12.34  | +3.45% |
| 600519  | 贵州茅台 | 1678.90| -1.23% |
| ...     | ...     | ...    | ...    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
显示 100 条记录
```

#### 4.5 测试交互功能

- ✅ 点击"刷新"按钮: 数据重新加载
- ✅ 表格排序: 点击列标题可排序
- ✅ 页面跳转: 点击股票名称跳转到详情页

**✅ Layer 4 通过** (时间: 15 分钟)

---

### Layer 5: 数据验证层

#### 5.1 连接数据库

```bash
mt-db
```

**输出**:
```
Server: PostgreSQL 14.5
Version: 14.5
User: mystocks_user
Database: mystocks
```

#### 5.2 检查数据存在

```sql
SELECT COUNT(*) as record_count FROM cn_stock_top;
```

**输出**:
```
 record_count
--------------
          523
(1 row)
```

✅ 数据存在

#### 5.3 检查数据时效性

```sql
SELECT MAX(trade_date) as latest_date FROM cn_stock_top;
```

**输出**:
```
 latest_date
-------------
 2025-10-29
(1 row)
```

✅ 最新数据为今天

#### 5.4 检查数据完整性

```sql
SELECT COUNT(*) as null_count
FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;
```

**输出**:
```
 null_count
------------
          0
(1 row)
```

✅ 无 NULL 值

#### 5.5 查看数据样本

```sql
SELECT stock_code, stock_name, close_price, change_percent
FROM cn_stock_top
WHERE trade_date = '2025-10-29'
ORDER BY change_percent DESC
LIMIT 5;
```

**输出**:
```
 stock_code | stock_name | close_price | change_percent
------------+------------+-------------+----------------
 000001     | 平安银行    |       12.34 |           3.45
 600519     | 贵州茅台    |     1678.90 |          -1.23
 600036     | 招商银行    |       45.67 |           2.11
 000858     | 五粮液     |      156.78 |           1.89
 601318     | 中国平安    |       67.89 |           0.56
(5 rows)
```

✅ 数据合理

退出数据库:
```sql
\q
```

**✅ Layer 5 通过** (时间: 5 分钟)

---

## ✅ 验证总结

### 完成状态

| Layer | 状态 | 时间 | 备注 |
|-------|------|------|------|
| Layer 1: 代码层 | ✅ 通过 | 10 min | 修复查询逻辑，单元测试通过 |
| Layer 2: API 层 | ✅ 通过 | 12 min | API 返回正确数据，状态码 200 |
| Layer 3: 集成层 | ✅ 通过 | 8 min | Playwright 测试通过 |
| Layer 4: UI 层 | ✅ 通过 | 15 min | 页面正常显示，无错误 |
| Layer 5: 数据层 | ✅ 通过 | 5 min | 数据库有数据，数据完整 |
| **总计** | **✅ 完成** | **50 min** | 所有层验证通过 |

### 截图清单

- ✅ `dashboard-fix-20251029-console.png`: Console 无错误
- ✅ `dashboard-fix-20251029-network.png`: Network 请求成功
- ✅ `dashboard-fix-20251029-ui.png`: UI 正常显示数据

---

## 📝 经验教训

### 问题根因

**代码问题**:
```python
# ❌ 错误: 硬编码 CURRENT_DATE
WHERE trade_date = CURRENT_DATE;

# ✅ 正确: 查询最新交易日
WHERE trade_date = (SELECT MAX(trade_date) FROM cn_stock_top);
```

### 为什么之前的流程没有发现这个问题？

**旧流程 (只有 Layer 1)**:
1. 单元测试通过 → ✅ (使用 mock 数据，总是返回数据)
2. 代码合并 → ✅
3. **部署后用户发现问题** → ❌

**新流程 (5 层验证)**:
1. Layer 1: 单元测试 → ✅
2. Layer 2: API 验证 → **❌ 发现返回空数据**
3. 立即修复，避免部署后问题

### 关键学习点

1. **不要相信 mock 数据**: 单元测试使用 mock 可能掩盖真实问题
2. **API 层验证必不可少**: 在真实环境验证 API 返回数据
3. **完整数据流验证**: 从数据库到 UI 的每一层都要检查
4. **截图保存证据**: 方便后续复盘和知识积累

---

## 🔗 相关资源

- [Definition of Done](../definition-of-done.md)
- [手动验证指南](../manual-verification-guide.md)
- [API 验证模板](../../../scripts/api_templates.sh)
- [SQL 查询模板](../../../scripts/sql_templates.sql)

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，展示完整 5 层验证流程
