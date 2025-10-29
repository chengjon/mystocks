# 工具选型指南 (Tool Selection Guide)

**版本**: 1.0
**日期**: 2025-10-29
**目的**: 为 5 层验证模型选择合适的工具

---

## 📖 概述 (Overview)

本指南说明为什么选择这些工具，以及它们在 5 层验证中的作用。

**选型原则**:
1. **开源免费**: 所有工具开源，无许可证费用
2. **广泛使用**: 业界标准工具，社区支持强
3. **易于安装**: 支持 pip/npm/apt 一键安装
4. **学习曲线低**: 新人可在 30 分钟内上手
5. **功能完整**: 覆盖端到端验证需求

---

## 🔧 工具矩阵 (Tool Matrix)

| Layer | 工具 | 用途 | 安装方式 | 学习时间 |
|-------|-----|------|---------|----------|
| **Layer 1: 代码层** | pytest | Python 单元测试 | `pip install pytest` | 1 小时 |
| | black | 代码格式化 | `pip install black` | 10 分钟 |
| | flake8 | 代码风格检查 | `pip install flake8` | 10 分钟 |
| | mypy | 类型检查 (可选) | `pip install mypy` | 30 分钟 |
| **Layer 2: API 层** | httpie | HTTP 客户端 | `pip install httpie` | 15 分钟 |
| | jq | JSON 处理 | `apt install jq` | 20 分钟 |
| | curl | HTTP 工具 (备选) | 系统自带 | 10 分钟 |
| **Layer 3: 集成层** | Playwright | 浏览器自动化 | `pip install playwright` | 2 小时 |
| | pytest-playwright | Playwright + pytest 集成 | `pip install pytest-playwright` | 30 分钟 |
| **Layer 4: UI 层** | Chrome DevTools | 浏览器调试 | 浏览器自带 | 1 小时 |
| **Layer 5: 数据层** | pgcli | PostgreSQL CLI | `pip install pgcli` | 30 分钟 |
| | taos | TDengine CLI | TDengine 自带 | 20 分钟 |

---

## 📊 Layer 1: 代码层工具

### pytest - Python 测试框架

**为什么选择 pytest？**
- ✅ Python 社区最流行的测试框架
- ✅ 语法简洁，易于编写和维护
- ✅ 强大的插件生态系统
- ✅ 支持参数化测试、Fixture 等高级功能

**替代方案**:
- `unittest`: Python 标准库，语法冗长
- `nose2`: 功能类似 pytest，但社区较小

**安装**:
```bash
pip install pytest pytest-cov pytest-xdist
```

**基本用法**:
```bash
# 运行所有测试
pytest

# 运行特定目录
pytest tests/unit/

# 显示详细输出
pytest -v

# 生成测试覆盖率报告
pytest --cov=app tests/
```

---

### black - 代码格式化工具

**为什么选择 black？**
- ✅ "The uncompromising code formatter"
- ✅ 零配置，开箱即用
- ✅ 确保团队代码风格一致

**替代方案**:
- `autopep8`: 可配置性强，但需要配置
- `yapf`: Google 开发，功能强大但复杂

**安装**:
```bash
pip install black
```

**基本用法**:
```bash
# 格式化所有 Python 文件
black .

# 格式化特定文件
black app/main.py

# 检查但不修改
black --check .
```

---

### flake8 - 代码风格检查

**为什么选择 flake8？**
- ✅ 集成 pycodestyle + pyflakes + mccabe
- ✅ 检查代码风格和潜在错误
- ✅ 可配置性强

**替代方案**:
- `pylint`: 功能更强大，但规则过严
- `pycodestyle`: 只检查 PEP 8 风格

**安装**:
```bash
pip install flake8
```

**基本用法**:
```bash
# 检查所有 Python 文件
flake8 .

# 检查特定文件
flake8 app/main.py

# 忽略特定错误
flake8 --ignore=E501,W503 .
```

