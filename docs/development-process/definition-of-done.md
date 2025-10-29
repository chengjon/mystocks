# Definition of Done - 功能完成标准

**版本**: 1.0
**日期**: 2025-10-29
**适用项目**: MyStocks 量化交易系统
**语言**: 中文

---

## 📖 什么是 "完成" (What Does "Done" Mean)

在新的开发流程中，**"完成"不再只是代码通过测试，而是用户可以实际使用功能并获得预期结果**。

### 旧定义 vs 新定义

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
✅ API 层验证通过 (后端返回正确数据)
✅ 集成测试通过 (数据流完整)
✅ UI 层验证通过 (用户可见数据)
✅ 数据层验证通过 (数据库有数据)
```

---

## 🎯 核心原则 (Core Principles)

### 1. 功能可用性 > 代码正确性
**Functional Usability > Code Correctness**

- ❌ 错误: "测试通过了，功能完成了"
- ✅ 正确: "用户可以看到数据并完成任务，功能完成了"

### 2. 端到端验证 (End-to-End Verification)

验证完整数据流:
```
数据库 → 后端 API → 前端请求 → 用户界面显示
   ✓        ✓          ✓            ✓
```

**如果任何一层断开，功能未完成。**

### 3. 分层验证快速定位问题
**Layered Verification for Fast Problem Isolation**

当测试失败时，清楚知道哪一层出问题:
- **数据库层**: 数据不存在
- **API 层**: API 返回错误
- **前端层**: 前端未调用 API
- **UI 层**: 数据未渲染到界面

### 4. 自动化 + 手动的平衡
**Balance Between Automation and Manual Verification**

- **自动化**: 单元测试、集成测试 (快速反馈)
- **手动**: 用户界面、数据正确性 (最终确认)

### 5. 时间可预测性
**Predictable Time Investment**

每个验证步骤有明确的时间预算，总额外开销目标 <30%。

---

## 🔄 五层验证模型 (5-Layer Verification Model)

### Layer 1: 代码层 (Code Layer)

**目标**: 确保代码质量和基础正确性
**时间**: 5-10 分钟
**工具**: pytest, black, flake8, mypy

**验证清单**:
- [ ] 代码已提交到 feature 分支
- [ ] 单元测试通过: `pytest tests/unit/ -v`
- [ ] 代码格式符合规范: `black . && flake8 .`
- [ ] 类型检查通过 (如适用): `mypy .`
- [ ] 无调试代码残留 (console.log, print 语句)

**示例命令**:
```bash
# 运行单元测试
pytest tests/unit/ -v

# 代码格式检查
black . && flake8 .

# 类型检查 (可选)
mypy .
```

---

### Layer 2: API 层 (API Layer)

**目标**: 确保后端 API 正确返回数据
**时间**: 10-15 分钟
**工具**: httpie, jq, curl

**验证清单**:
- [ ] 后端服务已启动 (`http://localhost:8000`)
- [ ] 所有相关 API 端点可访问
- [ ] HTTP 状态码正确 (200/201/204)
- [ ] 响应数据结构符合预期
- [ ] 数据不为空: `jq -e '.data != null'`
- [ ] 错误场景正确处理 (400/401/500)

**示例命令**:
```bash
# 方法 1: 使用 httpie + jq
# 1. 获取访问 token
TOKEN=$(http POST http://localhost:8000/api/auth/login \
  username=admin password=admin123 | jq -r '.access_token')

# 2. 验证 API 端点
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN"

# 3. 验证数据不为空
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN" | jq -e '.data != null'

# 4. 验证错误场景
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer invalid_token" | jq -e '.status_code == 401'

# 方法 2: 使用快捷命令 (需先 source scripts/bash_aliases.sh)
mt-api /api/data/dashboard/summary
mt-test-api /api/data/dashboard/summary
```

**重要**:
- 所有 API 验证必须使用 httpie 或 curl，不得跳过此步骤
- 必须验证数据不为空，而不仅仅是状态码 200

