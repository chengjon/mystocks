# 工具选择决策树

本文档帮助开发者根据任务类型选择正确的验证工具。

**目标**: 快速决策 - 30 秒内确定使用哪个工具

---

## 快速决策流程

```
开始验证任务
    ↓
问题 1: 需要验证哪一层？
    ├─ Layer 5 (数据库) → 使用 SQL + pgcli
    ├─ Layer 2 (API) → 使用 httpie 或 MCP Tools
    ├─ Layer 4 (UI) → 使用浏览器 DevTools
    └─ Layer 3 (集成) → 继续下一个问题
            ↓
问题 2: 是一次性验证还是重复验证？
    ├─ 一次性 → 手动验证 (浏览器 + DevTools)
    └─ 重复验证 → 继续下一个问题
            ↓
问题 3: 需要截图证据吗？
    ├─ 是 → 使用 Playwright (自动化测试)
    └─ 否 → 继续下一个问题
            ↓
问题 4: 流程有多少步骤？
    ├─ 1-3 步骤 → MCP Playwright Tools (快速交互)
    └─ 4+ 步骤 → Playwright 脚本 (完整自动化)
```

---

## 决策矩阵

| 场景 | Layer | 推荐工具 | 原因 | 用时 |
|------|-------|----------|------|------|
| 检查数据是否存在 | Layer 5 | pgcli + SQL | 交互式查询最快 | 1 分钟 |
| 验证 API 响应 | Layer 2 | httpie | 命令行简洁高效 | 1 分钟 |
| 检查 UI 显示 | Layer 4 | 浏览器 F12 | 直接可视化验证 | 2 分钟 |
| 登录流程测试 | Layer 3 | MCP Playwright | 快速交互验证 | 3 分钟 |
| 完整功能测试 | Layer 3 | Playwright 脚本 | 可重复自动化 | 5 分钟 |
| 复杂多步流程 | Layer 3 | Playwright 脚本 | 需要完整控制 | 10+ 分钟 |
| 生产环境验证 | 所有层 | 手动 + httpie | 生产不能运行脚本 | 5 分钟 |

---

## 详细决策指南

### Layer 5: 数据库验证

**总是使用**: SQL + pgcli

**工具**:
```bash
# 连接数据库
PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks

# 验证数据
SELECT COUNT(*) FROM cn_stock_top;
SELECT MAX(trade_date) FROM cn_stock_top;
```

**何时使用**:
- ✅ 检查数据是否存在
- ✅ 验证数据新鲜度
- ✅ 确认数据完整性

**不需要其他工具**: 数据库验证只需要 SQL

---

### Layer 2: API 验证

#### 选择 1: httpie (推荐，95% 场景)

**何时使用**:
- ✅ 简单 GET/POST 请求
- ✅ 需要快速查看响应
- ✅ 命令行操作

**示例**:
```bash
# 获取 token
TOKEN=$(http POST $MYSTOCKS_URL/api/auth/login username=admin password=admin123 | jq -r '.access_token')

# 测试 API
http GET "$MYSTOCKS_URL/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
```

**优点**:
- 速度快（1-2 秒）
- 输出清晰
- 支持 JSON 高亮

#### 选择 2: MCP Chrome DevTools

**何时使用**:
- ✅ 需要测试浏览器环境特定行为
- ✅ 需要检查 Cookies/Session
- ✅ 调试 CORS 问题

**示例**:
```python
# 使用 MCP Chrome DevTools
mcp__chrome-devtools__navigate_page(url="http://localhost:5173/api/market/dragon-tiger")
```

**缺点**: 比 httpie 慢，仅在必要时使用

---

### Layer 4: UI 验证

#### 选择 1: 浏览器 F12 DevTools (推荐，首次验证)

**何时使用**:
- ✅ 开发中首次验证 UI
- ✅ 检查控制台错误
- ✅ 调试 CSS/布局问题
- ✅ 查看网络请求

**步骤**:
1. 打开浏览器访问页面
2. 按 F12 打开 DevTools
3. 检查 Console 标签（无红色错误）
4. 检查 Network 标签（状态码 200）
5. 检查 Elements 标签（元素存在）

**用时**: 2-3 分钟

#### 选择 2: MCP Playwright Tools (快速自动化)