---

## 🌐 Layer 2: API 层工具

### httpie - 现代 HTTP 客户端

**为什么选择 httpie？**
- ✅ 语法简洁，比 curl 更易读
- ✅ 自动语法高亮 (JSON 格式化)
- ✅ 支持会话 (Session)
- ✅ 友好的错误消息

**替代方案**:
- `curl`: 功能强大但语法复杂
- `Postman`: GUI 工具，不适合自动化

**安装**:
```bash
pip install httpie
```

**基本用法**:
```bash
# GET 请求
http GET http://localhost:8000/api/data/dashboard/summary

# POST 请求
http POST http://localhost:8000/api/auth/login username=admin password=admin123

# 自定义 Header
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN"

# 下载文件
http --download GET http://localhost:8000/api/export/data
```

**httpie vs curl 对比**:
```bash
# httpie (简洁)
http POST http://localhost:8000/api/auth/login username=admin password=admin123

# curl (冗长)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

### jq - JSON 处理工具

**为什么选择 jq？**
- ✅ 命令行 JSON 处理标准工具
- ✅ 强大的过滤和转换功能
- ✅ 支持复杂查询 (类似 SQL)

**替代方案**:
- `python -m json.tool`: Python 自带，功能有限
- `jmespath`: 功能类似，但不如 jq 流行

**安装**:
```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq
```

**基本用法**:
```bash
# 格式化 JSON
echo '{"name":"John"}' | jq

# 提取字段
echo '{"name":"John","age":30}' | jq '.name'
# 输出: "John"

# 验证数据不为空
http GET http://localhost:8000/api/data/dashboard/summary | jq -e '.data != null'
# 输出: true (退出码 0) 或 false (退出码 1)

# 提取数组长度
http GET http://localhost:8000/api/market/dragon-tiger?limit=5 | jq '.data | length'
# 输出: 5
```

---

### curl - 经典 HTTP 工具 (备选)

**何时使用 curl？**
- ⚠️ 当 httpie 不可用时
- ⚠️ 当需要更底层的 HTTP 控制时
- ⚠️ 当编写 Shell 脚本时 (curl 更通用)

**基本用法**:
```bash
# GET 请求
curl -X GET http://localhost:8000/api/data/dashboard/summary

# POST 请求
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 自定义 Header
curl -X GET http://localhost:8000/api/data/dashboard/summary \
  -H "Authorization: Bearer $TOKEN"

# 只显示状态码
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
```

---

## 🎭 Layer 3: 集成层工具

### Playwright - 现代浏览器自动化

**为什么选择 Playwright？**
- ✅ 微软开发，现代化设计
- ✅ 支持所有主流浏览器 (Chromium, Firefox, WebKit)
- ✅ 自动等待机制 (减少 flaky 测试)
- ✅ 强大的调试工具 (Trace Viewer, Inspector)
- ✅ 原生支持 Python (不需要 Selenium WebDriver)

**替代方案**:
- `Selenium`: 老牌工具，但语法冗长，需要 WebDriver
- `Puppeteer`: 功能强大，但只支持 JavaScript

**安装**:
```bash
# 安装 Playwright
pip install playwright pytest-playwright

# 安装浏览器
playwright install chromium
```

**基本用法**:
```python
# tests/integration/test_example.py
def test_dashboard_display(page):
    # 访问页面
    page.goto("http://localhost:8000/dashboard")

    # 等待元素出现
    page.wait_for_selector("[data-testid='dashboard-summary']")

    # 断言元素存在
    assert page.locator("[data-testid='data-table']").count() > 0
```

**运行测试**:
```bash
# 运行所有集成测试
pytest tests/integration/ -v

# 启用调试模式 (慢速执行，查看浏览器)
pytest tests/integration/ --headed --slowmo=1000

