# API 验证指南 (Layer 2)

**版本**: 1.0
**日期**: 2025-10-29
**目的**: Layer 2 (API 层) 验证的完整指南

---

## 概述

Layer 2 验证确保 API 端点返回正确的数据,字段完整,格式正确。

**验证原则**: 先验证 API,再验证 UI

---

## MyStocks API 端点清单

### 核心 API 端点

| API 端点 | 用途 | 预期字段 |
|---------|------|---------|
| `/api/auth/login` | 用户登录 | `access_token`, `token_type` |
| `/api/market/v3/dragon-tiger` | 龙虎榜数据 | `stock_code`, `stock_name`, `trade_date`, `net_buy_amount` |
| `/api/market/v3/etf-data` | ETF 数据 | `symbol`, `name`, `price`, `change_percent` |
| `/api/market/v3/fund-flow` | 资金流向 | `industry_name`, `主力净额`, `超大单净额`, `大单净额` |
| `/api/market/v3/chip-race` | 竞价抢筹 | `stock_code`, `stock_name`, `竞价金额`, `竞买率` |
| `/api/data/dashboard/summary` | 仪表盘汇总 | `dragon_tiger`, `etf_data`, `fund_flow`, `chip_race` |

---

## 快速验证工具选择

### 工具选择决策

| 场景 | 推荐工具 | 用时 |
|------|---------|------|
| 测试单个 API | **httpie** | 1 分钟 |
| 测试 2-3 个 API | **httpie + shell 脚本** | 3 分钟 |
| 测试 4+ 个 API | **MCP Tools** | 5 分钟 |
| 需要截图证据 | **MCP Playwright** | 3 分钟 |
| 重复验证 | **Playwright 脚本** | 1 分钟 (自动) |

---

## 方法 1: httpie 快速验证 (推荐)

### 安装

```bash
pip install httpie
```

### 基本用法

#### 1. 登录获取 Token

```bash
# POST 请求登录
http POST http://localhost:8000/api/auth/login \
  username=admin \
  password=admin123

# 预期响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### 2. 使用 Token 调用 API

```bash
# 方法 A: 手动复制 token
TOKEN="eyJhbGciOiJIUzI1NiIs..."
http GET http://localhost:8000/api/market/v3/dragon-tiger?limit=5 \
  Authorization:"Bearer $TOKEN"

# 方法 B: 自动提取 token (推荐)
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')
http GET http://localhost:8000/api/market/v3/dragon-tiger?limit=5 \
  Authorization:"Bearer $TOKEN"
```

### MyStocks API 完整示例

#### 示例 1: 龙虎榜 API

```bash
# 获取 token
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')

# 调用龙虎榜 API
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"

# 预期响应
{
  "code": 200,
  "data": [
    {
      "stock_code": "600519",
      "stock_name": "贵州茅台",
      "trade_date": "2025-10-29",
      "net_buy_amount": 123456789.00,
      "closing_price": 1680.50
    },
    ...
  ],
  "message": "success"
}
```

**验证要点**:
- ✅ `code` = 200
- ✅ `data` 是数组
- ✅ 数组至少有 1 条记录
- ✅ 每条记录有 `stock_code`, `stock_name`, `trade_date`
- ✅ `net_buy_amount` 是数字类型

#### 示例 2: ETF 数据 API

```bash
http GET "http://localhost:8000/api/market/v3/etf-data?limit=5" \
  Authorization:"Bearer $TOKEN"

# 预期响应
{
  "code": 200,
  "data": [
    {
      "symbol": "510300",
      "name": "沪深300ETF",
      "price": 4.123,
      "change_percent": 1.25,
      "volume": 1234567
    },
    ...
  ]
}
```

**验证要点**:
- ✅ `symbol` 是字符串
- ✅ `price` 是浮点数
- ✅ `change_percent` 是浮点数 (可正可负)

#### 示例 3: 资金流向 API

```bash
http GET "http://localhost:8000/api/market/v3/fund-flow?industry_type=csrc&limit=5" \
  Authorization:"Bearer $TOKEN"

# 预期响应
{
  "code": 200,
  "data": [
    {
      "industry_name": "电子",
      "主力净额": 1234567890.00,
      "超大单净额": 987654321.00,
      "大单净额": 456789012.00
    },
    ...
  ]
}
```

**验证要点**:
- ✅ 参数 `industry_type` 正确传递
- ✅ 中文字段名正常显示
- ✅ 金额字段是数字类型

#### 示例 4: 竞价抢筹 API

```bash
http GET "http://localhost:8000/api/market/v3/chip-race?limit=5" \
  Authorization:"Bearer $TOKEN"

# 预期响应
{
  "code": 200,
  "data": [
    {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "竞价金额": 12345678.00,
      "竞买率": 85.5
    },
    ...
  ]
}
```

#### 示例 5: 仪表盘汇总 API

```bash
http GET "http://localhost:8000/api/data/dashboard/summary" \
  Authorization:"Bearer $TOKEN"

