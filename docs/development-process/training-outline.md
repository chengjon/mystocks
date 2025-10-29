# MyStocks 开发流程培训大纲

**版本**: 1.0
**日期**: 2025-10-29
**时长**: 2 小时
**目标**: 让团队掌握 5 层验证方法论，提升功能可用率从 10% 到 90%

---

## 📋 培训概览

### 培训目标

完成本培训后，参与者将能够:

1. ✅ 理解 5 层验证模型的核心概念
2. ✅ 使用正确的工具进行每一层验证
3. ✅ 独立完成一个完整的功能开发和验证流程
4. ✅ 快速诊断和定位常见问题
5. ✅ 应用 SC-001 指标追踪功能可用率

### 目标受众

- 后端开发工程师
- 前端开发工程师
- 全栈工程师
- QA 工程师
- 技术负责人

### 先决条件

- 熟悉 Python 和 Vue.js
- 了解 RESTful API 概念
- 基本的数据库知识 (PostgreSQL)
- 命令行操作经验

---

## 🗓️ 培训议程

### 第一部分: 背景与问题 (15 分钟)

#### 1.1 当前问题分析 (5 分钟)

**案例展示**: 真实的功能失败案例

```
问题: 龙虎榜页面显示"无数据"
代码测试: ✅ 通过
实际使用: ❌ 失败
```

**数据驱动的问题**:
- SC-001 基线: 功能可用率仅 10%
- 原因: 只验证代码层，忽略了其他 4 层
- 影响: 90% 的功能虽然代码正确但无法使用

**互动环节**:
> "在你的工作中，是否遇到过代码测试通过但实际不可用的情况？"

#### 1.2 5 层验证模型介绍 (10 分钟)

**核心理念**: 自底向上验证

```
Layer 5 (数据层)  → 数据库有数据且新鲜
   ↓
Layer 2 (API层)   → API 返回正确数据
   ↓
Layer 4 (UI层)    → UI 正确显示
   ↓
Layer 3 (集成层)  → 完整流程畅通
   ↓
Layer 1 (代码层)  → 代码质量合格
```

**为什么是 5 层？**
- 每一层代表一个可能的失败点
- 必须从底层到顶层依次验证
- 跳过任何一层都可能导致功能失败

**成功案例**:
- 实施前: 10% 功能可用率
- 实施后: 目标 90% 功能可用率
- 预期时间: 6 个月达标

---

### 第二部分: 5 层详解与工具 (45 分钟)

#### 2.1 Layer 5: 数据层验证 (10 分钟)

**目标**: 确保数据库中有正确且新鲜的数据

**常见问题**:
- ❌ 数据库为空
- ❌ 数据过期 (超过 1 天)
- ❌ 数据格式错误

**验证工具**: pgcli

**实操演示**:

```bash
# 连接数据库
source scripts/bash_aliases.sh
mt-db

# 验证数据存在
SELECT COUNT(*) FROM cn_stock_top;
-- 期望: > 0

# 验证数据新鲜度
SELECT MAX(trade_date) FROM cn_stock_top;
-- 期望: 今天或昨天的日期

# 验证数据完整性
SELECT * FROM cn_stock_top LIMIT 5;
-- 检查: 字段是否完整，值是否合理
```

**检查清单**:
- [ ] 数据库连接正常
- [ ] 表中有数据 (COUNT > 0)
- [ ] 数据新鲜 (MAX(date) 在 1 天内)
- [ ] 数据格式正确

**练习题**:
> 检查 `cn_stock_fund_flow_industry` 表的数据新鲜度

#### 2.2 Layer 2: API 层验证 (10 分钟)

**目标**: 确保 API 返回正确的数据

**常见问题**:
- ❌ API 返回 500 错误
- ❌ API 返回空数组
- ❌ API 响应时间过长 (> 2 秒)

**验证工具**: httpie (推荐) / curl

**实操演示**:

```bash
# 获取 token
TOKEN=$(mt-token)

# 测试龙虎榜 API
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"

# 期望结果:
# - HTTP 200
# - success: true
# - data 数组长度 = 5
# - 响应时间 < 2 秒
```

**检查清单**:
- [ ] API 返回 HTTP 200
- [ ] 响应包含 `success: true`
- [ ] data 字段有正确数量的记录
- [ ] 数据结构符合预期
- [ ] 响应时间 < 2 秒