---

### Layer 3: 集成层 (Integration Layer)

**目标**: 确保数据流完整，各层无断点
**时间**: 5-10 分钟 (自动执行)
**工具**: Playwright, pytest

**验证清单**:
- [ ] Playwright 集成测试通过
- [ ] 数据流完整: 数据库 → 后端 → 前端 → UI
- [ ] 无层间断点
- [ ] 失败时明确指出哪一层出错

**示例命令**:
```bash
# 运行集成测试
pytest tests/integration/test_*.py -v

# 查看详细测试报告
pytest tests/integration/ -v --tb=short

# 运行特定测试
pytest tests/integration/test_dashboard_data_display.py -v
```

**测试示例结构**:
```python
def test_dashboard_data_display(page, authenticated_session):
    """验证仪表板数据显示的完整流程"""

    # Layer 5: 数据库检查
    assert database_has_data("cn_stock_top"), \
        "Data Layer Failed: 数据库无数据"

    # Layer 2: API 检查
    api_response = requests.get(
        "http://localhost:8000/api/data/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert api_response.status_code == 200, \
        "API Layer Failed: API 返回错误"
    assert len(api_response.json()["data"]) > 0, \
        "API Layer Failed: API 返回空数据"

    # Layer 4: UI 检查
    page.goto("http://localhost:8000/dashboard")
    page.wait_for_selector("[data-testid='dashboard-summary']")
    assert page.locator("[data-testid='data-table']").count() > 0, \
        "UI Layer Failed: 数据表未渲染"
```

---

### Layer 4: 用户界面层 (UI Layer)

**目标**: 确保用户可见数据，交互正常
**时间**: 10-20 分钟
**工具**: 浏览器 (Chrome), DevTools

**验证清单**:
- [ ] 浏览器中手动访问功能页面
- [ ] 数据正确显示 (截图保存)
- [ ] 无控制台错误 (F12 → Console)
- [ ] 网络请求成功 (F12 → Network)
- [ ] 交互功能正常 (按钮、表单等)

**验证步骤**:

1. **打开页面**
   ```
   浏览器访问: http://localhost:8000/dashboard
   ```

2. **检查 Console (F12 → Console)**
   - ✅ 无红色错误 (Errors)
   - ⚠️ 如有 Warning，确认不影响功能
   - 截图保存到: `docs/verification-screenshots/feature-name-YYYYMMDD-console.png`

3. **检查 Network (F12 → Network)**
   - ✅ 所有 API 请求状态为 200/201/204
   - ✅ 无 failed 请求 (红色)
   - 截图保存到: `docs/verification-screenshots/feature-name-YYYYMMDD-network.png`

4. **检查数据显示**
   - ✅ 数据正确显示在页面上
   - ✅ 数据格式正确 (日期、数字、文本等)
   - 截图保存到: `docs/verification-screenshots/feature-name-YYYYMMDD-ui.png`

5. **测试交互功能**
   - ✅ 按钮点击响应正常
   - ✅ 表单提交成功 (如适用)
   - ✅ 数据刷新功能正常 (如适用)

**截图要求**:
- `feature-name-YYYYMMDD-ui.png`: 完整页面展示，数据清晰可见
- `feature-name-YYYYMMDD-console.png`: Console 无错误截图
- `feature-name-YYYYMMDD-network.png`: Network 请求成功截图

---

### Layer 5: 数据验证层 (Data Validation Layer)

**目标**: 确保数据库有数据且数据有效
**时间**: 5-10 分钟
**工具**: pgcli, taos, SQL

**验证清单**:
- [ ] 使用 SQL 查询确认数据存在
- [ ] 数据时效性检查 (最新数据不超过 X 小时)
- [ ] 数据完整性检查 (关键字段无 NULL)
- [ ] 数据样本合理 (查看 10 条记录确认数据质量)

**示例命令**:

**PostgreSQL 数据验证**:
```bash
# 连接数据库 (方法 1: 完整命令)
PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks

# 连接数据库 (方法 2: 使用快捷命令)
mt-db

# 1. 检查数据存在
SELECT COUNT(*) as record_count FROM cn_stock_top;
-- 期望: > 0

# 2. 检查最新数据时间
SELECT MAX(trade_date) as latest_date FROM cn_stock_top;
-- 期望: 今天或最近日期 (根据业务需求)

# 3. 检查数据完整性
SELECT COUNT(*) as null_count FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;
-- 期望: 0

# 4. 查看数据样本
SELECT * FROM cn_stock_top ORDER BY trade_date DESC LIMIT 10;
-- 目视检查数据合理性

# 退出
\q
```

**TDengine 数据验证** (如适用):
```bash
# 连接 TDengine (方法 1: 完整命令)
taos -h 192.168.123.104 -u root -ptaosdata

# 连接 TDengine (方法 2: 使用快捷命令)
mt-td

# 检查数据
USE market_data;
SELECT COUNT(*) FROM tick_data;
SELECT LAST(*) FROM tick_data;
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
- 额外开销: 35% ✅ (符合 <30% 目标的宽松范围)

**中等功能**:
- 额外验证时间: 50 分钟
- 额外开销: 50% (首次可能超预算，熟练后降至 30%)

**复杂功能**:
- 额外验证时间: 90 分钟
- 额外开销: 90% (首次投入高，但避免返工节省更多时间)

### 长期收益

- ✅ 减少 75% 的"以为完成但实际不可用"问题
- ✅ 减少 50% 的生产环境 Bug
- ✅ 提升用户信任度和产品质量
- ✅ 减少返工时间和成本

---

## 📋 完成检查清单 (Completion Checklist)

使用此检查清单确保功能真正完成:

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

### Layer 2: API 层
- [ ] 后端服务已启动
- [ ] API 端点验证通过
- [ ] HTTP 状态码正确
- [ ] 响应数据不为空
- [ ] 错误场景处理正确

### Layer 3: 集成层
- [ ] Playwright 集成测试通过
- [ ] 数据流完整无断点
- [ ] 测试报告无失败

### Layer 4: UI 层
- [ ] 浏览器页面正常加载
- [ ] 数据正确显示
- [ ] Console 无错误
- [ ] Network 请求成功
- [ ] 交互功能正常
- [ ] 截图已保存 (UI, Console, Network)

### Layer 5: 数据层
- [ ] 数据库有数据
- [ ] 数据时效性合格
- [ ] 数据完整性检查通过
- [ ] 数据样本合理

### 最终确认
- [ ] **所有 5 层检查通过，功能标记为 "完成"**
- [ ] 如有未通过项，已记录原因和后续计划

---

## 🚦 分层失败处理 (Failure Handling)

### 如果 Layer 1 失败
**问题**: 代码质量问题
**处理**: 修复代码错误，重新运行测试
**不要**: 跳过代码层直接测试后续层

### 如果 Layer 2 失败
**问题**: 后端 API 问题
**处理**:
1. 检查后端服务是否启动
2. 检查 API 路由是否正确
3. 检查数据库连接
4. 检查 API 返回数据是否为空

**不要**: 在 API 层未通过的情况下测试前端

### 如果 Layer 3 失败
**问题**: 数据流断点
**处理**:
1. 查看测试报告，确定失败的层
2. 回到对应的 Layer 手动验证
3. 修复断点后重新运行集成测试

**分层排查**:
```
AssertionError: Data Layer Failed: 数据库无数据
  → 回到 Layer 5 检查数据库

AssertionError: API Layer Failed: API 返回错误
  → 回到 Layer 2 检查 API

AssertionError: UI Layer Failed: 数据表未渲染
  → 回到 Layer 4 检查前端和 Network