# 生成 Trace (用于调试失败测试)
pytest tests/integration/ --tracing=on
```

---

## 🖥️ Layer 4: UI 层工具

### Chrome DevTools - 浏览器开发者工具

**为什么选择 Chrome DevTools？**
- ✅ 浏览器内置，无需安装
- ✅ 功能全面 (Console, Network, Performance, etc.)
- ✅ 实时查看网络请求和响应
- ✅ 强大的调试功能

**替代方案**:
- Firefox DevTools: 功能类似，某些方面更强 (如 CSS Grid 调试)
- Safari Web Inspector: macOS/iOS 调试必备

**主要功能**:

#### 1. Console (控制台)
- 查看 JavaScript 错误和警告
- 运行 JavaScript 代码
- 查看日志输出

**快捷键**: `Ctrl+Shift+J` (Windows/Linux) 或 `Cmd+Option+J` (macOS)

#### 2. Network (网络)
- 查看所有 HTTP 请求
- 检查请求/响应头
- 查看响应数据

**快捷键**: `Ctrl+Shift+E` (Windows/Linux)

#### 3. Elements (元素)
- 检查 HTML 结构
- 修改 CSS 样式
- 调试布局问题

**快捷键**: `Ctrl+Shift+C` (元素选择模式)

#### 4. Performance (性能)
- 录制性能分析
- 查看 FPS、内存使用
- 识别性能瓶颈

---

## 🗄️ Layer 5: 数据层工具

### pgcli - PostgreSQL 交互式客户端

**为什么选择 pgcli？**
- ✅ 自动补全 (表名、列名、SQL 关键字)
- ✅ 语法高亮
- ✅ 支持 `.pgclirc` 配置文件
- ✅ 更友好的错误消息

**替代方案**:
- `psql`: PostgreSQL 官方客户端，功能强大但不够友好
- `DBeaver`: GUI 工具，不适合快速验证

**安装**:
```bash
pip install pgcli
```

**基本用法**:
```bash
# 连接数据库
pgcli -h localhost -U mystocks_user -d mystocks

# 使用密码环境变量
PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks

# 常用命令
\dt           # 列出所有表
\d table_name # 查看表结构
\l            # 列出所有数据库
\q            # 退出
```

---

### taos - TDengine CLI

**为什么选择 taos？**
- ✅ TDengine 官方客户端
- ✅ 支持所有 TDengine 功能
- ✅ 语法类似 SQL，易于学习

**安装**:
- TDengine 安装时自动包含

**基本用法**:
```bash
# 连接 TDengine
taos -h 192.168.123.104 -u root -ptaosdata

# 常用命令
SHOW DATABASES;           # 列出所有数据库
USE market_data;          # 切换数据库
SHOW TABLES;              # 列出所有表
DESCRIBE table_name;      # 查看表结构
SELECT LAST(*) FROM tick_data;  # 查看最新数据
quit;                     # 退出
```

---

## 🚀 工具组合示例

### 完整验证流程工具链

```bash
# Layer 1: 代码层
pytest tests/unit/ -v        # 单元测试
black . && flake8 .          # 代码质量

# Layer 2: API 层
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN" | jq -e '.data != null'

# Layer 3: 集成层
pytest tests/integration/ -v

# Layer 4: UI 层
# 手动打开浏览器 → DevTools (F12)

# Layer 5: 数据层
pgcli -h localhost -U mystocks_user -d mystocks \
  -c "SELECT COUNT(*) FROM cn_stock_top;"
```

---

## 📦 快速安装脚本

```bash
#!/bin/bash
# install_verification_tools.sh

echo "Installing verification tools..."

# Layer 1: 代码层
pip install pytest pytest-cov black flake8 mypy

# Layer 2: API 层
pip install httpie
sudo apt install jq  # macOS: brew install jq

# Layer 3: 集成层
pip install playwright pytest-playwright
playwright install chromium

# Layer 4: UI 层 (浏览器自带，无需安装)

# Layer 5: 数据层
pip install pgcli

