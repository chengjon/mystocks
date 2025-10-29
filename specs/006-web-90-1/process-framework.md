# Web 应用开发流程框架 - Definition of Done

**版本**: 1.0
**日期**: 2025-10-29
**适用项目**: MyStocks 量化交易系统
**语言**: 中文

---

## 📖 概述 (Overview)

### 什么是"完成" (What Does "Done" Mean)

在新的开发流程中，**"完成"不再只是代码通过测试，而是用户可以实际使用功能并获得预期结果**。

**旧定义 (Old Definition)**:
```
✅ 代码编写完成
✅ 单元测试通过
❌ 用户无法使用 (90% 功能不可用)
```

**新定义 (New Definition)**:
```
✅ 代码编写完成
✅ 单元测试通过
✅ 集成测试通过 (数据流完整)
✅ 手动验证通过 (用户可见数据)
✅ 冒烟测试通过 (核心功能正常)
```

### 为什么要改变 (Why Change)

**当前问题**:
- 90% 的 Web 功能不可用
- 代码测试通过但用户看不到数据
- 后端未连接或连接错误
- 只有 Web 元素，没有实际数据

**根本原因**:
- 开发流程关注**代码正确性** (code correctness)
- 忽略了**功能可用性** (functional usability)

**新流程目标**:
- 确保用户可以完成预期任务
- 数据流从数据库 → 后端 → 前端 → UI 完整无断点
- 部署前发现集成问题

---

## 🏗️ 核心原则 (Core Principles)

### 原则 1: 功能可用性 > 代码正确性
**Functional Usability > Code Correctness**

- ❌ 错误: "测试通过了，功能完成了"
- ✅ 正确: "用户可以看到数据并完成任务，功能完成了"

### 原则 2: 端到端验证 (End-to-End Verification)

验证完整数据流:
```
数据库 → 后端 API → 前端请求 → 用户界面显示
   ✓        ✓          ✓            ✓
```

如果任何一层断开，功能未完成。

### 原则 3: 分层验证快速定位问题
**Layered Verification for Fast Problem Isolation**

当测试失败时，清楚知道哪一层出问题:
- 数据库层: 数据不存在
- API 层: API 返回错误
- 前端层: 前端未调用 API
- UI 层: 数据未渲染到界面

### 原则 4: 自动化 + 手动的平衡
**Balance Between Automation and Manual Verification**

- 自动化: 单元测试、集成测试 (快速反馈)
- 手动: 用户界面、数据正确性 (最终确认)

### 原则 5: 时间可预测性
**Predictable Time Investment**

每个验证步骤有明确的时间预算，总额外开销 <30%。

---

## 🔄 验证层次 (Verification Layers)

### Layer 1: 代码层 (Code Layer)
**目标**: 确保代码质量和基础正确性
**时间**: 5-10 分钟
**工具**: pytest, black, flake8, mypy

**验证内容**:
- ✅ 代码已提交到 feature 分支
- ✅ 单元测试通过
- ✅ 代码格式符合规范
- ✅ 类型检查通过 (如适用)

**命令示例**:
```bash
# 运行单元测试
pytest tests/unit/ -v

# 代码格式检查
black . && flake8 .

# 类型检查
mypy .
```

---

### Layer 2: API 层 (API Layer)
**目标**: 确保后端 API 正确返回数据
**时间**: 10-15 分钟
**工具**: MCP 工具, httpie, jq

**验证��容**:
- ✅ 所有相关 API 端点可访问
- ✅ HTTP 状态码正确 (200/201/204)
- ✅ 响应数据结构符合预期
- ✅ 错误场景正确处理 (400/401/500)

**命令示例**:
```bash
# 获取访问 token
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')

# 验证 API 端点
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN" | jq -e '.data != null'

# 验证错误场景
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer invalid_token" | jq -e '.status_code == 401'
```

**重要**: 所有 API 验证必须使用 MCP 工具或 httpie，不得跳过此步骤。

---

### Layer 3: 集成层 (Integration Layer)
**目标**: 确保数据流完整，各层无断点
**时间**: 5-10 分钟 (自动执行)
**工具**: Playwright, pytest

**验证内容**:
- ✅ Playwright 集成测试通过
- ✅ 数据流完整: 数据库 → 后端 → 前端 → UI
- ✅ 无层间断点
- ✅ 失败时明确指出哪一层出错

**命令示例**:
```bash
# 运行集成测试
pytest tests/integration/test_*.py -v

# 查看测试报告
pytest tests/integration/ -v --tb=short
```