**何时使用**:
- ✅ 需要截图证据
- ✅ 重复验证同一页面
- ✅ 快速交互验证（3 步以内）

**示例**:
```python
# 导航 + 截图
mcp__playwright__browser_navigate(url="http://localhost:5173/dragon-tiger")
mcp__playwright__browser_snapshot()  # 检查元素
mcp__playwright__browser_take_screenshot(filename="dragon-tiger-verified.png")
```

**用时**: 3-5 分钟

#### 选择 3: Playwright 脚本 (完整自动化)

**何时使用**:
- ✅ 复杂交互（4+ 步骤）
- ✅ 需要重复运行
- ✅ 需要集成到 CI/CD

**示例**: 参考 `tests/integration/test_data_table_rendering.py`

**用时**: 首次 10+ 分钟，后续 1 分钟自动运行

---

### Layer 3: 集成测试验证

#### 决策流程图

```
集成测试场景
    ↓
是否需要重复运行？
    ├─ 否 → 手动验证 (浏览器点击)
    └─ 是 → 继续
            ↓
流程有多少步骤？
    ├─ 1-3 步 → MCP Playwright Tools
    └─ 4+ 步 → Playwright 脚本
            ↓
需要多层验证？
    ├─ 是 → 使用 validate_all_layers()
    └─ 否 → 简单 Playwright 脚本
```

#### 选择 1: 手动验证 (一次性测试)

**何时使用**:
- ✅ 首次开发功能
- ✅ 简单流程（登录、点击、查看）
- ✅ 不需要重复验证

**步骤**:
1. 打开浏览器
2. 按照用户流程操作
3. 用 F12 检查每一步

**用时**: 5 分钟

#### 选择 2: MCP Playwright Tools (快速自动化)

**何时使用**:
- ✅ 简单流程需要自动化
- ✅ 需要截图证据
- ✅ 快速迭代验证

**示例**:
```python
# 登录流程
page = mcp__playwright__browser_navigate(url="http://localhost:5173/login")
mcp__playwright__browser_fill_form(fields=[
    {"name": "username", "type": "textbox", "value": "admin"},
    {"name": "password", "type": "textbox", "value": "admin123"}
])
mcp__playwright__browser_click(element="登录按钮", ref="button[type=submit]")
mcp__playwright__browser_take_screenshot(filename="login-success.png")
```

**用时**: 5-10 分钟编写，1 分钟运行

#### 选择 3: Playwright 脚本 (完整自动化)

**何时使用**:
- ✅ 复杂多步流程
- ✅ 需要条件判断
- ✅ 需要多层验证
- ✅ CI/CD 集成

**示例**:
```python
def test_complete_flow_all_layers(page: Page, db_cursor, api_client):
    """完整流程 + 5 层验证"""
    result = validate_all_layers(
        db_cursor, api_client, page,
        config={
            "database_table": "cn_stock_top",
            "api_endpoint": "/api/market/v3/dragon-tiger",
            "ui_elements": {"table": "table.dragon-tiger"}
        }
    )
    assert result.all_passed
```

**用时**: 首次 15-30 分钟，后续自动化

---

## 快速查询表

### 按任务类型选择

| 任务类型 | 推荐工具 | 替代方案 |
|---------|---------|---------|
| 验证数据存在 | SQL + pgcli | - |
| 测试 API 端点 | httpie | MCP Chrome DevTools |
| 检查 UI 显示 | 浏览器 F12 | MCP Playwright snapshot |
| 截图证明 | MCP Playwright | Playwright 脚本 |
| 登录流程 | MCP Playwright | 手动验证 |
| 复杂流程 | Playwright 脚本 | - |
| 一次性验证 | 手动 + httpie | - |
| 重复验证 | Playwright 脚本 | MCP Playwright |
| 调试问题 | 浏览器 F12 | MCP Chrome DevTools |
| CI/CD 集成 | Playwright 脚本 | - |

### 按工具特性选择