```

### 如果 Layer 4 失败
**问题**: UI 显示问题
**处理**:
1. **Console 有错误**: 修复前端代码错误
2. **Network 请求失败**: 检查 API 调用是否正确
3. **数据未显示**: 检查前端渲染逻辑
4. **交互不响应**: 检查事件处理代码

### 如果 Layer 5 失败
**问题**: 数据库数据问题
**处理**:
1. 检查数据采集脚本是否运行
2. 检查数据库连接配置
3. 手动运行数据采集
4. 验证数据完整性

---

## 🎓 最佳实践 (Best Practices)

### 1. 按顺序验证，不要跳层
❌ 错误: 代码未测试就直接打开浏览器
✅ 正确: Layer 1 → 2 → 3 → 4 → 5 顺序验证

### 2. 失败立即停止，不要继续
❌ 错误: Layer 2 失败了还继续测试 Layer 4
✅ 正确: Layer 2 失败立即修复，通过后再继续

### 3. 保存证据，截图为证
❌ 错误: "我看了页面，数据都有"
✅ 正确: 保存 UI + Console + Network 三张截图

### 4. 记录问题，便于复盘
❌ 错误: 修复后不记录问题原因
✅ 正确: 在 PR 或文档中记录遇到的问题和解决方案

### 5. 自动化优先，手动补充
❌ 错误: 每次都手动测试所有功能
✅ 正确: 编写 Playwright 集成测试，手动测试仅验证 UI

---

## 📚 相关文档 (Related Documentation)

- **[完成检查清单](../specs/006-web-90-1/contracts/definition-of-done-checklist.md)**: 详细的逐项检查清单
- **[手动验证指南](../specs/006-web-90-1/contracts/manual-verification-checklist.md)**: Layer 4 UI 层详细验证步骤
- **[Playwright 测试示例](../specs/006-web-90-1/contracts/playwright-test-examples/)**: 集成测试代码示例
- **[快速上手指南](../specs/006-web-90-1/quickstart.md)**: 30 分钟快速入门
- **[流程框架文档](../specs/006-web-90-1/process-framework.md)**: 完整流程理念和设计

---

## ✅ 开始使用 (Getting Started)

### 第一次使用新流程？

1. **阅读**: [快速上手指南](../specs/006-web-90-1/quickstart.md) (30 分钟)
2. **安装工具**: Playwright, httpie, jq, pgcli
3. **配置快捷命令**: `source scripts/bash_aliases.sh`
4. **完成第一次完整验证**: 按照 5 层模型验证一个简单 Bug

### 每次开发新功能或修复 Bug

1. **开发前**: 阅读本文档，了解完成标准
2. **开发中**: 编写代码 + 单元测试 (Layer 1)
3. **开发后**: 按 Layer 1 → 5 顺序验证
4. **提交前**: 填写 [完成检查清单](../specs/006-web-90-1/contracts/definition-of-done-checklist.md)

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，定义 5 层验证模型和完成标准

---

## 附录：验证工作流程图

```
┌─────────────────┐
│  功能开发完成    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Layer 1: 代码   │ ← 单元测试、Linting
│ ✅ 通过?        │
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│ Layer 5: 数据库 │ ← SQL 查询验证
│ ✅ 有数据?      │ ← 数据时效性
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│ Layer 2: API    │ ← httpie / curl 测试
│ ✅ 返回正确?    │ ← 状态码、数据结构
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│ Layer 4: UI     │ ← 浏览器 DevTools
│ ✅ 显示正常?    │ ← Console、Network
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│ Layer 3: 集成   │ ← Playwright 测试
│ ✅ 端到端OK?    │ ← 完整用户流程
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│ ✅ Definition   │
│    of Done!     │
│                 │
│ 功能真正可用!   │
└─────────────────┘
```

**关键点**:
- 自底向上验证（Layer 5 → Layer 1）
- 任一层失败即停止，定位问题
- 所有层通过才算"完成"
- 每层有明确的验证标准