**测试示例**:
```python
def test_dashboard_data_display(page, authenticated_session):
    """验证仪表板数据显示的完整流程"""
    # Layer 1: 数据库检查
    assert database_has_data("dashboard_summary")

    # Layer 2: API 检查
    api_response = requests.get("/api/data/dashboard/summary")
    assert api_response.status_code == 200
    assert len(api_response.json()["data"]) > 0

    # Layer 3 + 4: 前端 + UI 检查
    page.goto("/dashboard")
    page.wait_for_selector("[data-testid='dashboard-summary']")
    assert page.locator("[data-testid='data-table']").count() > 0, \
        "UI Layer Failed: 数据表未渲染"
```

---

### Layer 4: 用户界面层 (UI Layer)
**目标**: 确保用户可见数据，交互正常
**时间**: 10-20 分钟
**工具**: 浏览器 (Chrome), DevTools

**验证内容**:
- ✅ 浏览器中手动访问功能
- ✅ 数据正确显示 (保存截图)
- ✅ 无控制台错误 (F12 Console)
- ✅ 网络请求成功 (F12 Network)
- ✅ 交互功能正常 (按钮、表单等)

**验证步骤**:
1. 打开浏览器访问功能页面
2. **F12 → Console**: 检查无红色错误
3. **F12 → Network**: 检查所有 API 请求状态 200
4. 截图保存到 `docs/verification-screenshots/`
5. 测试交互功能 (点击按钮、提交表单)

**截图要求**:
- `feature-name-ui.png`: 完整页面展示
- `feature-name-console.png`: Console 无错误
- `feature-name-network.png`: Network 请求成功

---

### Layer 5: 数据验证层 (Data Validation Layer)
**目标**: 确保数据库有数据且数据有效
**时间**: 5-10 分钟
**工具**: pgcli, taos, SQL

**验证内容**:
- ✅ 使用 SQL 查询确认数据存在
- ✅ 数据时效性检查 (最新数据不超过 X 小时)
- ✅ 数据完整性检查 (关键字段无 NULL)

**命令示例**:
```bash
# PostgreSQL 数据验证
pgcli -h localhost -U mystocks_user -d mystocks

# 检查数据存在
SELECT COUNT(*) FROM cn_stock_top;

# 检查最新数据时间
SELECT MAX(trade_date) FROM cn_stock_top;

# 检查数据完整性
SELECT COUNT(*) FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;
```

---

## ⏱️ 时间预算 (Time Budget)

### 按工作类型的时间投入

| 工作类型 | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Layer 5 | **总计** |
|---------|---------|---------|---------|---------|---------|----------|
| **简单 Bug 修复** | 5 min | 10 min | 5 min | 10 min | 5 min | **35-55 min** |
| **中等功能** | 7 min | 12 min | 7 min | 15 min | 7 min | **50-80 min** |
| **复杂功能** | 10 min | 15 min | 10 min | 20 min | 10 min | **90-120 min** |

### 额外开销分析

假设原始开发时间 = 100 分钟 (编写代码 + 单元测试)

**简单 Bug**:
- 额外验证时间: 35 分钟
- 额外��销: 35% ✅ (符合 <30% 目标的宽松范围)

**中等功能**:
- 额外验证时间: 50 分钟
- 额外开销: 50% (首次可能超预算，熟练后降至 30%)

**复杂功能**:
- 额外验证时间: 90 分钟
- 额外开销: 90% (首次投入高，但避免返工节省更多时间)

**长期收益**:
- 减少 75% 的"以为完成但实际不可用"问题
- 减少 50% 的生产环境 Bug
- 提升用户信任度和产品质量

---

## 📊 工作流程图 (Workflow Diagram)

```
┌─────────────────┐
│  编写代码        │
│  Write Code     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Layer 1: 代码层  │
│ 单元测试 + 格式   │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│ Layer 2: API层   │
│ MCP 工具验证     │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│ Layer 3: 集成层  │
│ Playwright 测试  │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│ Layer 4: UI层    │
│ 手动浏览器验证   │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│ Layer 5: 数据层  │
│ SQL 查询验证     │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│  标记为"完成"    │
│  Mark as Done   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  提交 PR         │
│  Create PR      │
└─────────��───────┘
         │
         ▼
┌─────────────────┐
│  冒烟测试        │
│  Smoke Tests    │
└────────┬────────┘
         │ ✅ 通过
         ▼
┌─────────────────┐
│  部署到生产      │
│  Deploy         │
└─────────────────┘
```