echo "✅ All tools installed successfully!"
echo "Run 'source scripts/bash_aliases.sh' to load shortcuts."
```

---

## 📚 学习资源

### pytest
- 官方文档: https://docs.pytest.org/
- 快速入门: 30 分钟
- 推荐教程: Real Python - Pytest

### Playwright
- 官方文档: https://playwright.dev/python/
- 快速入门: 1 小时
- 推荐教程: Playwright 官方教程

### httpie
- 官方文档: https://httpie.io/docs/cli
- 快速入门: 15 分钟
- 推荐: httpie cheat sheet

### jq
- 官方文档: https://stedolan.github.io/jq/
- 快速入门: 20 分钟
- 推荐: jq playground (在线练习)

### Chrome DevTools
- 官方文档: https://developer.chrome.com/docs/devtools/
- 快速入门: 1 小时
- 推荐: Google DevTools 教程

---

## 🆚 工具对比

### API 测试: httpie vs curl vs Postman

| 特性 | httpie | curl | Postman |
|-----|--------|------|---------|
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **自动化** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **语法高亮** | ✅ | ❌ | ✅ |
| **GUI** | ❌ | ❌ | ✅ |
| **脚本集成** | ✅ | ✅ | ⚠️ |
| **推荐场景** | 手动验证 | Shell 脚本 | 团队协作 |

**结论**: httpie 最适合手动 API 验证

---

### 浏览器自动化: Playwright vs Selenium

| 特性 | Playwright | Selenium |
|-----|-----------|----------|
| **现代化** | ⭐⭐⭐⭐⭐ (2020) | ⭐⭐⭐ (2004) |
| **自动等待** | ✅ | ❌ (需手动) |
| **速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **调试工具** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Python 支持** | ✅ 原生 | ⚠️ 需 WebDriver |
| **学习曲线** | ⭐⭐⭐⭐ | ⭐⭐ |

**结论**: Playwright 更现代、更易用、更可靠

---

## 🤖 MCP (Model Context Protocol) 工具

### 什么是 MCP？

**MCP (Model Context Protocol)** 是 Anthropic 开发的协议,允许 AI 助手(如 Claude)通过标准化接口访问外部工具和服务。

**核心理念**: 让 AI 直接调用工具,而不是生成命令让人执行

### MCP Tools 在验证中的角色

MCP Tools 提供了一种**中间自动化层级**:
- 比完全手动验证更快
- 比编写完整 Playwright 脚本更灵活
- 适合探索性验证和快速迭代

### 可用的 MCP Tools

#### 1. MCP Playwright Tools

**用途**: 浏览器自动化的快速交互式验证

**主要工具**:
```python
# 导航到页面
mcp__playwright__browser_navigate(url="http://localhost:5173/dragon-tiger")

# 获取页面快照(文本表示)
mcp__playwright__browser_snapshot()

# 点击元素
mcp__playwright__browser_click(
    element="登录按钮",
    ref="button[type=submit]"
)

# 填写表单
mcp__playwright__browser_fill_form(fields=[
    {"name": "用户名", "type": "textbox", "ref": "input#username", "value": "admin"},
    {"name": "密码", "type": "textbox", "ref": "input#password", "value": "admin123"}
])

# 截图
mcp__playwright__browser_take_screenshot(
    filename="login-success.png"
)

# 等待文本出现
mcp__playwright__browser_wait_for(
    text="登录成功"
)

# 查看控制台消息
mcp__playwright__browser_console_messages(onlyErrors=True)

# 查看网络请求
mcp__playwright__browser_network_requests()
```

#### 2. MCP Chrome DevTools

**用途**: 真实浏览器环境的调试和验证

**主要工具**:
```python
# 创建新页面并导航
mcp__chrome-devtools__new_page(url="http://localhost:5173/dashboard")

# 获取页面快照
mcp__chrome-devtools__take_snapshot()

