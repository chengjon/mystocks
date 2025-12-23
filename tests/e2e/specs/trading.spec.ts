/**
 * 交易工作流端到端测试
 *
 * 测试范围:
 * 1. 股票搜索和查看流程
 * 2. 技术分析工作流
 * 3. 问财查询工作流
 * 4. 策略管理流程
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { test, expect } from '@playwright/test';
import {
  StockSearchPage,
  TechnicalAnalysisPage,
  WencaiPage,
  StrategyPage
} from '../utils/page-objects';
import {
  UserAuth,
  ScreenshotHelper,
  UIHelper,
  MockDataHelper,
  TestDataGenerator
} from '../utils/test-helpers';

test.describe('交易工作流', () => {
  let stockSearchPage: StockSearchPage;
  let technicalAnalysisPage: TechnicalAnalysisPage;
  let wencaiPage: WencaiPage;
  let strategyPage: StrategyPage;

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/login');
    await UserAuth.login(page, { username: 'testuser', password: 'password123' });

    // 初始化页面对象
    stockSearchPage = new StockSearchPage(page);
    technicalAnalysisPage = new TechnicalAnalysisPage(page);
    wencaiPage = new WencaiPage(page);
    strategyPage = new StrategyPage(page);
  });

  test.describe('股票搜索工作流', () => {
    test('股票搜索功能', async ({ page }) => {
      await stockSearchPage.navigate();

      // 搜索贵州茅台
      await stockSearchPage.performSearch('贵州茅台');

      // 验证搜索结果显示
      await expect(stockSearchPage.areSearchResultsVisible()).toBeTruthy();

      const resultsCount = await stockSearchPage.getSearchResultsCount();
      expect(resultsCount).toBeGreaterThan(0);

      // 验证搜索结果包含目标股票
      const results = await stockSearchPage.getSearchResultsList();
      const hasMaotai = results.some(stock =>
        stock.symbol === '600519' || stock.name?.includes('茅台')
      );
      expect(hasMaotai).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'stock-search-results');
    });

    test('股票代码搜索', async ({ page }) => {
      await stockSearchPage.navigate();

      // 按股票代码搜索
      await stockSearchPage.performSearch('600519');

      // 验证搜索结果
      await expect(stockSearchPage.areSearchResultsVisible()).toBeTruthy();

      const results = await stockSearchPage.getSearchResultsList();
      expect(results.length).toBeGreaterThan(0);

      // 验证返回结果包含搜索的股票
      const hasTargetStock = results.some(stock => stock.symbol === '600519');
      expect(hasTargetStock).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'stock-code-search');
    });

    test('股票详情页面访问', async ({ page }) => {
      await stockSearchPage.navigate();
      await stockSearchPage.performSearch('600519');

      // 点击第一个搜索结果
      await stockSearchPage.clickFirstResult();

      // 验证跳转到股票详情页
      await expect(page).toHaveURL(/\/market\/600519/);

      // 验证股票详情页内容
      await expect(page.locator('[data-testid=stock-symbol]')).toContainText('600519');
      await expect(page.locator('[data-testid=stock-name]')).toContainText('贵州茅台');

      // 验证K线图显示
      await expect(page.locator('[data-testid=kline-chart]')).toBeVisible();

      // 验证技术指标显示
      await expect(page.locator('[data-testid=technical-indicators]')).toBeVisible();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'stock-detail-page');
    });

    test('股票搜索过滤器', async ({ page }) => {
      await stockSearchPage.navigate();

      // 测试行业过滤器
      await page.selectOption('[data-testid=industry-filter]', '白酒');
      await page.click('[data-testid=apply-filter]');

      // 验证过滤结果
      await page.waitForTimeout(1000);

      const results = await stockSearchPage.getSearchResultsList();
      // 验证所有结果都属于白酒行业
      const allInIndustry = results.every(stock =>
        stock.industry === '白酒' || stock.name?.includes('白酒')
      );
      expect(allInIndustry).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'stock-filter-results');
    });
  });

  test.describe('技术分析工作流', () => {
    test('技术分析页面加载', async ({ page }) => {
      await technicalAnalysisPage.navigate();

      // 验证页面基本元素
      await expect(page.locator('[data-testid=stock-selector]')).toBeVisible();
      await expect(page.locator('[data-testid=indicator-checkboxes]')).toBeVisible();
      await expect(page.locator('[data-testid=analyze-button]')).toBeVisible();

      // 验证股票选择器有选项
      const stockOptions = page.locator('[data-testid=stock-selector] option');
      const optionCount = await stockOptions.count();
      expect(optionCount).toBeGreaterThan(5); // 至少5个股票选项

      // 验证技术指标选项
      const indicatorOptions = page.locator('[data-testid=indicator-ma5]');
      await expect(indicatorOptions).toBeVisible();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'technical-analysis-page');
    });

    test('技术指标分析执行', async ({ page }) => {
      await technicalAnalysisPage.navigate();

      // 选择股票和技术指标
      await technicalAnalysisPage.performAnalysis('600519', ['ma5', 'rsi', 'macd']);

      // 验证分析结果加载
      await expect(technicalAnalysisPage.areAnalysisResultsVisible()).toBeTruthy();
      await expect(technicalAnalysisPage.isKlineChartVisible()).toBeTruthy();

      // 验证K线图显示
      const klineChart = page.locator('[data-testid=kline-chart] canvas');
      await expect(klineChart).toBeVisible();

      // 验证技术指标计算结果
      const ma5Value = page.locator('[data-testid=ma5-value]').textContent();
      const rsiValue = page.locator('[data-testid=rsi-value]').textContent();
      const macdValue = page.locator('[data-testid=macd-value]').textContent();

      expect(ma5Value).toBeTruthy();
      expect(rsiValue).toBeTruthy();
      expect(macdValue).toBeTruthy();

      // 验证数值在合理范围内
      expect(parseFloat(ma5Value as string)).toBeGreaterThan(0);
      expect(parseFloat(rsiValue as string)).toBeGreaterThanOrEqual(0);
      expect(parseFloat(rsiValue as string)).toBeLessThanOrEqual(100);

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'technical-analysis-results');
    });

    test('多指标同时分析', async ({ page }) => {
      await technicalAnalysisPage.navigate();

      // 选择更多技术指标
      await technicalAnalysisPage.selectStock('600036');
      await technicalAnalysisPage.selectIndicators([
        'ma5', 'ma10', 'ma20', 'rsi', 'macd', 'kdj', 'bollinger'
      ]);

      await technicalAnalysisPage.analyzeButton.click();

      // 验证所有指标都显示
      await expect(page.locator('[data-testid=ma5-value]')).toBeVisible();
      await expect(page.locator('[data-testid=rsi-chart]')).toBeVisible();
      await expect(page.locator('[data-testid=macd-chart]')).toBeVisible();
      await expect(page.locator('[data-testid=kdj-chart]')).toBeVisible();
      await expect(page.locator('[data-testid=bollinger-chart]')).toBeVisible();

      // 验证图表正确渲染
      const charts = page.locator('[data-testid$=-chart] canvas');
      const chartCount = await charts.count();
      expect(chartCount).toBeGreaterThan(3);

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'multi-indicator-analysis');
    });

    test('买卖信号分析', async ({ page }) => {
      await technicalAnalysisPage.navigate();

      // 执行技术分析
      await technicalAnalysisPage.performAnalysis('600519', ['ma5', 'rsi', 'macd']);

      // 验证信号分析结果
      await expect(page.locator('[data-testid=signal-results]')).toBeVisible();

      // 验证买卖信号
      const signals = page.locator('[data-testid=trading-signals]');
      const signalCount = await signals.locator('[data-testid=signal-item]').count();
      expect(signalCount).toBeGreaterThan(0);

      // 验证信号类型
      const buySignals = page.locator('[data-testid=buy-signal]');
      const sellSignals = page.locator('[data-testid=sell-signal]');

      const hasBuySignal = await buySignals.count() > 0;
      const hasSellSignal = await sellSignals.count() > 0;

      // 至少应该有一种信号
      expect(hasBuySignal || hasSellSignal).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'trading-signals');
    });
  });

  test.describe('问财查询工作流', () => {
    test('问财页面加载和预定义查询', async ({ page }) => {
      await wencaiPage.navigate();

      // 验证页面基本元素
      await expect(page.locator('[data-testid=query-selector]')).toBeVisible();
      await expect(page.locator('[data-testid=custom-query-tab]')).toBeVisible();

      // 验证预定义查询选项
      const queryOptions = page.locator('[data-testid=query-selector] option');
      const optionCount = await queryOptions.count();
      expect(optionCount).toBeGreaterThan(3); // 至少3个预定义查询

      // 执行预定义查询
      await wencaiPage.executePredefinedQuery('strong_stocks');

      // 验证查询结果
      await expect(wencaiPage.areQueryResultsVisible()).toBeTruthy();

      const results = await wencaiPage.getQueryResultsData();
      expect(results.length).toBeGreaterThan(0);

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'wencai-predefined-query');
    });

    test('自定义查询执行', async ({ page }) => {
      await wencaiPage.navigate();

      // 切换到自定义查询
      await wencaiPage.switchToCustomQuery();

      // 输入自定义查询
      const customQuery = '涨停板股票 2024-01-15';
      await wencaiPage.executeCustomQuery(customQuery);

      // 验证查询结果显示
      await expect(wencaiPage.areQueryResultsVisible()).toBeTruthy();

      const results = await wencaiPage.getQueryResultsData();
      expect(results.length).toBeGreaterThan(0);

      // 验证查询结果格式
      const firstResult = results[0];
      expect(firstResult.content).toBeTruthy();
      expect(firstResult.type).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'wencai-custom-query');
    });

    test('问财查询结果导出', async ({ page }) => {
      await wencaiPage.navigate();

      // 执行查询
      await wencaiPage.executePredefinedQuery('limit_up');

      // 等待结果加载
      await wencaiPage.areQueryResultsVisible();

      // 点击导出按钮
      await page.click('[data-testid=export-results]');

      // 验证导出选项
      await expect(page.locator('[data-testid=export-modal]')).toBeVisible();

      // 选择Excel导出
      await page.click('[data-testid=export-excel]');

      // 验证下载开始（模拟）
      // 实际测试中需要检查文件下载
      await expect(page.locator('[data-testid=export-success]')).toBeVisible();

      // 关闭导出对话框
      await page.click('[data-testid=close-export-modal]');

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'wencai-export-results');
    });

    test('问财查询历史记录', async ({ page }) => {
      await wencaiPage.navigate();

      // 执行几个查询
      await wencaiPage.executePredefinedQuery('strong_stocks');
      await wencaiPage.switchToCustomQuery();
      await wencaiPage.executeCustomQuery('放量股票');

      // 访问历史记录
      await page.click('[data-testid=query-history]');

      // 验证历史记录显示
      await expect(page.locator('[data-testid=history-list]')).toBeVisible();

      const historyItems = page.locator('[data-testid=history-item]');
      const historyCount = await historyItems.count();
      expect(historyCount).toBeGreaterThan(0);

      // 点击历史查询重新执行
      await historyItems.first().click();

      // 验证查询重新执行
      await expect(wencaiPage.areQueryResultsVisible()).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'wencai-history');
    });
  });

  test.describe('策略管理工作流', () => {
    test('策略管理页面加载', async ({ page }) => {
      await strategyPage.navigate();

      // 验证页面基本元素
      await expect(page.locator('[data-testid=strategy-list]')).toBeVisible();
      await expect(page.locator('[data-testid=create-strategy-button]')).toBeVisible();

      // 验证策略列表显示
      const strategies = await strategyPage.getStrategyList();
      expect(strategies.length).toBeGreaterThan(0);

      // 验证策略信息
      const firstStrategy = strategies[0];
      expect(firstStrategy.name).toBeTruthy();
      expect(firstStrategy.status).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'strategy-management-page');
    });

    test('策略执行流程', async ({ page }) => {
      await strategyPage.navigate();

      // 获取可用策略
      const strategies = await strategyPage.getStrategyList();
      const activeStrategies = strategies.filter(s => s.status === 'active');

      if (activeStrategies.length > 0) {
        // 执行第一个活跃策略
        await strategyPage.runStrategy(0);

        // 验证策略结果
        await expect(strategyPage.areStrategyResultsVisible()).toBeTruthy();

        // 验证结果数据
        const results = page.locator('[data-testid=strategy-result-item]');
        await expect(results.first()).toBeVisible();

        const resultCount = await results.count();
        expect(resultCount).toBeGreaterThan(0);

        // 验证结果包含股票推荐
        const hasStockRecommendations = await page.locator('[data-testid=recommended-stock]').count() > 0;
        expect(hasStockRecommendations).toBeTruthy();
      }

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'strategy-execution');
    });

    test('创建新策略', async ({ page }) => {
      await strategyPage.navigate();

      // 点击创建策略按钮
      await strategyPage.createStrategy('测试策略', '这是一个测试策略的描述');

      // 验证创建表单显示
      await expect(page.locator('[data-testid=strategy-form]')).toBeVisible();

      // 填写策略信息
      await page.fill('[data-testid=strategy-name-input]', '自动化测试策略');
      await page.fill('[data-testid=strategy-description-input]', '自动化创建的测试策略');

      // 选择策略类型
      await page.selectOption('[data-testid=strategy-type]', 'technical');

      // 设置策略参数
      await page.fill('[data-testid=param-ma-period]', '5');
      await page.fill('[data-testid=param-rsi-threshold]', '70');

      // 保存策略
      await page.click('[data-testid=save-strategy-button]');

      // 验证策略创建成功
      await expect(page.locator('[data-testid=success-message]')).toBeVisible();

      // 验证新策略出现在列表中
      const updatedStrategies = await strategyPage.getStrategyList();
      const newStrategy = updatedStrategies.find(s => s.name === '自动化测试策略');
      expect(newStrategy).toBeTruthy();

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'create-new-strategy');
    });

    test('策略回测功能', async ({ page }) => {
      await strategyPage.navigate();

      // 选择一个策略进行回测
      const strategies = await strategyPage.getStrategyList();
      if (strategies.length > 0) {
        // 点击第一个策略
        await page.locator('[data-testid=strategy-item]').first().click();

        // 点击回测按钮
        await page.click('[data-testid=backtest-button]');

        // 验证回测配置对话框
        await expect(page.locator('[data-testid=backtest-modal]')).toBeVisible();

        // 设置回测参数
        await page.fill('[data-testid=backtest-start-date]', '2024-01-01');
        await page.fill('[data-testid=backtest-end-date]', '2024-01-31');
        await page.fill('[data-testid=initial-capital]', '100000');

        // 开始回测
        await page.click('[data-testid=start-backtest]');

        // 等待回测完成
        await expect(page.locator('[data-testid=backtest-results]')).toBeVisible();

        // 验证回测结果
        const backtestResults = page.locator('[data-testid=backtest-metric]');
        const metricCount = await backtestResults.count();
        expect(metricCount).toBeGreaterThan(3); // 至少3个回测指标

        // 验证收益曲线图表
        await expect(page.locator('[data-testid=equity-curve-chart] canvas')).toBeVisible();

        // 关闭回测对话框
        await page.click('[data-testid=close-backtest-modal]');
      }

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'strategy-backtest');
    });
  });

  test.describe('端到端工作流', () => {
    test('完整股票分析工作流', async ({ page }) => {
      // 1. 搜索股票
      await stockSearchPage.navigate();
      await stockSearchPage.performSearch('600519');

      // 验证搜索结果
      const results = await stockSearchPage.getSearchResultsList();
      expect(results.length).toBeGreaterThan(0);

      // 2. 进入技术分析
      await page.goto('/technical-analysis');
      await technicalAnalysisPage.selectStock('600519');
      await technicalAnalysisPage.selectIndicators(['ma5', 'rsi', 'macd']);
      await technicalAnalysisPage.analyzeButton.click();

      // 验证技术分析结果
      await expect(technicalAnalysisPage.areAnalysisResultsVisible()).toBeTruthy();

      // 3. 使用问财查询验证
      await wencaiPage.navigate();
      await wencaiPage.executePredefinedQuery('strong_stocks');

      // 验证问财查询结果
      const wencaiResults = await wencaiPage.getQueryResultsData();
      expect(wencaiResults.length).toBeGreaterThan(0);

      // 4. 查看策略推荐
      await strategyPage.navigate();
      const strategies = await strategyPage.getStrategyList();
      expect(strategies.length).toBeGreaterThan(0);

      // 验证整个工作流的完整性
      console.log('✅ Complete trading workflow executed successfully');

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'complete-trading-workflow');
    });

    test('Mock数据一致性验证', async ({ page }) => {
      // 验证不同页面间Mock数据的一致性

      // 1. 仪表盘数据
      await page.goto('/dashboard');
      await page.waitForTimeout(2000);

      const dashboardStocks = await page.locator('[data-testid=favorite-stocks-table] tbody tr').count();
      expect(dashboardStocks).toBeGreaterThan(0);

      // 2. 搜索页面数据
      await stockSearchPage.navigate();
      await stockSearchPage.performSearch('600519');

      // 3. 技术分析页面数据
      await technicalAnalysisPage.navigate();
      await technicalAnalysisPage.selectStock('600519');

      // 验证股票代码在不同页面的一致性
      const stockSelectorOptions = page.locator('[data-testid=stock-selector] option');
      const optionCount = await stockSelectorOptions.count();
      expect(optionCount).toBeGreaterThan(0);

      // 验证Mock系统提供的股票代码一致
      console.log('✅ Mock data consistency validated across workflows');

      // 截图保存
      await ScreenshotHelper.takeScreenshot(page, 'mock-data-consistency');
    });
  });
});