# 预期响应
{
  "code": 200,
  "data": {
    "dragon_tiger": {
      "total": 100,
      "latest_date": "2025-10-29"
    },
    "etf_data": {
      "total": 50,
      "latest_date": "2025-10-29"
    },
    "fund_flow": {
      "total": 200,
      "latest_date": "2025-10-29"
    },
    "chip_race": {
      "total": 80,
      "latest_date": "2025-10-29"
    }
  }
}
```

**验证要点**:
- ✅ 包含所有 4 个数据源的汇总
- ✅ `total` 是正整数
- ✅ `latest_date` 是今天或最近交易日

### 使用 jq 验证字段

```bash
# 验证字段存在
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=1" \
  Authorization:"Bearer $TOKEN" | \
  jq -e '.data[0] | has("stock_code") and has("stock_name")'
# 输出: true (字段存在)

# 验证数组长度
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN" | \
  jq '.data | length'
# 输出: 5

# 验证数据不为空
http GET "http://localhost:8000/api/data/dashboard/summary" \
  Authorization:"Bearer $TOKEN" | \
  jq -e '.data != null'
# 输出: true (退出码 0)
```

---

## 方法 2: MCP Tools 系统化验证

### 何时使用 MCP Tools?

- ✅ 需要验证多个 API 端点 (4+)
- ✅ 需要截图证据
- ✅ 需要快速迭代测试

### MCP Playwright 示例

#### 示例 1: 验证所有 4 个数据 API

```python
# 1. 导航到龙虎榜 API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/market/v3/dragon-tiger?limit=5"
)
mcp__playwright__browser_snapshot()
# 查看: JSON 响应是否包含 stock_code, stock_name?

# 2. 导航到 ETF API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/market/v3/etf-data?limit=5"
)
mcp__playwright__browser_snapshot()
# 查看: JSON 响应是否包含 symbol, name, price?

# 3. 导航到资金流向 API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/market/v3/fund-flow?industry_type=csrc&limit=5"
)
mcp__playwright__browser_snapshot()
# 查看: JSON 响应是否包含 industry_name, 主力净额?

# 4. 导航到竞价抢筹 API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/market/v3/chip-race?limit=5"
)
mcp__playwright__browser_snapshot()
# 查看: JSON 响应是否包含 stock_code, 竞价金额?
```

**用时**: 6-8 分钟验证所有 4 个端点

#### 示例 2: 验证 API 并截图

```python
# 导航到仪表盘汇总 API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/data/dashboard/summary"
)

# 获取页面快照
snapshot = mcp__playwright__browser_snapshot()
# 验证: 是否包含 dragon_tiger, etf_data, fund_flow, chip_race?

# 截图保存证据
mcp__playwright__browser_take_screenshot(
    filename="api-dashboard-summary-verified.png"
)
```

#### 示例 3: 使用 JavaScript 验证

```python
# 导航到 API
mcp__playwright__browser_navigate(
    url="http://localhost:8000/api/market/v3/dragon-tiger?limit=10"
)

# 执行 JavaScript 验证数据长度
result = mcp__playwright__browser_evaluate(
    function="""() => {
        const pre = document.querySelector('pre');
        const data = JSON.parse(pre.textContent);
        return data.data.length;
    }"""
)
# 预期: result = 10
```

### MCP Chrome DevTools 示例

```python
# 创建新页面并导航
mcp__chrome-devtools__new_page(
    url="http://localhost:8000/api/market/v3/dragon-tiger?limit=5"
)

# 获取页面快照
snapshot = mcp__chrome-devtools__take_snapshot()
# 检查: JSON 数据是否正确显示?

# 执行 JavaScript 提取数据
result = mcp__chrome-devtools__evaluate_script(
    function="""() => {
        const pre = document.querySelector('pre');
        const data = JSON.parse(pre.textContent);
        return {
            count: data.data.length,
            has_stock_code: data.data[0].hasOwnProperty('stock_code')
        };
    }"""
)
# 验证: count >= 5, has_stock_code = true

# 截图
mcp__chrome-devtools__take_screenshot(filename="dragon-tiger-api.png")
```

---

## 方法 3: curl 备选方案

### 何时使用 curl?

- ⚠️ httpie 不可用时
- ⚠️ 需要在 Shell 脚本中使用

### 基本用法

```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 提取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.access_token')

# 调用 API
curl -X GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 完整验证脚本

### Shell 脚本: 验证所有 API

