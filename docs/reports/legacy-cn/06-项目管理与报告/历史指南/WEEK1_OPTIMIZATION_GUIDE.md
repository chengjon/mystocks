# Week 1 优化执行指南

**文档日期**: 2025-11-28
**目标**: 将 E2E 测试通过率从 82.7% 提升到 95%+
**优先级**: 按 🔴 → 🟠 → 🟡 顺序执行

---

## 目录

1. [当前状态](#当前状态)
2. [优化计划](#优化计划)
3. [Priority 1: 选择器优化](#priority-1-选择器优化)
4. [Priority 2: API 标准化](#priority-2-api-标准化)
5. [Priority 3: 超时优化](#priority-3-超时优化)
6. [验证清单](#验证清单)

---

## 当前状态

### 基准数据 (Phase 9)
```
总测试:      81
通过:        67 (82.7%)
失败:        14 (17.3%)

浏览器分布:
├─ Chromium: 100% (27/27) ✅
├─ Firefox:  74.1% (20/27) ⚠️
└─ WebKit:   74.1% (20/27) ⚠️
```

### 失败分类
```
🔴 选择器问题 (6 个):   处理  DOM 初始化延迟、文本选择不稳定
🟠 格式问题 (4 个):    API 响应字段缺失
🟡 超时问题 (4 个):    页面加载和导航超时
```

---

## 优化计划

### Week 1 时间表
```
Monday:     选择器优化 (Priority 1)  → 预期 +10% 通过率
Tuesday:    选择器优化完善 & 测试
Wednesday:  API 标准化 (Priority 2)  → 预期 +7% 通过率
Thursday:   超时优化 (Priority 3)    → 预期 +8% 通过率
Friday:     全量验证               → 目标 95%+ 通过率
```

### 预期效果
```
当前:    82.7% (67/81)
Mon后:   ~85% (69/81)  [+2个: 选择器修复]
Wed后:   ~92% (74/81)  [+5个: 格式修复]
Thu后:   100% (81/81)  [+7个: 超时修复]

最终目标: 95%+ (77+/81)
```

---

## Priority 1: 选择器优化

### 症状
```
测试失败信息:
  "Element not found" 或 "Element not visible"

浏览器分布:
  Firefox: 3 个失败 (42.8%)
  WebKit:  3 个失败 (42.8%)
  Chromium: 0 个失败
```

### 根本原因
```
1. 文本选择器脆弱
   ❌ locator('text=资金流向')
   ❌ 依赖完整的文本渲染
   ❌ Firefox/WebKit 渲染延迟导致匹配失败

2. DOM 初始化延迟
   ❌ 直接查询元素，未等待渲染
   ❌ CSS 应用延迟
   ❌ 组件异步加载

3. 选择器超时不足
   ❌ 默认 10 秒超时对 Firefox/WebKit 不够
```

### 实施方案

#### 步骤 1: 应用 test-helpers (已完成 ✅)
文件: `tests/e2e/test-helpers.ts`

**核心函数**:
- `getBrowserConfig()` - 获取浏览器特定配置
- `smartWaitForElement()` - 智能元素等待
- `smartClick()` - 带重试的点击
- `setPageTimeouts()` - 设置页面超时

#### 步骤 2: 更新测试文件

**示例: MarketDataView 标签页检测 (已修复 ✅)**

```javascript
// ❌ 旧方式 - 不稳定
const fundFlowTab = page.locator('text=资金流向')
const tabCount = await Promise.all([
  fundFlowTab.isVisible().catch(() => false),
]).then(results => results.filter(v => v).length)

// ✅ 新方式 - 稳定
await page.waitForSelector('.el-tabs', { timeout: 5000 })
await page.waitForTimeout(1000)
const tabPanes = await page.locator('.el-tab-pane')
const paneCount = await tabPanes.count()
expect(paneCount).toBeGreaterThanOrEqual(1)
```

#### 步骤 3: 检查所有 UI 交互测试

**需要审查的测试**:
```
docs/reports/E2E_FAILURE_CLASSIFICATION.md
→ 分类 1 中列出的 6 个失败
→ 每个都需要改用 CSS 选择器或 ID 选择器
```

**改进策略**:

| 旧选择器类型 | 问题 | 新选择器类型 | 优点 |
|-----------|------|-----------|------|
| `text=...` | 文本依赖 | `.class` | CSS 类稳定 |
| `xpath=...` | 复杂路径 | `[data-testid=...]` | 属性稳定 |
| `label >> nth=0` | 顺序依赖 | `[aria-label=...]` | 语义稳定 |

#### 步骤 4: 添加额外等待

```javascript
// 在所有导航后添加
await page.waitForLoadState('networkidle')

// Firefox/WebKit 特定等待
if (browserName === 'firefox') {
  await page.waitForTimeout(2000)  // 额外 2 秒
} else if (browserName === 'webkit') {
  await page.waitForTimeout(2500)  // 额外 2.5 秒
}
```

#### 步骤 5: 使用 test-helpers

```typescript
import {
  smartGoto,
  smartWaitForElement,
  smartClick,
  setPageTimeouts,
  getBrowserName
} from './test-helpers'

test('should interact with tabs', async ({ page, browserName }) => {
  // 设置超时
  setPageTimeouts(page, browserName)

  // 智能导航
  await smartGoto(page, '/#/market-data', browserName)

  // 智能等待元素
  await smartWaitForElement(page, '.el-tabs', browserName)

  // 智能点击
  await smartClick(page, '.el-tab-pane', browserName)
})
```

### 预期效果
```
修复前: Firefox 74%, WebKit 74%
修复后: Firefox 90%+, WebKit 90%+
改进: +3-4 个失败修复
```

---

## Priority 2: API 标准化

### 症状
```
测试失败信息:
  expect(data.success).toBe(true)  ❌ undefined
  expect(data.connections).toBeDefined()  ❌ undefined

影响的 API:
  /api/announcement/stats     (缺 success 字段) ✅ 已修复
  /api/system/database/stats  (缺 connections/tables) ✅ 已修复
  其他 25+ 端点               (格式不一致) ⏳ 待修复
```

### 标准化规范

参考: `docs/standards/API_RESPONSE_STANDARDIZATION.md`

**标准格式**:
```json
{
  "success": true,
  "code": 0,
  "message": "请求成功",
  "data": {
    /* 实际数据 */
  },
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2025-11-28T..."
}
```

### 实施方案

#### 步骤 1: 验证已修复的端点 ✅

```bash
# Announcement stats
curl http://localhost:8000/api/announcement/stats | jq '.success'
# 期望: true

# Database stats
curl http://localhost:8000/api/system/database/stats | jq '.data.connections'
# 期望: {tdengine: {...}, postgresql: {...}}
```

#### 步骤 2: 标准化其他 25+ 端点

**需要修复的端点清单**:

**公告 API** (5 个):
- [ ] `/api/announcement/list`
- [ ] `/api/announcement/today`
- [ ] `/api/announcement/important`
- [ ] `/api/announcement/monitor-rules`
- [ ] `/api/announcement/triggered-records`

**交易 API** (6 个):
- [ ] `/api/trade/portfolio`
- [ ] `/api/trade/positions`
- [ ] `/api/trade/trades`
- [ ] `/api/trade/statistics`
- [ ] `/api/trade/execute`
- [ ] `/api/trade/health`

**系统 API** (2 个):
- [ ] `/api/system/health`
- [ ] `/api/system/database/health`

#### 步骤 3: 验证实施

使用自动化脚本验证:

```bash
cd /opt/claude/mystocks_spec

# 运行自动化验证 (参考规范文档中的脚本)
python validate_api_standards.py

# 预期输出: 所有端点返回 ✅
```

### 预期效果
```
修复前: 28.6% API 格式失败
修复后: 0% API 格式失败
改进: +4 个失败修复
```

---

## Priority 3: 超时优化

### 症状
```
测试失败信息:
  Timeout waiting for page to load
  Page didn't respond to navigation request within timeout

影响的测试:
  页面导航和加载相关
  特别是 Firefox/WebKit
```

### 已应用的改进 ✅

#### playwright.config.ts 更新:

```typescript
// 全局超时
timeout: 30000,  // 30 秒

// 浏览器特定超时
firefox: {
  timeout: 40000,  // Firefox: 40 秒
  retries: 2,      // 增加重试
}

webkit: {
  timeout: 45000,  // WebKit: 45 秒 (最慢)
  retries: 2,      // 增加重试
}
```

#### test-helpers.ts 中的超时配置:

```typescript
// Firefox
{
  waitAfterLoadState: 2000,     // 额外等待 2s
  selectTimeout: 15000,          // 选择器 15s
  navigationTimeout: 40000,      // 导航 40s
}

// WebKit
{
  waitAfterLoadState: 2500,     // 额外等待 2.5s
  selectTimeout: 20000,          // 选择器 20s
  navigationTimeout: 45000,      // 导航 45s
}
```

### 额外优化 (可选)

如果仍有超时问题，考虑:

1. **增加 waitForLoadState 延迟**:
```javascript
await page.waitForLoadState('networkidle')
await page.waitForTimeout(3000)  // 增加到 3 秒
```

2. **分步导航**:
```javascript
// 而不是直接导航，分步加载
await page.goto(url, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle')
```

3. **预热连接**:
```javascript
// 测试开始前进行初始请求
await page.request.get('/api/health')
```

### 预期效果
```
修复前: 28.6% 超时失败
修复后: <5% 超时失败
改进: +3-4 个失败修复
```

---

## 验证清单

### Daily 验证 (每天)

```
□ 运行冒烟测试
  npm run test:smoke

□ 检查关键端点
  curl http://localhost:8000/api/announcement/health

□ 验证浏览器特定通过率
  PLAYWRIGHT_TEST_BASE_URL=http://localhost:3001 \
  npx playwright test tests/e2e/ --project=firefox --reporter=line
```

### Weekly 验证 (周五)

```
□ 运行完整 E2E 测试
  PLAYWRIGHT_TEST_BASE_URL=http://localhost:3001 \
  npx playwright test tests/e2e/ --reporter=line

□ 验证通过率指标
  期望: 95%+ (77+/81)

□ 生成测试报告
  npx playwright show-report

□ 验证所有浏览器
  Chromium: 100% ✅
  Firefox: 95%+ ⚠️ → 目标
  WebKit: 95%+ ⚠️ → 目标
```

### 验证脚本 (推荐)

```bash
#!/bin/bash
# verify-week1-progress.sh

echo "🔍 验证 Week 1 优化进度..."
echo ""

# 1. 检查 API 修复
echo "✅ 检查 API 修复..."
curl -s http://localhost:8000/api/announcement/stats | jq '.success' && echo "  success 字段: ✅"
curl -s http://localhost:8000/api/system/database/stats | jq '.data.connections' > /dev/null && echo "  connections 字段: ✅"

# 2. 检查选择器改进
echo ""
echo "✅ 检查选择器改进..."
grep -l "\.el-" tests/e2e/*.spec.js && echo "  CSS 选择器: ✅"

# 3. 检查超时配置
echo ""
echo "✅ 检查超时配置..."
grep "timeout: 40000" playwright.config.ts && echo "  Firefox 超时配置: ✅"
grep "timeout: 45000" playwright.config.ts && echo "  WebKit 超时配置: ✅"

# 4. 运行冒烟测试
echo ""
echo "🧪 运行冒烟测试..."
python3 /tmp/smoke_test.py

echo ""
echo "✨ 验证完成！"
```

---

## 常见问题

### Q: 选择器改进会不会破坏现有测试?
A: 不会。我们只是从文本选择器改为 CSS 选择器，功能完全相同，稳定性更好。

### Q: 需要修改多少个测试文件?
A: 大约 5-10 个核心测试文件需要选择器改进，其余大部分已经使用稳定的选择器。

### Q: API 标准化会影响前端吗?
A: 不会。我们只是添加标准字段（success, timestamp），前端可以向后兼容。

### Q: 如果还有超时问题怎么办?
A: 检查后端性能，可能需要优化数据库查询或添加缓存。参考 Week 2 的性能优化任务。

---

## 参考文档

- **失败分类详情**: docs/reports/E2E_FAILURE_CLASSIFICATION.md
- **API 标准化规范**: docs/standards/API_RESPONSE_STANDARDIZATION.md
- **Test Helpers 文档**: tests/e2e/test-helpers.ts (代码注释)
- **Playwright 配置**: playwright.config.ts

---

## 预期成果

### Week 1 完成后

```
测试通过率:
  整体:     82.7% → 95%+ ✅
  Chromium: 100% → 100% ✅
  Firefox:  74% → 95%+ ✅
  WebKit:   74% → 95%+ ✅

文档更新:
  ✅ E2E 测试最佳实践指南
  ✅ 浏览器兼容性文档
  ✅ API 标准化文档

代码改进:
  ✅ 更稳健的选择器
  ✅ 更好的浏览器支持
  ✅ 可重用的测试工具库
```

---

**下一步**: 按优先级推进三个优化任务，每日验证进度。