**练习题**:
> 测试仪表盘汇总 API `/api/data/dashboard/summary`

#### 2.3 Layer 4: UI 层验证 (10 分钟)

**目标**: 确保前端正确显示数据

**常见问题**:
- ❌ 页面显示"无数据"
- ❌ 表格渲染错误
- ❌ JavaScript 控制台有错误

**验证工具**: 浏览器 DevTools (F12)

**实操演示**:

```
步骤 1: 打开页面
  http://localhost:5173/dragon-tiger

步骤 2: 打开 DevTools (F12)
  - Console 标签: 无红色错误
  - Network 标签: API 请求成功 (200)
  - Elements 标签: 数据正确渲染

步骤 3: 检查数据显示
  - 表格有数据行
  - 数据格式正确
  - 交互功能正常 (排序、筛选)
```

**检查清单**:
- [ ] Console 无 JavaScript 错误
- [ ] Network 中 API 请求成功
- [ ] 页面正确渲染数据
- [ ] 交互功能正常工作

**练习题**:
> 验证资金流向页面的 UI 显示

#### 2.4 Layer 3: 集成层验证 (10 分钟)

**目标**: 确保完整的用户流程畅通

**常见问题**:
- ❌ 登录后跳转失败
- ❌ 多步骤流程中断
- ❌ 页面间导航异常

**验证工具**: Playwright 自动化测试

**实操演示**:

```python
# tests/integration/test_user_login_flow.py

async def test_user_can_login_and_view_data(page):
    # 步骤 1: 访问登录页
    await page.goto("http://localhost:5173/login")

    # 步骤 2: 输入凭据
    await page.fill('input[name="username"]', "admin")
    await page.fill('input[name="password"]', "admin123")

    # 步骤 3: 点击登录
    await page.click('button[type="submit"]')

    # 步骤 4: 验证跳转到仪表盘
    await page.wait_for_url("**/dashboard")

    # 步骤 5: 验证数据加载
    await page.wait_for_selector('.stats-card')
    card_count = await page.locator('.stats-card').count()
    assert card_count == 4, "应该显示 4 个统计卡片"
```

**运行测试**:
```bash
pytest tests/integration/test_user_login_flow.py -v
```

**检查清单**:
- [ ] 登录流程完整
- [ ] 页面跳转正确
- [ ] 数据正确加载
- [ ] 用户交互流畅

**练习题**:
> 编写一个测试验证"查看龙虎榜数据"的完整流程

#### 2.5 Layer 1: 代码层验证 (5 分钟)

**目标**: 确保代码质量合格

**验证工具**: pytest, black, flake8

**实操演示**:

```bash
# 单元测试
pytest tests/unit/ -v

# 代码格式化
black app/

# 代码风格检查
flake8 app/
```

**检查清单**:
- [ ] 单元测试通过
- [ ] 代码格式规范
- [ ] 无代码风格警告

---

### 第三部分: 工具选择与实战 (30 分钟)

#### 3.1 工具决策树 (10 分钟)

**快速决策指南**:

```
需要验证哪一层？
├─ Layer 5 (数据库) → pgcli
├─ Layer 2 (API) → httpie (单个) / MCP Tools (多个)
├─ Layer 4 (UI) → 浏览器 DevTools
├─ Layer 3 (集成) → Playwright 测试
└─ Layer 1 (代码) → pytest
```

**工具对比演示**:

| 场景 | 手动操作 | MCP Tools | Playwright 脚本 | 推荐 |
|------|---------|-----------|----------------|------|
| 快速验证单个 API | 5 分钟 | 2 分钟 | 20 分钟 (编写) | httpie |
| 验证 10 个 API | 50 分钟 | 10 分钟 | 30 分钟 (编写) + 2 分钟 (运行) | MCP Tools |
| 回归测试 (重复 N 次) | 5N 分钟 | 2N 分钟 | 20 + 2N 分钟 | N>5: Playwright |

**互动环节**:
> "根据决策树，如果需要验证 15 个 API，你会选择哪种工具？"

#### 3.2 真实案例演练 (20 分钟)

**案例 1: 修复龙虎榜页面无数据问题**

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

**小组练习**:
> 分组诊断和修复"仪表盘卡片显示为 0"的问题

**案例 2: API 响应慢**

**问题描述**: 资金流向 API 响应时间超过 5 秒

**诊断流程**:

```bash
# Layer 2: 测量响应时间
time http GET "http://localhost:8000/api/market/v3/fund-flow" \
  Authorization:"Bearer $TOKEN"
# 结果: 5.2 秒 ← 确认问题

# Layer 5: 检查数据量
mt-db -c "SELECT COUNT(*) FROM cn_stock_fund_flow_industry;"
# 结果: 1,000,000 行

# 解决方案: 添加分页和索引
# 1. API 添加分页参数
# 2. 数据库添加索引

# 验证修复
time http GET "http://localhost:8000/api/market/v3/fund-flow?limit=50" \
  Authorization:"Bearer $TOKEN"
# 结果: 0.8 秒 ✓
```

---

### 第四部分: 流程集成与最佳实践 (25 分钟)

#### 4.1 DoD (Definition of Done) 标准 (10 分钟)

**新的完成定义**: 通过所有 5 层验证

**简单修改**:
- ✅ Layer 5: 数据正确
- ✅ Layer 2: API 正确
- ✅ Layer 4: UI 正确

**中等复杂度**:
- ✅ Layer 5, 2, 4 (同上)
- ✅ Layer 3: 集成测试通过

**复杂功能**:
- ✅ Layer 5, 2, 4, 3 (同上)
- ✅ Layer 1: 代码质量检查
- ✅ 截图证据保存到 `docs/verification-screenshots/`

**DoD 检查清单模板**:

```markdown
## 龙虎榜功能 DoD 检查清单

- [ ] Layer 5: 数据库有龙虎榜数据 (cn_stock_top 表)
- [ ] Layer 2: API /api/market/v3/dragon-tiger 返回正确数据
- [ ] Layer 4: 龙虎榜页面正确显示数据
- [ ] Layer 3: 集成测试通过 (test_dragon_tiger_flow.py)
- [ ] Layer 1: 单元测试通过
- [ ] 截图: dashboard-dragon-tiger.png
```

#### 4.2 SC-001 指标追踪 (5 分钟)

**指标定义**:
```
功能可用率 = (实际可用功能数 / 标记完成功能数) × 100%
```

**目标设定**:
- 基线: 10% (当前)
- 月度目标: 每月增加 13-14%
- 最终目标: 90% (6 个月)

**如何追踪**:

```markdown
## SC-001 每月追踪

### 2025-10 (Month 1)
- 标记完成: 20 个功能
- 实际可用: 2 个功能
- 可用率: 10%

### 2025-11 (Month 2)
- 标记完成: 25 个功能
- 实际可用: 6 个功能
- 可用率: 24% ✓ (+14%)

### 2025-12 (Month 3)
- 标记完成: 30 个功能
- 实际可用: 11 个功能
- 可用率: 37% ✓ (+13%)
```

**文档位置**: `docs/development-process/adoption-metrics.md`

#### 4.3 常见问题排查 (10 分钟)

**问题 1: API 返回 500 错误**

**排查步骤**:
```bash
# 1. 检查后端日志
tail -f /tmp/uvicorn.log

# 2. 检查数据库连接
mt-db -c "SELECT 1;"

# 3. 验证 API 路由
http GET http://localhost:8000/docs

# 4. 测试简化的 API 请求
```

**问题 2: 前端页面显示"无数据"**

**5 层诊断法**:
```
Layer 5 → Layer 2 → Layer 4
数据库   → API    → UI
↓         ↓        ↓
有数据?   返回数据? 显示数据?
```

**问题 3: 数据库连接失败**

**检查清单**:
- [ ] PostgreSQL 服务运行
- [ ] .env 配置正确
- [ ] 网络连通性
- [ ] 用户权限

**参考文档**: `docs/development-process/troubleshooting.md`

---

### 第五部分: 总结与行动计划 (5 分钟)

#### 5.1 关键要点回顾

1. **5 层验证模型**: 自底向上验证，缺一不可
2. **工具选择**: 根据场景选择合适工具
3. **DoD 标准**: 通过所有相关层才算完成
4. **SC-001 指标**: 追踪功能可用率，6 个月达到 90%

#### 5.2 立即行动

**第 1 周**:
- [ ] 完成 onboarding-checklist.md 上手清单
- [ ] 使用 5 层验证修复 1 个现有 Bug
- [ ] 运行一次完整验证流程

**第 1 月**:
- [ ] 独立完成 1 个新功能开发和验证
- [ ] 编写 1 个 Playwright 集成测试
- [ ] 贡献 1 个验证案例到文档

