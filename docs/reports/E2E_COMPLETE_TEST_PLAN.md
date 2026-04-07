# MyStocks项目完整E2E测试计划

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**创建时间**: 2026-01-08 09:20
**测试工程师**: Claude Code (自动化测试工程师)
**测试框架**: PM2 + Playwright + Python
**项目范围**: 28个Vue页面全覆盖

---

## 📋 目录

1. [项目概述](#项目概述)
2. [页面清单和分类](#页面清单和分类)
3. [测试策略](#测试策略)
4. [测试框架设计](#测试框架设计)
5. [分阶段执行计划](#分阶段执行计划)
6. [问题修复流程](#问题修复流程)
7. [质量标准](#质量标准)
8. [交付物清单](#交付物清单)

---

## 项目概述

### 目标

- ✅ **测试覆盖率**: 100% (28/28页面)
- ✅ **缺陷修复率**: 100% (所有Critical/High级别问题)
- ✅ **测试通过率目标**: >95%
- ✅ **零回归问题**: 修复后不引入新问题

### 测试原则

1. **全面覆盖**: 不遗漏任何页面
2. **可维护性**: 模块化、可复用的测试代码
3. **可扩展性**: 易于添加新测试
4. **自动化优先**: 尽量自动化，减少手工操作
5. **快速反馈**: 快速执行，快速发现问题

---

## 页面清单和分类

### ✅ Phase 1: P0核心页面 (已完成 - 6个)

| # | 页面名称 | 路由 | 测试状态 | 通过率 | 问题数 |
|---|---------|------|---------|--------|--------|
| 1 | Dashboard | `/#/dashboard` | ✅ 完成 | 85.7% | 1 |
| 2 | Market | `/#/market/list` | ✅ 完成 | 87.5% | 1 |
| 3 | Stocks | `/#/stocks` | ✅ 完成 | 100% | 0 |
| 4 | StockDetail | `/#/stock-detail/:symbol` | ✅ 完成 | 100% | 0 |
| 5 | RealTimeMonitor | `/#/market/realtime` | ✅ 完成 | 100% | 0 |
| 6 | RiskMonitor | `/#/risk-monitor/overview` | ✅ 完成 | 100% | 0 |

**小计**: 6个页面，91.3%通过率，2个低优先级问题

---

### 🔄 Phase 2: P1重要功能页面 (进行中 - 8个)

| # | 页面名称 | 路由 | 测试状态 | 预计问题 |
|---|---------|------|---------|----------|
| 7 | Analysis | `/#/analysis` | ⏳ 待测 | API集成、图表渲染 |
| 8 | IndustryConceptAnalysis | `/#/analysis/industry-concept` | ⏳ 待测 | 数据加载、交互 |
| 9 | TechnicalAnalysis | `/#/technical` | ⏳ 待测 | 指标计算、图表 |
| 10 | IndicatorLibrary | `/#/indicators` | ⏳ 待测 | 指标列表、搜索 |
| 11 | StrategyManagement | `/#/strategy-hub/management` | ⏳ 待测 | CRUD操作、验证 |
| 12 | BacktestAnalysis | `/#/strategy-hub/backtest` | ⏳ 待测 | 回测执行、结果展示 |
| 13 | TradeManagement | `/#/trade` | ⏳ 待测 | 交易表单、验证 |
| 14 | TaskManagement | `/#/tasks` | ⏳ 待测 | 任务列表、状态 |
| 15 | Settings | `/#/settings` | ⏳ 待测 | 配置保存、验证 |

**小计**: 9个页面，预计15-20个潜在问题

---

### ⏳ Phase 3: P2辅助功能页面 (待开始 - 14个)

#### MarketLayout子页面 (3个)

| # | 页面名称 | 路由 | 测试状态 |
|---|---------|------|---------|
| 16 | TdxMarket | `/#/market/tdx-market` | ⏳ 待测 |

#### DataLayout子页面 (5个)

| # | 页面名称 | 路由 | 测试状态 |
|---|---------|------|---------|
| 17 | FundFlowPanel | `/#/market-data/fund-flow` | ⏳ 待测 |
| 18 | ETFDataTable | `/#/market-data/etf` | ⏳ 待测 |
| 19 | ChipRaceTable | `/#/market-data/chip-race` | ⏳ 待测 |
| 20 | LongHuBangTable | `/#/market-data/lhb` | ⏳ 待测 |
| 21 | WencaiPanelV2 | `/#/market-data/wencai` | ⏳ 待测 |

#### RiskLayout子页面 (1个)

| # | 页面名称 | 路由 | 测试状态 |
|---|---------|------|---------|
| 22 | AnnouncementMonitor | `/#/risk-monitor/announcement` | ⏳ 待测 |

#### Demo页面 (8个)

| # | 页面名称 | 路由 | 测试状态 |
|---|---------|------|---------|
| 23 | OpenStockDemo | `/#/openstock-demo` | ⏳ 待测 |
| 24 | PyprofilingDemo | `/#/pyprofiling-demo` | ⏳ 待测 |
| 25 | FreqtradeDemo | `/#/freqtrade-demo` | ⏳ 待测 |
| 26 | StockAnalysisDemo | `/#/stock-analysis-demo` | ⏳ 待测 |
| 27 | TdxpyDemo | `/#/tdxpy-demo` | ⏳ 待测 |
| 28 | SmartDataSourceTest | `/#/smart-data-test` | ⏳ 待测 |

**小计**: 14个页面，预计10-15个潜在问题

---

## 测试策略

### 测试优先级矩阵

```
高影响 × 高频率 = P0 (核心页面) ✅ 已完成
高影响 × 低频率 = P1 (重要功能) 🔄 进行中
低影响 × 高频率 = P2 (辅助功能) ⏳ 待开始
低影响 × 低频率 = P3 (可选功能)
```

### 测试类型

#### 1. 冒烟测试 (Smoke Test)
- **目标**: 快速验证页面基本可访问
- **时间**: 每个页面< 10秒
- **检查项**:
  - 页面可加载
  - 无JavaScript错误
  - 关键元素可见

#### 2. 功能测试 (Functional Test)
- **目标**: 验证页面核心功能
- **时间**: 每个页面< 30秒
- **检查项**:
  - 表格数据加载
  - 图表渲染
  - 表单验证
  - 交互响应

#### 3. 集成测试 (Integration Test)
- **目标**: 验证跨页面流程
- **时间**: 每个流程< 60秒
- **检查项**:
  - 页面导航
  - 数据流转
  - 状态同步

#### 4. 回归测试 (Regression Test)
- **目标**: 确保修复不引入新问题
- **时间**: 每次修复后
- **检查项**:
  - 之前通过的测试
  - 相关功能测试

---

## 测试框架设计

### 架构设计

```
┌─────────────────────────────────────────────────────┐
│               PM2 Process Manager                   │
│          (统一管理所有测试服务)                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │       Test Framework (tests/base.py)         │ │
│  │  - BaseTest Class                            │ │
│  │  - Common Utilities                          │ │
│  │  - Assertion Helpers                         │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  P0 Tests│  │  P1 Tests│  │  P2 Tests│         │
│  │ (6 pages)│  │ (9 pages)│  │ (14pages)│         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │     Playwright Async API                    │ │
│  │  - Browser Automation                       │ │
│  │  - Element Selection                         │ │
│  │  - Screenshot & Video                        │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 模块化设计

#### 1. 基础测试类 (tests/base.py)

```python
class BaseTest:
    """所有测试的基类"""

    async def setup(self):
        """测试前置条件"""
        pass

    async def teardown(self):
        """测试后置清理"""
        pass

    async def navigate_to_page(self, url):
        """导航到页面"""
        pass

    async def check_no_console_errors(self):
        """检查无控制台错误"""
        pass

    async def take_screenshot(self, name):
        """保存截图"""
        pass

    async def generate_report(self):
        """生成测试报告"""
        pass
```

#### 2. 测试工具库 (tests/utils.py)

```python
# 元素选择器工具
def select_element(page, selector)
def wait_for_element(page, selector, timeout)

# 断言工具
def assert_element_visible(element)
def assert_text_content(element, expected_text)
def assert_no_console_errors(page)

# 数据工具
def load_test_data(page_name)
def compare_with_baseline(actual, expected)
```

#### 3. 页面对象模式 (tests/pages/)

```python
class DashboardPage:
    """Dashboard页面对象"""

    def __init__(self, page):
        self.page = page

    async def get_stat_cards(self):
        """获取统计卡片"""
        pass

    async def click_refresh_button(self):
        """点击刷新按钮"""
        pass

    async def get_market_heat_chart(self):
        """获取市场热度图表"""
        pass
```

---

## 分阶段执行计划

### Phase 2: P1重要功能页面 (当前阶段)

**时间估计**: 2-3小时
**页面数量**: 9个
**测试脚本**: 9个
**预计问题**: 15-20个

**执行步骤**:
1. ✅ 创建基础测试框架 (`tests/base.py`, `tests/utils.py`)
2. ✅ 创建P1测试脚本
3. ✅ 配置PM2服务 (`ecosystem.playwright.p1.config.js`)
4. ✅ 并发执行测试
5. ✅ 收集测试结果
6. ✅ 分析和修复问题

### Phase 3: P2辅助功能页面

**时间估计**: 2小时
**页面数量**: 14个
**测试脚本**: 14个
**预计问题**: 10-15个

**执行步骤**:
1. ✅ 创建P2测试脚本
2. ✅ 配置PM2服务
3. ✅ 批量执行测试
4. ✅ 收集测试结果
5. ✅ 修复关键问题

### Phase 4: 问题修复和回归测试

**时间估计**: 1-2小时
**预计问题**: 25-35个

**修复优先级**:
1. **Critical**: 系统崩溃、数据丢失、安全漏洞
2. **High**: 核心功能不可用
3. **Medium**: 功能部分可用、用户体验差
4. **Low**: UI小问题、文案错误

---

## 问题修复流程

### 标准修复流程

```
1. 发现问题
   ↓
2. 记录问题 (问题日志、截图、复现步骤)
   ↓
3. 分析根本原因
   ↓
4. 设计修复方案
   ↓
5. 实施修复
   ↓
6. 验证修复 (单元测试 + E2E测试)
   ↓
7. 回归测试 (确保无新问题)
   ↓
8. 更新文档
```

### 问题跟踪模板

```json
{
  "id": "BUG-001",
  "title": "问题标题",
  "severity": "High",
  "page": "页面名称",
  "description": "详细描述",
  "steps_to_reproduce": ["步骤1", "步骤2"],
  "expected_result": "预期结果",
  "actual_result": "实际结果",
  "screenshots": ["截图路径"],
  "logs": ["日志路径"],
  "root_cause": "根本原因",
  "fix_solution": "修复方案",
  "status": "Open/Fixed/Verified",
  "fixed_at": "修复时间",
  "verified_at": "验证时间"
}
```

---

## 质量标准

### 测试质量标准

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| 测试覆盖率 | 100% | 21.4% (6/28) | 🔄 进行中 |
| 测试通过率 | >95% | 91.3% | ⚠️ 略低 |
| Critical问题数 | 0 | 0 | ✅ 达标 |
| High问题数 | 0 | 0 | ✅ 达标 |
| 测试执行时间 | <30分钟 | ~5分钟 | ✅ 达标 |

### 代码质量标准

| 指标 | 要求 |
|------|------|
| 代码规范 | 遵循PEP 8和项目编码规范 |
| 注释覆盖率 | 核心逻辑100%注释 |
| 测试可读性 | 任何开发者可理解测试意图 |
| 可维护性 | 易于修改和扩展 |

---

## 交付物清单

### 测试脚本

#### Phase 1 (已完成)
- [x] `/tmp/test_dashboard_playwright.py`
- [x] `/tmp/test_market_playwright.py`
- [x] `/tmp/test_stocks_playwright.py`
- [x] `/tmp/test_stockdetail_playwright.py`
- [x] `/tmp/test_realtimemonitor_playwright.py`
- [x] `/tmp/test_riskmonitor_playwright.py`

#### Phase 2 (待创建)
- [ ] `/tmp/test_analysis_playwright.py`
- [ ] `/tmp/test_industryconcept_playwright.py`
- [ ] `/tmp/test_technical_playwright.py`
- [ ] `/tmp/test_indicatorlibrary_playwright.py`
- [ ] `/tmp/test_strategy_playwright.py`
- [ ] `/tmp/test_backtest_playwright.py`
- [ ] `/tmp/test_trade_playwright.py`
- [ ] `/tmp/test_tasks_playwright.py`
- [ ] `/tmp/test_settings_playwright.py`

#### Phase 3 (待创建)
- [ ] 14个P2页面测试脚本

### 测试框架

- [ ] `/opt/claude/mystocks_spec/tests/base.py` - 基础测试类
- [ ] `/opt/claude/mystocks_spec/tests/utils.py` - 测试工具库
- [ ] `/opt/claude/mystocks_spec/tests/pages/` - 页面对象

### PM2配置

- [x] `ecosystem.playwright.p0.config.js`
- [ ] `ecosystem.playwright.p1.config.js`
- [ ] `ecosystem.playwright.p2.config.js`
- [ ] `ecosystem.playwright.all.config.js` - 全量测试

### 测试报告

- [x] `/tmp/p0_test_summary.json`
- [x] `/docs/reports/E2E_PHASE1_COMPLETION_REPORT.md`
- [ ] `/tmp/p1_test_summary.json`
- [ ] `/docs/reports/E2E_PHASE2_COMPLETION_REPORT.md`
- [ ] `/tmp/p2_test_summary.json`
- [ ] `/docs/reports/E2E_PHASE3_COMPLETION_REPORT.md`
- [ ] `/docs/reports/E2E_FINAL_REPORT.md` - 最终报告

### 问题跟踪

- [ ] `/docs/reports/E2E_ISSUES_TRACKER.md` - 问题跟踪表
- [ ] `/docs/reports/E2E_FIX_LOG.md` - 修复日志

---

## 时间表

| 阶段 | 页面数 | 预计时间 | 开始时间 | 完成时间 |
|------|--------|----------|----------|----------|
| Phase 1 | 6 | 2小时 | 09:10 | 09:14 |
| Phase 2 | 9 | 2-3小时 | 09:20 | ~12:00 |
| Phase 3 | 14 | 2小时 | ~12:00 | ~14:00 |
| Phase 4 | 修复 | 1-2小时 | ~14:00 | ~16:00 |

**总计**: 28个页面，预计7-9小时完成

---

## 风险和挑战

### 技术风险

1. **测试环境不稳定**
   - 缓解: 使用PM2管理，自动重启失败测试

2. **数据加载时间长**
   - 缓解: 实现智能等待机制

3. **动态内容难以测试**
   - 缓解: 使用Mock数据或固定测试数据

### 资源风险

1. **浏览器资源占用**
   - 缓解: 串行执行或限制并发数

2. **测试执行时间长**
   - 缓解: 优化测试脚本，并行执行

---

## 总结

本测试计划旨在系统性地完成MyStocks项目所有28个页面的E2E测试覆盖，确保项目质量和稳定性。通过模块化测试框架、PM2统一管理和分阶段执行策略，我们将高效地发现并修复所有问题，最终交付一个高质量的量化交易系统。

**下一步**: 立即开始Phase 2的测试工作！

---

**计划创建时间**: 2026-01-08 09:20
**最后更新时间**: 2026-01-08 09:20
**计划状态**: ✅ 已批准，执行中
