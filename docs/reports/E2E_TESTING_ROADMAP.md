# E2E测试路线图 - PM2 + Playwright全覆盖测试

**创建时间**: 2026-01-08
**测试范围**: 28个主要页面
**测试工具**: PM2 + Playwright + Python

---

## 测试范围分类

### ✅ 已完成测试 (1个页面)
- [x] PortfolioManagement.vue - 投资组合管理（健康度雷达图）

### 📋 待测试页面 (27个页面)

#### MainLayout页面 (16个)
1. Dashboard.vue - 仪表盘
2. Analysis.vue - 数据分析
3. IndustryConceptAnalysis.vue - 行业概念分析
4. Stocks.vue - 股票管理
5. StockDetail.vue - 股票详情
6. TechnicalAnalysis.vue - 技术分析
7. IndicatorLibrary.vue - 指标库
8. TradeManagement.vue - 交易管理
9. TaskManagement.vue - 任务管理
10. Settings.vue - 系统设置
11. OpenStockDemo.vue - OpenStock功能演示
12. PyprofilingDemo.vue - PyProfiling功能演示
13. FreqtradeDemo.vue - Freqtrade功能演示
14. StockAnalysisDemo.vue - Stock-Analysis功能演示
15. TdxpyDemo.vue - pytdx功能演示
16. SmartDataSourceTest.vue - 智能数据源测试

#### MarketLayout页面 (3个)
17. Market.vue - 市场行情
18. TdxMarket.vue - TDX行情
19. RealTimeMonitor.vue - 实时监控

#### DataLayout页面 (5个)
20. FundFlowPanel.vue - 资金流向
21. ETFDataTable.vue - ETF行情
22. ChipRaceTable.vue - 竞价抢筹
23. LongHuBangTable.vue - 龙虎榜
24. WencaiPanelV2.vue - 问财筛选

#### RiskLayout页面 (2个)
25. RiskMonitor.vue - 风险监控
26. AnnouncementMonitor.vue - 公告监控

#### StrategyLayout页面 (2个)
27. StrategyManagement.vue - 策略管理
28. BacktestAnalysis.vue - 回测分析

---

## 测试优先级

### P0 - 核心业务页面 (高优先级)
这些页面是系统核心功能，需要优先测试：

1. Dashboard.vue - 用户入口，仪表盘
2. Market.vue - 市场行情，核心功能
3. Stocks.vue - 股票管理，核心功能
4. StockDetail.vue - 股票详情，核心功能
5. RealTimeMonitor.vue - 实时监控，核心功能
6. RiskMonitor.vue - 风险监控，核心功能

### P1 - 重要功能页面 (中优先级)
7. Analysis.vue - 数据分析
8. TechnicalAnalysis.vue - 技术分析
9. IndustryConceptAnalysis.vue - 行业概念分析
10. StrategyManagement.vue - 策略管理
11. BacktestAnalysis.vue - 回测分析
12. TradeManagement.vue - 交易管理
13. TaskManagement.vue - 任务管理
14. Settings.vue - 系统设置

### P2 - 辅助功能页面 (低优先级)
15-28. Demo页面和市场数据子页面

---

## 测试检查清单

每个页面的测试包括：

### 基础检查 (必做)
- [ ] 页面可访问性 (URL导航成功)
- [ ] 页面标题和元信息
- [ ] 关键元素可见性 (卡片、表格、按钮等)
- [ ] 无JavaScript错误
- [ ] 无网络请求失败 (4xx/5xx)

### 功能检查 (根据页面特性)
- [ ] 表格数据加载
- [ ] 图表渲染
- [ ] 表单交互
- [ ] 按钮响应
- [ ] 弹窗/对话框
- [ ] 分页/排序/筛选

### 用户体验检查
- [ ] 页面加载速度 (< 3秒)
- [ ] 响应式布局 (桌面端)
- [ ] 文字可读性
- [ ] 颜色对比度
- [ ] 交互反馈 (hover, active状态)

---

## PM2配置策略

### 测试服务命名规则
- `playwright-test-{page}` - 单页面测试
- `playwright-test-{layout}` - 布局级别测试
- `playwright-test-all` - 全量回归测试

### 日志文件位置
- 标准输出: `/var/log/pm2/playwright-{name}-out.log`
- 错误输出: `/var/log/pm2/playwright-{name}-error.log`
- 测试报告: `/tmp/{name}_report.json`
- 截图证据: `/tmp/{name}_screenshot_{num}.png`

---

## 执行计划

### Phase 1: P0核心页面测试 (优先)
**时间估计**: 6个页面 × 30分钟 = 3小时

**目标**:
- 确保核心功能可用
- 发现并修复阻塞性问题
- 建立测试脚本模板

### Phase 2: P1重要功能测试
**时间估计**: 8个页面 × 20分钟 = 2.5小时

**目标**:
- 覆盖主要业务流程
- 验证跨页面导航
- 测试数据流转

### Phase 3: P2辅助功能测试
**时间估计**: 13个页面 × 10分钟 = 2小时

**目标**:
- 全覆盖验证
- 收集UX问题
- 完善测试报告

---

## 测试脚本模板

每个测试脚本包含：

```python
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def test_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 1. 导航到页面
            await page.goto('http://localhost:3020/#/page-url')
            await page.wait_for_timeout(2000)

            # 2. 基础检查
            title = await page.title()
            print(f"✅ 页面标题: {title}")

            # 3. 关键元素检查
            element = await page.query_selector('.key-selector')
            if element:
                is_visible = await element.is_visible()
                print(f"✅ 关键元素: {'可见' if is_visible else '不可见'}")

            # 4. 功能测试 (根据页面特性)
            # ...

            # 5. 截图保存
            await page.screenshot(path=f'/tmp/page_screenshot.png')

            # 6. 生成报告
            report = {
                'timestamp': datetime.now().isoformat(),
                'page': 'PageName',
                'status': 'passed',
                'checks': [...]
            }

            with open('/tmp/page_report.json', 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            # 保存错误截图
            await page.screenshot(path=f'/tmp/page_error.png')

        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_page())
```

---

## 问题记录和修复

### 发现问题格式
- **页面**: PageName.vue
- **问题**: 问题描述
- **严重级别**: Critical/High/Medium/Low
- **复现步骤**: 1, 2, 3...
- **预期结果**: 应该如何
- **实际结果**: 实际如何
- **修复方案**: 如何修复
- **状态**: Open/Fixed/Verified

### 问题跟踪
- 所有问题记录到 `/docs/reports/E2E_TEST_ISSUES.md`
- 每个问题包含修复前后对比
- 修复后重新测试验证

---

## 成功标准

### 测试完成标准
- [ ] 所有28个页面至少测试1次
- [ ] P0页面100%通过率
- [ ] P1页面 > 90%通过率
- [ ] P2页面 > 80%通过率
- [ ] 所有Critical/High级别问题已修复

### 质量标准
- [ ] 无JavaScript错误
- [ ] 无网络请求失败
- [ ] 页面加载时间 < 3秒
- [ ] 所有核心功能可用
- [ ] 用户体验流畅

---

## 最终交付物

1. **测试脚本**: 28个Playwright测试脚本
2. **PM2配置**: 完整的测试服务配置
3. **测试报告**: 每个页面的详细测试报告
4. **问题清单**: 发现的所有问题和修复记录
5. **完成报告**: 总结性报告和改进建议

---

**下一步**: 开始Phase 1 - P0核心页面测试
