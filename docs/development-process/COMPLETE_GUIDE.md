# MyStocks 开发流程完整指南

**版本**: 1.0
**日期**: 2025-10-29
**目的**: MyStocks 项目 5 层验证方法论完整参考手册
**语言**: 中文

---

## 📚 目录

1. [快速开始](#快速开始)
2. [核心理念](#核心理念)
3. [5 层验证模型](#5-层验证模型详解)
4. [工具与命令](#工具与命令)
5. [完整工作流程](#完整工作流程)
6. [故障排查](#故障排查)
7. [最佳实践](#最佳实践)
8. [实战示例](#实战示例)

---

# 快速开始

## 🎯 核心问题

**问题**: 90% 的功能虽然代码测试通过，但用户无法实际使用

**原因**: 只验证代码层，忽略了数据、API、UI 等其他层

**解决方案**: 5 层验证模型 - 确保每一层都正常工作

## ⚡ 60 分钟上手

### 第 1 步: 安装工具 (15 分钟)

```bash
# Python 工具
pip install pytest playwright pytest-playwright httpie pgcli black flake8

# Playwright 浏览器
playwright install chromium

# 系统工具 (如果没有)
sudo apt install jq  # Ubuntu/Debian
brew install jq      # macOS
```

### 第 2 步: 配置快捷命令 (5 分钟)

```bash
# 加载快捷命令
source /opt/claude/mystocks_spec/scripts/bash_aliases.sh

# 验证工具安装
mt-verify-tools
```

### 第 3 步: 理解 5 层模型 (15 分钟)

```
Layer 5 (数据层)  → 数据库有数据且新鲜  [pgcli, SQL]
   ↓
Layer 2 (API层)   → API 返回正确数据   [httpie]
   ↓
Layer 4 (UI层)    → UI 正确显示       [浏览器 DevTools]
   ↓
Layer 3 (集成层)  → 完整流程畅通      [Playwright]
   ↓
Layer 1 (代码层)  → 代码质量合格      [pytest, linter]
```

**核心原则**:
- 自底向上验证 (Layer 5 → Layer 1)
- 任一层失败即停止，定位问题
- 所有层通过才算"完成"

### 第 4 步: 动手实践 (25 分钟)

**练习 1: Layer 5 数据验证**
```bash
mt-db
SELECT COUNT(*) FROM cn_stock_top;
SELECT MAX(trade_date) FROM cn_stock_top;
\q
```

**练习 2: Layer 2 API 验证**
```bash
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
```

**练习 3: Layer 4 UI 验证**
```bash
# 1. 打开浏览器: http://localhost:5173/dragon-tiger
# 2. 按 F12 打开 DevTools
# 3. 检查 Console (无红色错误)
# 4. 检查 Network (API 请求成功)
# 5. 确认数据正确显示
```

**练习 4: Layer 3 集成测试**
```bash
pytest tests/integration/test_user_login_flow.py -v
```

---

# 核心理念

## 什么是 "完成" (Definition of Done)

### 旧定义 vs 新定义

**旧定义** (导致 90% 功能不可用):
```
✅ 代码编写完成
✅ 单元测试通过
❌ 用户无法使用
```

**新定义** (确保功能真正可用):
```
✅ Layer 1: 代码质量合格
✅ Layer 2: API 返回正确数据
✅ Layer 3: 集成测试通过
✅ Layer 4: UI 正确显示
✅ Layer 5: 数据库有数据
```

## 核心原则

### 1. 功能可用性 > 代码正确性
- ❌ "测试通过了，功能完成了"
- ✅ "用户可以看到数据并完成任务，功能完成了"

### 2. 端到端验证
验证完整数据流: `数据库 → API → 前端 → UI`

### 3. 分层验证快速定位
失败时明确知道哪一层出问题

### 4. 自动化 + 手动平衡
- 自动化: 快速反馈 (单元测试、集成测试)
- 手动: 最终确认 (UI 验证、数据正确性)

### 5. 时间可预测性
每个验证步骤有明确时间预算，总额外开销目标 <30%

## SC-001 指标: 功能可用率

```
功能可用率 = (实际可用功能数 / 标记完成功能数) × 100%
```

**目标**:
- 基线: 10% (当前状态)
- 6 个月目标: 90%
- 每月增长: 13-14%

**追踪方法**: 参考 `docs/development-process/adoption-metrics.md`

---

# 5 层验证模型详解

## Layer 5: 数据层 (Data Validation Layer)

### 目标
确保数据库有数据且数据有效

### 时间预算
5-10 分钟

### 工具
- pgcli (PostgreSQL)
- taos (TDengine)
- SQL 查询

### 验证清单
- [ ] 数据存在 (COUNT > 0)
- [ ] 数据时效性 (最新数据不超过 X 小时)
- [ ] 数据完整性 (关键字段无 NULL)
- [ ] 数据合理性 (抽样检查数据质量)

### 操作步骤

**PostgreSQL 验证**:
```bash
# 方法 1: 完整命令
PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks

# 方法 2: 使用快捷命令
mt-db

# 1. 检查数据存在
SELECT COUNT(*) as record_count FROM cn_stock_top;
-- 期望: > 0

# 2. 检查最新数据时间
SELECT MAX(trade_date) as latest_date FROM cn_stock_top;
-- 期望: 今天或最近日期

# 3. 检查数据完整性
SELECT COUNT(*) as null_count FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;
-- 期望: 0

# 4. 查看数据样本
SELECT * FROM cn_stock_top ORDER BY trade_date DESC LIMIT 10;
-- 目视检查数据合理性

\q
```

**TDengine 验证** (如适用):
```bash
# 连接 TDengine
mt-td

USE market_data;
SELECT COUNT(*) FROM tick_data;
SELECT LAST(*) FROM tick_data;
```

### 常见问题

**问题: 数据为空**
- 检查数据采集脚本是否运行
- 运行: `python run_realtime_market_saver.py`

**问题: 数据过期**
- 检查采集任务调度
- 手动触发数据更新

---

## Layer 2: API 层 (API Layer)

### 目标
确保后端 API 正确返回数据

### 时间预算
10-15 分钟

### 工具
- httpie (推荐)
- curl (备选)
- jq (JSON 处理)

### 验证清单
- [ ] 后端服务已启动 (`http://localhost:8000`)
- [ ] API 端点可访问
- [ ] HTTP 状态码正确 (200/201/204)
- [ ] 响应数据结构符合预期
- [ ] 数据不为空: `jq -e '.data != null'`
- [ ] 错误场景正确处理 (400/401/500)

### 操作步骤

**方法 1: 使用 httpie (推荐)**
```bash
# 1. 获取访问 token
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')

# 2. 验证 API 端点
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"

# 3. 验证数据不为空
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN" | jq -e '.data != null and .data | length > 0'

# 4. 验证响应时间
time http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
# 期望: < 2 秒
```

**方法 2: 使用快捷命令**
```bash
# 获取 token
TOKEN=$(mt-token)

# 测试龙虎榜 API
mt-api-dragon

# 测试仪表盘汇总 API
mt-api-summary
```

**方法 3: 使用 MCP Tools (批量验证)**
```python
# Claude Code 中使用 MCP Playwright 工具快速验证多个 API
mcp__playwright__browser_navigate(url="http://localhost:8000/docs")
mcp__playwright__browser_snapshot()
```

### API 验证模板

参考完整模板: `scripts/api_templates.sh`

```bash
# 加载 API 模板
source scripts/api_templates.sh

# 查看所有模板
api_usage_examples

# 运行 API 冒烟测试
api_smoke_test
```

### 常见问题

**问题: API 返回 500 错误**
- 检查后端日志: `tail -f /tmp/uvicorn.log`
- 检查数据库连接
- 验证 Layer 5 (数据层)

**问题: API 返回空数组**
- 首先验证 Layer 5 (数据库有数据)
- 检查 API 查询条件
- 检查权限配置

---

## Layer 4: UI 层 (User Interface Layer)

### 目标
确保用户可见数据，交互正常

### 时间预算
10-20 分钟

### 工具
- 浏览器 (Chrome 推荐)
- DevTools (F12)
- 截图工具

### 验证清单
- [ ] 浏览器中手动访问功能页面
- [ ] 数据正确显示 (截图保存)
- [ ] 无控制台错误 (F12 → Console)
- [ ] 网络请求成功 (F12 → Network)
- [ ] 交互功能正常 (按钮、表单等)

### 操作步骤

#### 步骤 1: 打开页面
```
浏览器访问: http://localhost:5173/dragon-tiger
```

#### 步骤 2: 检查 Console (F12 → Console)
- ✅ 无红色错误 (Errors)
- ⚠️ 如有 Warning，确认不影响功能
- 截图保存: `docs/verification-screenshots/feature-name-YYYYMMDD-console.png`

#### 步骤 3: 检查 Network (F12 → Network)
- ✅ 所有 API 请求状态为 200/201/204
- ✅ 无 failed 请求 (红色)
- ✅ 响应时间合理 (< 2 秒)
- 截图保存: `docs/verification-screenshots/feature-name-YYYYMMDD-network.png`

#### 步骤 4: 检查数据显示
- ✅ 数据正确显示在页面上
- ✅ 数据格式正确 (日期、数字、文本等)
- ✅ 表格/图表正确渲染
- 截图保存: `docs/verification-screenshots/feature-name-YYYYMMDD-ui.png`

#### 步骤 5: 测试交互功能
- ✅ 按钮点击响应正常
- ✅ 表单提交成功 (如适用)
- ✅ 数据刷新功能正常 (如适用)
- ✅ 排序、筛选功能正常 (如适用)

### 截图要求

必须保存的截图:
1. `feature-name-YYYYMMDD-ui.png`: 完整页面展示，数据清晰可见
2. `feature-name-YYYYMMDD-console.png`: Console 无错误截图
3. `feature-name-YYYYMMDD-network.png`: Network 请求成功截图

### 常见问题

**问题: 页面显示 "无数据"**
- 按 5 层诊断: Layer 5 → Layer 2 → Layer 4
- 检查 Network 标签，API 是否成功调用
- 检查 Console，是否有 JavaScript 错误

**问题: JavaScript 控制台错误**
- 定位错误所在的文件和行号
- 检查前端代码逻辑
- 确认 API 响应数据结构

---

## Layer 3: 集成层 (Integration Layer)

### 目标
确保数据流完整，各层无断点

### 时间预算
5-10 分钟 (自动执行)

### 工具
- Playwright (浏览器自动化)
- pytest (测试框架)

### 验证清单
- [ ] Playwright 集成测试通过
- [ ] 数据流完整: 数据库 → 后端 → 前端 → UI
- [ ] 无层间断点
- [ ] 失败时明确指出哪一层出错

### 操作步骤

**运行集成测试**:
```bash
# 运行所有集成测试
pytest tests/integration/ -v

# 运行特定测试
pytest tests/integration/test_user_login_flow.py -v

# 带详细输出和截图
pytest tests/integration/ -v --headed --screenshot=on

# 只运行失败的测试
pytest tests/integration/ -v --lf
```

### 测试结构示例

```python
async def test_dashboard_data_display(page):
    """验证仪表板数据显示的完整流程"""

    # Layer 5: 数据库检查
    assert database_has_data("cn_stock_top"), \
        "Data Layer Failed: 数据库无数据"

    # Layer 2: API 检查
    api_response = requests.get(
        "http://localhost:8000/api/market/v3/dragon-tiger?limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert api_response.status_code == 200, \
        "API Layer Failed: API 返回错误"
    assert len(api_response.json()["data"]) > 0, \
        "API Layer Failed: API 返回空数据"

    # Layer 4: UI 检查
    await page.goto("http://localhost:5173/dragon-tiger")
    await page.wait_for_selector('[data-testid="dragon-tiger-table"]')
    row_count = await page.locator('tbody tr').count()
    assert row_count > 0, \
        "UI Layer Failed: 数据表未渲染"
```

### 常见问题

**问题: 集成测试失败**
- 查看测试报告，确定失败的层
- 回到对应的 Layer 手动验证
- 修复断点后重新运行测试

**分层排查**:
```
AssertionError: Data Layer Failed: 数据库无数据
  → 回到 Layer 5 检查数据库

AssertionError: API Layer Failed: API 返回错误
  → 回到 Layer 2 检查 API

AssertionError: UI Layer Failed: 数据表未渲染
  → 回到 Layer 4 检查前端和 Network
```

---

## Layer 1: 代码层 (Code Layer)

### 目标
确保代码质量和基础正确性

### 时间预算
5-10 分钟

### 工具
- pytest (单元测试)
- black (代码格式化)
- flake8 (代码风格检查)
- mypy (类型检查)

### 验证清单
- [ ] 代码已提交到 feature 分支
- [ ] 单元测试通过
- [ ] 代码格式符合规范
- [ ] 类型检查通过 (如适用)
- [ ] 无调试代码残留

### 操作步骤

```bash
# 1. 运行单元测试
pytest tests/unit/ -v

# 2. 代码格式化
black app/

# 3. 代码风格检查
flake8 app/

# 4. 类型检查 (可选)
mypy app/

# 5. 检查 Git 状态
git status
git diff
```

### 常见问题

**问题: 单元测试失败**
- 修复代码错误
- 不要跳过此步骤继续验证其他层

**问题: 代码格式不规范**
- 运行 `black app/` 自动格式化
- 修复 flake8 警告

---

# 工具与命令

## 快捷命令 (Bash Aliases)

### 加载快捷命令
```bash
source /opt/claude/mystocks_spec/scripts/bash_aliases.sh
```

### 常用命令

**数据库验证**:
```bash
mt-db                          # 连接 PostgreSQL
mt-td                          # 连接 TDengine
mt-db -c "SELECT COUNT(*) FROM cn_stock_top;"  # 执行查询
```

**API 验证**:
```bash
mt-token                       # 获取 JWT token
mt-api-dragon                  # 测试龙虎榜 API
mt-api-summary                 # 测试仪表盘 API
mt-api <endpoint>              # 测试任意 API 端点
```

**系统验证**:
```bash
mt-verify-tools                # 检查所有工具安装状态
mt-check-services              # 检查服务运行状态
```

## API 验证模板

### 加载 API 模板
```bash
source /opt/claude/mystocks_spec/scripts/api_templates.sh
```

### 常用模板
```bash
api_usage_examples             # 查看所有示例
api_get_token                  # 获取访问 token
api_test_dashboard_summary     # 测试仪表板 API
api_test_dragon_tiger          # 测试龙虎榜 API
api_smoke_test                 # 运行 API 冒烟测试
```

## SQL 验证模板

参考: `scripts/sql_templates.sql`

**常用查询**:
```sql
-- 数据存在性检查
SELECT COUNT(*) FROM cn_stock_top;

-- 数据时效性检查
SELECT MAX(trade_date) FROM cn_stock_top;

-- 数据完整性检查
SELECT COUNT(*) FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;

-- 数据合理性检查
SELECT * FROM cn_stock_top ORDER BY trade_date DESC LIMIT 10;
```

## 测试命令

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 特定测试
pytest tests/integration/test_user_login_flow.py -v

# 带截图的测试
pytest tests/integration/ -v --headed --screenshot=on

# 代码质量
black app/ && flake8 app/
```

---

# 完整工作流程

## 修复 Bug 的完整流程

```bash
# 0. 创建 feature 分支
git checkout -b fix/dashboard-empty-data

# 1. Layer 1: 代码层
pytest tests/unit/ -v        # 单元测试
black . && flake8 .          # 代码格式

# 2. Layer 5: 数据层
mt-db
SELECT COUNT(*) FROM cn_stock_top;
SELECT MAX(trade_date) FROM cn_stock_top;
\q

# 3. Layer 2: API 层
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"

# 4. Layer 4: UI 层
# 打开浏览器 → http://localhost:5173/dragon-tiger
# F12 → Console (无错误)
# F12 → Network (所有请求 200)
# 截图保存: docs/verification-screenshots/dashboard-fix-20251029-*.png

# 5. Layer 3: 集成层
pytest tests/integration/test_dashboard_data_display.py -v

# 6. 提交 PR
git add .
git commit -m "fix(dashboard): Fix empty data issue

- Layer 5: Verified database has data
- Layer 2: API returns correct data
- Layer 4: UI displays data correctly
- Layer 3: Integration test passes

Closes #123"
git push origin fix/dashboard-empty-data
```

## 开发新功能的完整流程

```bash
# 0. 创建 feature 分支
git checkout -b feature/new-etf-display

# 1. 开发代码 + 单元测试 (Layer 1)
# ... 编写代码 ...
pytest tests/unit/test_etf_api.py -v

# 2. 确保数据存在 (Layer 5)
mt-db
SELECT COUNT(*) FROM cn_etf_spot;
\q

# 3. 验证 API (Layer 2)
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/etf-data?limit=5" \
  Authorization:"Bearer $TOKEN"

# 4. 验证 UI (Layer 4)
# 打开浏览器验证
# 保存截图

# 5. 编写集成测试 (Layer 3)
# 创建 tests/integration/test_etf_display.py
pytest tests/integration/test_etf_display.py -v

# 6. 完整回归测试
pytest tests/ -v

# 7. 提交 PR
git add .
git commit -m "feat(etf): Add ETF data display feature

- Implemented ETF data API endpoint
- Added frontend ETF display page
- All 5 layers verified and passing

Closes #456"
git push origin feature/new-etf-display
```

## 时间投入参考

| 工作类型 | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Layer 5 | **总计** |
|---------|---------|---------|---------|---------|---------|----------|
| **简单 Bug** | 5 min | 10 min | 5 min | 10 min | 5 min | **35-55 min** |
| **中等功能** | 7 min | 12 min | 7 min | 15 min | 7 min | **50-80 min** |
| **复杂功能** | 10 min | 15 min | 10 min | 20 min | 10 min | **90-120 min** |

---

# 故障排查

## 场景 1: API 返回 500 错误

### 诊断步骤

```bash
# 1. 检查后端日志
tail -f /tmp/uvicorn.log

# 2. 检查数据库连接
mt-db -c "SELECT 1;"

# 3. 验证 API 路由
http GET http://localhost:8000/docs

# 4. 测试简化的 API 请求
http GET http://localhost:8000/health
```

### 常见原因
- 数据库连接失败 → 检查 .env 配置
- SQL 查询错误 → 检查后端日志
- 权限问题 → 检查用户权限

---

## 场景 2: 前端页面显示 "无数据"

### 5 层诊断法

```
Layer 5 → Layer 2 → Layer 4
数据库   → API    → UI
↓         ↓        ↓
有数据?   返回数据? 显示数据?
```

### 诊断步骤

```bash
# Layer 5: 检查数据库
mt-db -c "SELECT COUNT(*) FROM cn_stock_top;"
# 如果 = 0,问题在 Layer 5

# Layer 2: 测试 API
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
# 如果返回空数组，问题在 Layer 2

# Layer 4: 检查前端
# 打开浏览器 F12 → Network
# 检查 API 是否被调用
# 检查 Console 是否有错误
```

---

## 场景 3: 数据库连接失败

### 检查清单

```bash
# 1. PostgreSQL 服务运行
sudo systemctl status postgresql

# 2. 连接配置正确
cat .env | grep POSTGRESQL

# 3. 网络连通性
ping localhost
telnet localhost 5432

# 4. 用户权限
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "SELECT 1;"
```

---

## 场景 4: 前端控制台报 JavaScript 错误

### 诊断步骤

```bash
# 1. 定位错误所在文件
# 在 Console 中点击错误链接

# 2. 检查 API 响应数据结构
# Network → 点击 API 请求 → Response

# 3. 验证前端代码逻辑
# 检查数据绑定和渲染代码

# 4. 测试数据 mock
# 使用假数据测试前端渲染
```

---

## 场景 5: 集成测试失败

### 分层排查

```python
# 测试输出示例:
AssertionError: Data Layer Failed: 数据库无数据

# 排查步骤:
# 1. 回到 Layer 5
mt-db
SELECT COUNT(*) FROM cn_stock_top;

# 2. 如果数据为空，运行数据采集
python run_realtime_market_saver.py

# 3. 重新运行测试
pytest tests/integration/test_dashboard_data_display.py -v
```

---

# 最佳实践

## 1. 按顺序验证，不要跳层

❌ **错误**: 代码未测试就直接打开浏览器
✅ **正确**: Layer 1 → 5 → 2 → 4 → 3 顺序验证

## 2. 失败立即停止，不要继续

❌ **错误**: Layer 2 失败了还继续测试 Layer 4
✅ **正确**: Layer 2 失败立即修复，通过后再继续

## 3. 保存证据，截图为证

❌ **错误**: "我看了页面，数据都有"
✅ **正确**: 保存 UI + Console + Network 三张截图

## 4. 记录问题，便于复盘

❌ **错误**: 修复后不记录问题原因
✅ **正确**: 在 PR 或文档中记录遇到的问题和解决方案

## 5. 自动化优先，手动补充

❌ **错误**: 每次都手动测试所有功能
✅ **正确**: 编写 Playwright 集成测试，手动测试仅验证 UI

## 6. 时间预算意识

- 简单 Bug: 总计 35-55 分钟
- 中等功能: 总计 50-80 分钟
- 复杂功能: 总计 90-120 分钟

**如果超时**: 关键路径优先，边缘场景可标记"部分完成"

## 7. 工具选择决策

**快速决策树**:
```
需要验证哪一层？
├─ Layer 5 (数据库) → pgcli + SQL
├─ Layer 2 (API) → httpie (单个) / MCP Tools (多个)
├─ Layer 4 (UI) → 浏览器 DevTools
├─ Layer 3 (集成) → Playwright 测试
└─ Layer 1 (代码) → pytest + linter
```

---

# 实战示例

## 示例 1: 修复龙虎榜页面无数据问题

**问题描述**: 用户报告龙虎榜页面显示"无数据"

**5 层诊断流程**:

```bash
# Layer 5: 检查数据库
mt-db -c "SELECT COUNT(*) FROM cn_stock_top;"
# 结果: 0 行 ← 找到问题！

# 解决方案: 运行数据采集
python run_realtime_market_saver.py

# 重新验证 Layer 5
mt-db -c "SELECT COUNT(*) FROM cn_stock_top;"
# 结果: 1250 行 ✓

# Layer 2: 测试 API
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
# 结果: success: true, data.length = 5 ✓

# Layer 4: 检查 UI
# 打开 http://localhost:5173/dragon-tiger
# 结果: 数据正确显示 ✓

# 问题解决！
```

**根本原因**: 数据采集任务未运行，数据库为空

**预防措施**:
- 设置定时任务自动采集数据
- 添加数据监控告警

---

## 示例 2: API 响应时间过长

**问题描述**: 资金流向 API 响应时间超过 5 秒

**诊断流程**:

```bash
# Layer 2: 测量响应时间
time http GET "http://localhost:8000/api/market/v3/fund-flow" \
  Authorization:"Bearer $TOKEN"
# 结果: 5.2 秒 ← 确认问题

# Layer 5: 检查数据量
mt-db -c "SELECT COUNT(*) FROM cn_stock_fund_flow_industry;"
# 结果: 1,000,000 行 ← 数据量大

# 解决方案:
# 1. API 添加分页参数
# 2. 数据库添加索引
CREATE INDEX idx_trade_date ON cn_stock_fund_flow_industry(trade_date DESC);

# 验证修复
time http GET "http://localhost:8000/api/market/v3/fund-flow?limit=50" \
  Authorization:"Bearer $TOKEN"
# 结果: 0.8 秒 ✓
```

**根本原因**: 未分页查询大表 + 缺少索引

**优化措施**:
- 所有列表 API 强制分页
- 为常用查询字段添加索引
- 设置响应时间监控

---

## 示例 3: 前端 Console 错误

**问题描述**: Dashboard 页面 Console 显示 "Cannot read property 'length' of undefined"

**诊断流程**:

```bash
# Layer 4: 分析 Console 错误
# 错误位置: Dashboard.vue:125

# 检查代码
# Dashboard.vue:125
# const count = data.dragon_tiger.length  ← 问题代码

# Layer 2: 检查 API 响应结构
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/data/dashboard/summary" \
  Authorization:"Bearer $TOKEN" | jq '.data'

# 发现问题: API 返回 dragon_tiger 为 null
{
  "dragon_tiger": null,  ← 应该是空数组 []
  "etf_data": [],
  ...
}

# 解决方案: 修复后端 API
# app/api/data.py
dragon_tiger = dragon_tiger_data if dragon_tiger_data else []

# 验证修复
# Layer 2: API 返回正确
# Layer 4: Console 无错误 ✓
```

**根本原因**: 后端 API 返回 null 而非空数组

**最佳实践**:
- API 应始终返回一致的数据类型
- 前端应添加空值检查

---

# 附录

## 完成检查清单

### 基本信息
- [ ] 功能名称: _______________
- [ ] 任务编号: _______________
- [ ] 分支名称: _______________
- [ ] 验证人: _______________
- [ ] 验证日期: _______________

### Layer 1: 代码层
- [ ] 代码已提交
- [ ] 单元测试通过
- [ ] 代码格式检查通过
- [ ] 无调试代码残留

### Layer 5: 数据层
- [ ] 数据库有数据
- [ ] 数据时效性合格
- [ ] 数据完整性检查通过
- [ ] 数据样本合理

### Layer 2: API 层
- [ ] 后端服务已启动
- [ ] API 端点验证通过
- [ ] HTTP 状态码正确
- [ ] 响应数据不为空
- [ ] 错误场景处理正确

### Layer 4: UI 层
- [ ] 浏览器页面正常加载
- [ ] 数据正确显示
- [ ] Console 无错误
- [ ] Network 请求成功
- [ ] 交互功能正常
- [ ] 截图已保存 (UI, Console, Network)

### Layer 3: 集成层
- [ ] Playwright 集成测试通过
- [ ] 数据流完整无断点
- [ ] 测试报告无失败

### 最终确认
- [ ] **所有 5 层检查通过，功能标记为 "完成"**
- [ ] 如有未通过项，已记录原因和后续计划

---

## 文档结构

```
docs/development-process/
├── README.md                          # 快速入门
├── INDEX.md                           # 文档索引
├── COMPLETE_GUIDE.md                  # 本文档 (完整参考)
├── definition-of-done.md              # 完成标准定义
├── onboarding-checklist.md            # 60 分钟上手清单
├── tool-selection-guide.md            # 工具选型完整指南
├── tool-comparison.md                 # 工具对比分析
├── manual-verification-guide.md       # Layer 4/5 手动验证
├── troubleshooting.md                 # 故障排查指南
├── training-outline.md                # 2 小时培训大纲
├── adoption-metrics.md                # SC-001 采纳指标
└── examples/                          # 实战示例
    ├── api-fix-example.md
    ├── ui-fix-example.md
    └── data-integration-example.md

specs/006-web-90-1/contracts/
├── tool-selection-decision-tree.md    # 30 秒工具决策
├── api-verification-guide.md          # API 验证完整指南
└── playwright-test-examples/          # Playwright 示例

scripts/
├── bash_aliases.sh                    # 快捷命令
├── api_templates.sh                   # API 验证模板
└── sql_templates.sql                  # SQL 查询模板
```

---

## 获取帮助

### 快速查找
- **完整文档索引**: `docs/development-process/INDEX.md`
- **60 分钟上手**: `docs/development-process/onboarding-checklist.md`
- **工具决策树**: `specs/006-web-90-1/contracts/tool-selection-decision-tree.md`
- **故障排查**: `docs/development-process/troubleshooting.md`

### 关键命令
```bash
# 加载快捷命令
source scripts/bash_aliases.sh

# 验证工具安装
mt-verify-tools

# 检查服务状态
mt-check-services

# 获取 API token
TOKEN=$(mt-token)

# 连接数据库
mt-db

# API 冒烟测试
source scripts/api_templates.sh
api_smoke_test
```

### 测试命令
```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 带截图测试
pytest tests/integration/ -v --headed --screenshot=on

# 代码质量
black app/ && flake8 app/
```

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，完整参考手册

---

**记住**: 功能可用性 > 代码正确性。只有用户能够成功使用的功能才算真正完成！