| 工具 | 优点 | 缺点 | 最佳场景 |
|------|------|------|---------|
| **pgcli** | 交互式，速度快 | 仅限数据库 | Layer 5 验证 |
| **httpie** | 命令行简洁，JSON 高亮 | 无 UI | Layer 2 验证 |
| **浏览器 F12** | 可视化，实时调试 | 手动操作 | Layer 4 首次验证 |
| **MCP Playwright** | 快速自动化，截图 | 需要 MCP 连接 | 简单流程自动化 |
| **Playwright 脚本** | 完全控制，可重复 | 编写时间长 | 复杂流程自动化 |
| **MCP Chrome DevTools** | 真实浏览器环境 | 慢于 httpie | 调试浏览器特定问题 |

---

## 实战案例

### 案例 1: 新功能开发 - 龙虎榜页面

**场景**: 首次开发龙虎榜数据展示功能

**决策**:
1. **Layer 5**: pgcli 检查数据 (1 分钟)
2. **Layer 2**: httpie 测试 API (1 分钟)
3. **Layer 4**: 浏览器 F12 检查显示 (2 分钟)
4. **Layer 3**: MCP Playwright 截图证明 (3 分钟)

**总用时**: 7 分钟手动 + 3 分钟截图

### 案例 2: Bug 修复 - API 返回空数据

**场景**: 用户报告龙虎榜页面无数据

**决策**:
1. **Layer 5**: SQL 检查数据存在 → ✅ 有数据
2. **Layer 2**: httpie 测试 API → ❌ 返回空数组
3. 定位: API 查询条件错误
4. **修复后验证**: httpie 重新测试 → ✅ 返回数据

**总用时**: 3 分钟定位 + 2 分钟修复 + 1 分钟验证 = 6 分钟

### 案例 3: 自动化测试 - 完整登录流程

**场景**: 需要在每次部署前验证登录功能

**决策**:
- **工具**: Playwright 脚本 (可重复)
- **包含**: Layer 5 (用户表) + Layer 2 (登录 API) + Layer 4 (UI) + Layer 3 (完整流程)

**用时**: 首次 20 分钟编写，后续自动化 1 分钟运行

---

## 工具切换时机

### 从手动切换到自动化

**时机**: 当同一验证需要第 3 次执行时

**示例**:
- 第 1 次: 手动浏览器验证（开发中）
- 第 2 次: 手动浏览器验证（修复后）
- **第 3 次**: 编写 Playwright 脚本（避免重复劳动）

### 从 MCP Tools 切换到脚本

**时机**: 当 MCP 命令超过 5 个时

**示例**:
```python
# MCP 命令太多 → 应该写脚本
mcp__playwright__browser_navigate(...)
mcp__playwright__browser_click(...)
mcp__playwright__browser_fill_form(...)
mcp__playwright__browser_click(...)
mcp__playwright__browser_wait_for(...)
mcp__playwright__browser_take_screenshot(...)

# ✅ 应该写成 Playwright 脚本
def test_complete_flow():
    page.goto(...)
    page.click(...)
    page.fill(...)
    # ...
```

---

## 常见错误

### ❌ 错误 1: 在生产环境运行 Playwright 脚本

**问题**: 生产环境不应该运行自动化测试

**正确做法**: 生产环境使用手动 + httpie 验证

### ❌ 错误 2: 所有验证都用 Playwright

**问题**: 过度自动化，开发速度变慢

**正确做法**: 简单验证用手动/httpie，复杂流程才自动化

### ❌ 错误 3: 从不自动化

**问题**: 重复手动劳动，效率低

**正确做法**: 重复验证超过 3 次立即自动化

---

## 总结

### 黄金法则

1. **Layer 5 (数据库)**: 总是用 SQL + pgcli
2. **Layer 2 (API)**: 优先用 httpie，除非需要浏览器环境
3. **Layer 4 (UI)**: 首次用手动，重复用自动化
4. **Layer 3 (集成)**: 简单用 MCP Tools，复杂用脚本

### 记住

- **速度优先**: 手动验证快于自动化（首次）
- **自动化原则**: 重复 3 次以上才自动化
- **工具组合**: 多数场景需要组合使用多个工具
- **时间预算**: 验证时间应 ≤ 开发时间的 30%

**下一步**: 查看具体工具使用指南
- MCP Tools 使用指南: `mcp-tools-guide.md`
- Playwright 脚本指南: `playwright-scripts-guide.md`
- 手动验证指南: `docs/development-process/manual-verification-guide.md`