**关键决策点 (Decision Points)**:

```
如果任何 Layer 失败:
  ├─ 数据库层失败 → 检查数据是否存在，运行数据导入脚本
  ├─ API 层失败 → 检查后端日志，修复 API 逻辑
  ├─ 集成层失败 → 检查测试报告，定位具体失败层
  ├─ UI 层失败 → 检查 Console 错误，修复前端代码
  └─ 数据层失败 → 检查 SQL 查询，确认数据完整性

  然后从失败的 Layer 重新开始验证
```

---

## 🚀 推广计划 (Rollout Plan)

### 策略: 全面立即采用 (Full Immediate Adoption)

考虑到当前 90% 功能不可用的严重性，选择全面立即采用新流程。

### Week 1: 培训和初步适应

**目标**: 全团队理解新流程，每人完成 1 个试运行任务

**Day 1-2**:
- 📚 全团队培训 (2 小时)
- 讲解新流程的 5 层验证模型
- 演示工具使用 (Playwright, httpie, pgcli)
- 发放文档和检查清单

**Day 3-5**:
- 🧪 每人选择 1 个简单任务试运行新流程
- 记录遇到的问题和困惑
- 每日站会分享经验

**Week 1 结束**:
- 收集反馈
- 调整检查清单和文档
- 优化工具配置

### Week 2: 全面推广

**目标**: 所有新任务必须使用新流程

**Day 1**:
- 宣布新流程正式生效
- 所有 feature 分支必须完成 Definition of Done 检查清单

**Day 2-5**:
- 每日站会分享验证经验
- Team Lead 抽查验证质量 (查看截图和测试报告)
- 记录平均验证时间

**Week 2 结束**:
- 统计验证时间是否在预算内
- 识别瓶颈环节

### Week 3-4: 流程优化

**目标**: 优化慢步骤，自动化重复任务

**优化措施**:
- 创建常用 API 验证脚本 (减少 Layer 2 时间)
- 自动截图工具 (减少 Layer 4 时间)
- SQL 查询模板库 (减少 Layer 5 时间)

**Week 4 结束**:
- 新流程成为团队习惯
- 验证时间稳定在预算内
- 更新 troubleshooting 文档

### 调整期 (2 周)

在推广期间，允许团队有 2 周调整期:
- 如果验证时间超预算 30%，允许跳过非关键验证
- 标记为"部分完成"，在下个 sprint 补充
- 重点确保核心功能通过完整验证

---

## 📖 相关文档 (Related Documentation)

### 开发者必读

1. **Definition of Done 检查清单**
   `contracts/definition-of-done-checklist.md`
   每个任务必须填写的完成检查清单

2. **手动验证指南**
   `contracts/manual-verification-checklist.md`
   Step-by-step 手动验证步骤

3. **冒烟测试清单**
   `contracts/smoke-test-checklist.md`
   部署前快速检查清单 (<5 分钟)

4. **工具选择决策树**
   `contracts/tool-selection-decision-tree.md`
   何时使用 MCP / AGENTS / 手动验证

5. **快速上手指南**
   `quickstart.md`
   30 分钟快速上手新流程

### 测试示例

6. **Playwright 测试示例**
   `contracts/playwright-test-examples/`
   完整的集成测试代码示例

### 故障排除

7. **常见问题解答**
   `troubleshooting.md` (将在 Phase 2 创建)
   常见失败模式和解决方案

---

## ✅ 成功标准 (Success Criteria)

### 短期目标 (1 个月)

- ✅ 所有新功能和 Bug 修复使用新流程
- ✅ 90% 标记为"完成"的功能用户可实际使用
- ✅ 验证时间稳定在预算内 (<30% 额外开销)
- ✅ "以为完成但实际不可用"问题减少 75%

### 长期目标 (3 个月)

- ✅ 生产环境 Bug 减少 50%
- ✅ 用户满意度提升
- ✅ 团队对功能可用性有信心
- ✅ 新流程成为团队文化的一部分

---

## 🎯 核心价值观 (Core Values)

### 用户第一 (User First)
功能是否"完成"由用户能否使用决定，而不是代码测试是否通过。

### 质量优于速度 (Quality Over Speed)
宁愿多花 30% 时间验证，也不要部署不可用的功能。

### 透明和可追溯 (Transparency and Traceability)
所有验证步骤有记录 (截图、测试报告、SQL 查询结果)。

### 持续改进 (Continuous Improvement)
根据团队反馈不断优化流程，减少不必要的步骤。

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，定义 5 层验证模型和推广计划