# 点击元素
mcp__chrome-devtools__click(uid="element_123")

# 填写表单
mcp__chrome-devtools__fill_form(elements=[
    {"uid": "input_1", "value": "admin"},
    {"uid": "input_2", "value": "admin123"}
])

# 截图
mcp__chrome-devtools__take_screenshot(filename="page.png")

# 查看控制台消息
mcp__chrome-devtools__list_console_messages(types=["error"])

# 查看网络请求
mcp__chrome-devtools__list_network_requests()

# 执行 JavaScript
mcp__chrome-devtools__evaluate_script(
    function="() => document.querySelectorAll('table tr').length"
)
```

### 何时使用 MCP Tools？

**✅ 推荐使用场景**:
1. **探索性验证**: 首次查看页面,不确定需要验证什么
2. **快速原型**: 需要快速验证想法,无需完整脚本
3. **一次性验证**: 不会重复运行的验证任务
4. **调试问题**: 需要交互式探索问题原因
5. **截图证据**: 需要快速生成验证截图

**❌ 不推荐场景**:
1. **复杂流程**: 超过 5 个步骤的流程应该写 Playwright 脚本
2. **重复验证**: 需要每次 PR 运行的测试应该自动化
3. **CI/CD 集成**: MCP Tools 不能在 CI/CD 中运行
4. **条件逻辑**: 需要 if/else 判断的复杂场景

### MCP Tools vs Playwright 脚本

| 特性 | MCP Tools | Playwright 脚本 |
|------|----------|----------------|
| **启动速度** | ⭐⭐⭐⭐⭐ 即时 | ⭐⭐⭐ 需要编写 |
| **灵活性** | ⭐⭐⭐⭐⭐ 交互式 | ⭐⭐⭐ 固定流程 |
| **可重复性** | ⭐⭐ 手动重新执行 | ⭐⭐⭐⭐⭐ 自动化 |
| **复杂逻辑** | ⭐⭐ 有限 | ⭐⭐⭐⭐⭐ 完全控制 |
| **CI/CD 集成** | ❌ 不支持 | ✅ 支持 |
| **学习曲线** | ⭐⭐⭐⭐⭐ 即用 | ⭐⭐⭐ 需学习 |
| **适用场景** | 探索、调试 | 自动化、回归测试 |

### 实战示例

#### 示例 1: 验证龙虎榜页面显示

**场景**: 首次开发龙虎榜页面,需要快速验证显示是否正确

**使用 MCP Tools**:
```python
# 1. 导航到页面
mcp__playwright__browser_navigate(url="http://localhost:5173/dragon-tiger")

# 2. 获取页面快照,检查元素
snapshot = mcp__playwright__browser_snapshot()
# 查看: 是否有表格、标题、数据行？

# 3. 检查控制台错误
errors = mcp__playwright__browser_console_messages(onlyErrors=True)
# 确认: 无红色错误

# 4. 截图证明
mcp__playwright__browser_take_screenshot(filename="dragon-tiger-verified.png")
```

**用时**: 3 分钟

#### 示例 2: 调试登录失败问题

**场景**: 用户报告无法登录,需要快速定位问题

**使用 MCP Tools**:
```python
# 1. 打开登录页
mcp__chrome-devtools__new_page(url="http://localhost:5173/login")

# 2. 填写表单
mcp__chrome-devtools__fill_form(elements=[
    {"uid": "input#username", "value": "admin"},
    {"uid": "input#password", "value": "wrong_password"}
])

# 3. 点击登录
mcp__chrome-devtools__click(uid="button[type=submit]")

# 4. 查看网络请求
requests = mcp__chrome-devtools__list_network_requests()
# 检查: API 是否返回 401？

# 5. 查看控制台错误
errors = mcp__chrome-devtools__list_console_messages(types=["error"])
# 查找: 是否有具体错误消息？