```bash
#!/bin/bash
# verify_all_apis.sh

BASE_URL="http://localhost:8000"

# 1. 获取 token
echo "=== Step 1: 登录获取 token ==="
TOKEN=$(http POST $BASE_URL/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  exit 1
fi
echo "✅ Token 获取成功"

# 2. 验证龙虎榜 API
echo -e "\n=== Step 2: 龙虎榜 API ==="
http GET "$BASE_URL/api/market/v3/dragon-tiger?limit=2" \
  Authorization:"Bearer $TOKEN" | jq -e '.data | length >= 1'
if [ $? -eq 0 ]; then
  echo "✅ 龙虎榜 API 正常"
else
  echo "❌ 龙虎榜 API 失败"
fi

# 3. 验证 ETF 数据 API
echo -e "\n=== Step 3: ETF 数据 API ==="
http GET "$BASE_URL/api/market/v3/etf-data?limit=2" \
  Authorization:"Bearer $TOKEN" | jq -e '.data | length >= 1'
if [ $? -eq 0 ]; then
  echo "✅ ETF 数据 API 正常"
else
  echo "❌ ETF 数据 API 失败"
fi

# 4. 验证资金流向 API
echo -e "\n=== Step 4: 资金流向 API ==="
http GET "$BASE_URL/api/market/v3/fund-flow?industry_type=csrc&limit=2" \
  Authorization:"Bearer $TOKEN" | jq -e '.data | length >= 1'
if [ $? -eq 0 ]; then
  echo "✅ 资金流向 API 正常"
else
  echo "❌ 资金流向 API 失败"
fi

# 5. 验证竞价抢筹 API
echo -e "\n=== Step 5: 竞价抢筹 API ==="
http GET "$BASE_URL/api/market/v3/chip-race?limit=2" \
  Authorization:"Bearer $TOKEN" | jq -e '.data | length >= 1'
if [ $? -eq 0 ]; then
  echo "✅ 竞价抢筹 API 正常"
else
  echo "❌ 竞价抢筹 API 失败"
fi

# 6. 验证仪表盘汇总 API
echo -e "\n=== Step 6: 仪表盘汇总 API ==="
http GET "$BASE_URL/api/data/dashboard/summary" \
  Authorization:"Bearer $TOKEN" | jq -e '.data | has("dragon_tiger")'
if [ $? -eq 0 ]; then
  echo "✅ 仪表盘汇总 API 正常"
else
  echo "❌ 仪表盘汇总 API 失败"
fi

echo -e "\n=== 所有 API 验证完成 ==="
```

**用法**:
```bash
chmod +x verify_all_apis.sh
./verify_all_apis.sh
```

---

## 常见问题排查

### 问题 1: 401 Unauthorized

**原因**: Token 过期或未提供

**解决**:
```bash
# 重新获取 token
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')
```

### 问题 2: 404 Not Found

**原因**: API 端点路径错误

**检查**:
- 确认 URL 拼写正确
- 确认后端服务正在运行: `curl http://localhost:8000/health`

### 问题 3: 500 Internal Server Error

**原因**: 后端代码错误或数据库问题

**排查步骤**:
1. 查看后端日志: `tail -f /tmp/uvicorn.log`
2. 检查数据库: `SELECT COUNT(*) FROM cn_stock_top;`

### 问题 4: 返回空数组 `{"data": []}`

**原因**: 数据库无数据或查询条件过严

**解决**:
```bash
# 检查数据库
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks \
  -c "SELECT COUNT(*) FROM cn_stock_top"
```

---

## 验证清单

### Layer 2 (API) 完整验证

- [ ] 登录 API 返回有效 token
- [ ] 龙虎榜 API 返回数据 (≥1 条)
- [ ] ETF 数据 API 返回数据 (≥1 条)
- [ ] 资金流向 API 返回数据 (≥1 条)
- [ ] 竞价抢筹 API 返回数据 (≥1 条)
- [ ] 仪表盘汇总 API 返回所有 4 个数据源
- [ ] 所有 API 响应时间 < 2 秒
- [ ] 所有 API 状态码 = 200
- [ ] 所有必需字段都存在
- [ ] 字段类型正确 (字符串/数字/日期)

---

## 快速参考

### 常用命令别名

添加到 `~/.bashrc` 或 `scripts/bash_aliases.sh`:

```bash
# MyStocks API 快捷命令
alias mt-token='http POST http://localhost:8000/api/auth/login username=admin password=admin123 | jq -r ".access_token"'
alias mt-api-dragon='TOKEN=$(mt-token) && http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" Authorization:"Bearer $TOKEN"'
alias mt-api-etf='TOKEN=$(mt-token) && http GET "http://localhost:8000/api/market/v3/etf-data?limit=5" Authorization:"Bearer $TOKEN"'
alias mt-api-flow='TOKEN=$(mt-token) && http GET "http://localhost:8000/api/market/v3/fund-flow?industry_type=csrc&limit=5" Authorization:"Bearer $TOKEN"'
alias mt-api-chip='TOKEN=$(mt-token) && http GET "http://localhost:8000/api/market/v3/chip-race?limit=5" Authorization:"Bearer $TOKEN"'
alias mt-api-summary='TOKEN=$(mt-token) && http GET "http://localhost:8000/api/data/dashboard/summary" Authorization:"Bearer $TOKEN"'
```

**用法**:
```bash
source scripts/bash_aliases.sh
mt-api-dragon  # 快速测试龙虎榜 API
```

---

## 参考文档

- **工具选型指南**: `docs/development-process/tool-selection-guide.md`
- **工具对比矩阵**: `docs/development-process/tool-comparison.md`
- **完整验证流程**: `docs/development-process/definition-of-done.md`

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本,包含所有 MyStocks API 示例