#### 5.3 资源与支持

**核心文档**:
- [开发流程快速入门](./README.md)
- [完成标准定义](./definition-of-done.md)
- [工具选型指南](./tool-selection-guide.md)
- [文档索引](./INDEX.md)

**快捷命令**:
```bash
# 加载快捷命令
source scripts/bash_aliases.sh

# 常用命令
mt-token     # 获取 API token
mt-db        # 连接数据库
mt-api-dragon # 测试龙虎榜 API
```

**获取帮助**:
- 📖 查看文档索引: `docs/development-process/INDEX.md`
- 🔍 搜索关键词: `grep -r "关键词" docs/development-process/`
- 💡 查看示例: `docs/development-process/examples/`

---

## 📝 培训反馈表

**培训后请完成以下反馈** (5 分钟):

1. **理解程度** (1-5 分):
   - 5 层验证模型: ___
   - 工具选择决策: ___
   - 实际操作流程: ___

2. **最有价值的部分**:
   - [ ] 5 层模型概念
   - [ ] 工具实操演示
   - [ ] 真实案例演练
   - [ ] DoD 标准定义

3. **需要更多练习的部分**:
   - [ ] Layer 5 (数据层)
   - [ ] Layer 2 (API 层)
   - [ ] Layer 4 (UI 层)
   - [ ] Layer 3 (集成层)
   - [ ] 工具使用

4. **建议与改进**:
   ```
   ___________________________________________
   ___________________________________________
   ```

---

## 🎯 培训检查清单 (讲师用)

### 准备工作 (培训前 1 天)

- [ ] 确认所有服务运行正常 (Backend + Frontend + Database)
- [ ] 验证所有示例代码可执行
- [ ] 准备演示环境和数据
- [ ] 打印培训材料和检查清单
- [ ] 准备分组练习的案例

### 材料清单

- [ ] 培训 PPT (基于本大纲)
- [ ] 上手清单打印版
- [ ] 快捷命令速查卡
- [ ] 工具决策树海报
- [ ] 真实案例分析文档

### 培训中检查点

**第一部分** (15 分钟):
- [ ] 参与者理解当前问题 (互动确认)
- [ ] 5 层模型概念清晰 (提问验证)

**第二部分** (45 分钟):
- [ ] 每层演示成功执行
- [ ] 参与者能跟随操作
- [ ] 练习题得到解答

**第三部分** (30 分钟):
- [ ] 工具选择决策清晰
- [ ] 小组练习完成
- [ ] 案例诊断正确

**第四部分** (25 分钟):
- [ ] DoD 标准理解
- [ ] SC-001 指标明确
- [ ] 排查方法掌握

**第五部分** (5 分钟):
- [ ] 行动计划明确
- [ ] 资源位置清楚
- [ ] 反馈表收集

---

## 📚 附录: 参考资源

### A. 文档链接

- [完整文档索引](./INDEX.md)
- [60 分钟上手清单](./onboarding-checklist.md)
- [API 验证完整指南](../../specs/006-web-90-1/contracts/api-verification-guide.md)
- [工具对比分析](./tool-comparison.md)
- [故障排查指南](./troubleshooting.md)

### B. 示例代码

- [API 修复示例](./examples/api-fix-example.md)
- [UI 修复示例](./examples/ui-fix-example.md)
- [数据集成示例](./examples/data-integration-example.md)
- [Playwright 测试示例](../../specs/006-web-90-1/contracts/playwright-test-examples/)

### C. 工具文档

- [httpie 官方文档](https://httpie.io/docs)
- [pgcli 官方文档](https://www.pgcli.com/)
- [Playwright 官方文档](https://playwright.dev/python/)
- [pytest 官方文档](https://docs.pytest.org/)

### D. 快捷命令速查

```bash
# 数据库验证
mt-db                          # 连接数据库
mt-db -c "SELECT COUNT(*) FROM cn_stock_top;"  # 执行查询

# API 验证
mt-token                       # 获取 token
mt-api-dragon                  # 测试龙虎榜 API
mt-api-summary                 # 测试仪表盘 API

# 测试运行
pytest tests/unit/ -v          # 单元测试
pytest tests/integration/ -v   # 集成测试

# 代码质量
black app/                     # 格式化代码
flake8 app/                    # 代码检查
```

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，2 小时培训大纲