# 6. 截图错误状态
mcp__chrome-devtools__take_screenshot(filename="login-error.png")
```

**用时**: 5 分钟定位问题

#### 示例 3: 系统化多端点验证

**场景**: 需要验证所有 4 个数据 API 端点

**使用 MCP Tools**:
```bash
# 注意: 这种系统化验证适合使用 MCP Tools
# 因为可以快速迭代测试多个端点

# 1. 龙虎榜 API
mcp__playwright__browser_navigate(url="http://localhost:8000/api/market/v3/dragon-tiger?limit=5")
mcp__playwright__browser_snapshot()  # 检查 JSON 响应

# 2. ETF 数据 API
mcp__playwright__browser_navigate(url="http://localhost:8000/api/market/v3/etf-data?limit=5")
mcp__playwright__browser_snapshot()

# 3. 资金流向 API
mcp__playwright__browser_navigate(url="http://localhost:8000/api/market/v3/fund-flow?industry_type=csrc&limit=5")
mcp__playwright__browser_snapshot()

# 4. 竞价抢筹 API
mcp__playwright__browser_navigate(url="http://localhost:8000/api/market/v3/chip-race?limit=5")
mcp__playwright__browser_snapshot()
```

**用时**: 8 分钟验证 4 个端点

### MCP Tools 最佳实践

#### ✅ 做法

1. **用于探索**: 首次验证使用 MCP Tools 快速探索
2. **截图证明**: 每次验证生成截图作为证据
3. **检查错误**: 总是检查控制台错误和网络请求
4. **文档记录**: 将 MCP 命令记录在文档中供参考

#### ❌ 避免

1. **不要过度使用**: 复杂流程应该写 Playwright 脚本
2. **不要依赖手动**: 重复验证应该自动化
3. **不要跳过检查**: 不要只看 UI,忽略控制台错误
4. **不要省略截图**: 截图是重要的验证证据

### MCP Tools 工作流程

```
开始验证
    ↓
使用 MCP Tools 快速验证
    ↓
验证通过? ─ 否 → 修复问题 → 重新验证
    ↓ 是
生成截图证明
    ↓
需要重复运行? ─ 是 → 转换为 Playwright 脚本
    ↓ 否
完成(一次性验证)
```

### MCP Tools 速查表

| 需求 | MCP Tool | 示例 |
|------|----------|------|
| 打开页面 | browser_navigate | `url="http://..."` |
| 查看页面 | browser_snapshot | 文本表示的页面结构 |
| 点击按钮 | browser_click | `element="登录", ref="button"` |
| 填写表单 | browser_fill_form | `fields=[{...}]` |
| 截图 | browser_take_screenshot | `filename="page.png"` |
| 等待文本 | browser_wait_for | `text="加载完成"` |
| 查看错误 | console_messages | `onlyErrors=True` |
| 查看网络 | network_requests | 所有 HTTP 请求 |
| 执行 JS | browser_evaluate | `function="() => ..."` |

### 参考文档

- **MCP Playwright Tools**: 完整工具列表参见 Claude Code 工具文档
- **MCP Chrome DevTools**: Chrome DevTools Protocol 的 MCP 包装
- **使用示例**: `specs/006-web-90-1/contracts/tool-selection-decision-tree.md`

---

## ✅ 检查清单

- [ ] 已安装所有必需工具 (pytest, httpie, jq, Playwright, pgcli)
- [ ] 已配置快捷命令 (`source scripts/bash_aliases.sh`)
- [ ] 已验证工具可用 (`mt-verify-tools`)
- [ ] 已阅读工具文档 (至少浏览官方快速入门)
- [ ] 已完成第一次完整验证流程
- [ ] 了解何时使用 MCP Tools vs Playwright 脚本

---

**版本历史**:
- v1.1 (2025-10-29): 添加 MCP Tools 使用指南和实战示例
- v1.0 (2025-10-29): 初始版本，定义工具选型标准和推荐工具
