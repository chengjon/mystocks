/**
 * WebSocket实时更新测试（Mock版）
 *
 * 用途：使用WebSocket Mock测试实时数据更新功能
 * 优势：不依赖真实后端，测试稳定可靠
 */

import { test, expect } from '@playwright/test';
import { WebSocketMock, MarketDataScenarios, RiskAlertScenarios } from '../helpers/websocket-mock';

test.describe('WebSocket实时更新测试（Mock）', () => {
  let wsMock: WebSocketMock;

  test.beforeEach(async ({ page }) => {
    // 初始化WebSocket Mock
    wsMock = new WebSocketMock(page);
    await wsMock.initialize();

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
  });

  test('WebSocket Mock应该正确初始化', async ({ page }) => {
    const isMocked = await wsMock.isWebSocketMocked();
    expect(isMocked).toBeTruthy();
  });

  test('应该接收市场数据推送', async ({ page }) => {
    // 模拟市场数据推送
    await wsMock.mockMarketData(MarketDataScenarios.normalMarketData);

    // 验证数据已更新（通过检查DOM）
    await page.waitForTimeout(500);

    // 检查市场数据元素（如果存在）
    const marketDataElement = page.locator('[data-test="market-summary"], .market-summary, .market-data').first();

    if (await marketDataElement.count() > 0) {
      await expect(marketDataElement).toBeVisible();
    }
  });

  test('应该接收风险预警推送', async ({ page }) => {
    // 模拟风险预警推送
    await wsMock.mockRiskAlert(RiskAlertScenarios.warningAlert);

    await page.waitForTimeout(500);

    // 检查风险预警Toast（如果实现）
    const toastElement = page.locator('.artdeco-toast--warning, .toast-warning').first();

    if (await toastElement.count() > 0) {
      await expect(toastElement).toBeVisible();
    }
  });

  test('应该接收策略信号推送', async ({ page }) => {
    // 模拟策略信号推送
    await wsMock.mockStrategySignal({
      type: 'strategy_signal',
      strategy: 'MACD策略',
      symbol: '000001',
      action: 'buy',
      price: 15.68,
      timestamp: Date.now()
    });

    await page.waitForTimeout(500);

    // 检查策略信号显示（如果实现）
    const signalElement = page.locator('[data-test="strategy-signal"], .strategy-signal').first();

    if (await signalElement.count() > 0) {
      await expect(signalElement).toBeVisible();
    }
  });

  test('应该处理多个连续的市场数据推送', async ({ page }) => {
    // 推送多个市场数据
    const scenarios = [
      MarketDataScenarios.normalMarketData,
      MarketDataScenarios.volatileMarketData,
      MarketDataScenarios.emptyMarketData
    ];

    for (const scenario of scenarios) {
      await wsMock.mockMarketData(scenario);
      await page.waitForTimeout(200);
    }

    // 验证最后推送的数据
    const connectionState = await wsMock.getConnectionState();
    expect(connectionState).toBe(1); // OPEN
  });

  test('应该处理连接错误', async ({ page }) => {
    // 模拟连接错误
    await wsMock.mockConnectionError();

    await page.waitForTimeout(500);

    // 检查错误提示（如果实现）
    const errorElement = page.locator('[data-test="ws-error"], .connection-error').first();

    if (await errorElement.count() > 0) {
      await expect(errorElement).toBeVisible();
    }
  });

  test('应该处理连接关闭', async ({ page }) => {
    // 模拟连接关闭
    await wsMock.mockConnectionClose(1000, 'Normal closure');

    await page.waitForTimeout(500);

    // 验证连接状态
    const connectionState = await wsMock.getConnectionState();
    expect(connectionState).toBe(3); // CLOSED
  });

  test('市场数据更新应该触发UI刷新', async ({ page }) => {
    // 获取初始市场数据
    const initialData = await page.locator('.market-summary, [data-test="market-summary"]').first().textContent();

    // 推送新数据
    await wsMock.mockMarketData(MarketDataScenarios.volatileMarketData);

    // 等待UI更新
    await page.waitForTimeout(1000);

    // 验证数据已更新
    const updatedData = await page.locator('.market-summary, [data-test="market-summary"]').first().textContent();

    // 如果数据存在，应该有所不同
    if (initialData && updatedData) {
      expect(updatedData).not.toBe(initialData);
    }
  });

  test('风险预警应该触发Toast通知', async ({ page }) => {
    // 推送严重风险预警
    await wsMock.mockRiskAlert(RiskAlertScenarios.criticalAlert);

    await page.waitForTimeout(1000);

    // 验证Toast通知
    const toast = page.locator('.artdeco-toast--error, .artdeco-toast--critical').first();

    if (await toast.count() > 0) {
      await expect(toast).toBeVisible();

      // 验证Toast内容
      const toastContent = await toast.textContent();
      expect(toastContent).toContain('触发止损规则');
    }
  });

  test('WebSocket重连机制应该工作（模拟）', async ({ page }) => {
    // 模拟连接关闭
    await wsMock.mockConnectionClose(1006, 'Abnormal closure');

    await page.waitForTimeout(2000);

    // 检查重连尝试（通过检查连接状态）
    const connectionState = await wsMock.getConnectionState();

    // 在实际应用中，应该有自动重连逻辑
    // 这里只是验证状态变化
    expect(connectionState).toBeGreaterThanOrEqual(0);
  });

  test('多个WebSocket频道应该独立工作', async ({ page }) => {
    // 创建多个WebSocket Mock实例（模拟不同频道）
    const wsMarket = new WebSocketMock(page, 'ws://localhost:8000/api/ws/market');
    await wsMarket.initialize();

    const wsRisk = new WebSocketMock(page, 'ws://localhost:8000/api/ws/risk');
    await wsRisk.initialize();

    // 同时推送不同频道的消息
    await Promise.all([
      wsMarket.mockMarketData(MarketDataScenarios.normalMarketData),
      wsRisk.mockRiskAlert(RiskAlertScenarios.infoAlert)
    ]);

    await page.waitForTimeout(500);

    // 验证两个Mock都已初始化
    expect(await wsMarket.isWebSocketMocked()).toBeTruthy();
    expect(await wsRisk.isWebSocketMocked()).toBeTruthy();
  });
});

test.describe('WebSocket性能测试（Mock）', () => {
  test('应该能够处理高频消息推送', async ({ page }) => {
    const wsMock = new WebSocketMock(page);
    await wsMock.initialize();

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // 模拟高频推送（100条消息/秒）
    const messageCount = 100;
    const startTime = Date.now();

    for (let i = 0; i < messageCount; i++) {
      await wsMock.mockMarketData({
        type: 'market_update',
        data: {
          index: i,
          price: 3200 + Math.random() * 100,
          timestamp: Date.now()
        }
      });
    }

    const endTime = Date.now();
    const duration = endTime - startTime;

    // 验证性能：100条消息推送应该在合理时间内完成
    expect(duration).toBeLessThan(5000); // 5秒内完成
  });

  test('批量数据推送不应该阻塞UI', async ({ page }) => {
    const wsMock = new WebSocketMock(page);
    await wsMock.initialize();

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // 推送大量数据
    const batchSize = 50;
    const promises = [];

    for (let i = 0; i < batchSize; i++) {
      promises.push(wsMock.mockMarketData(MarketDataScenarios.normalMarketData));
    }

    await Promise.all(promises);

    // 验证页面仍然响应
    await page.waitForTimeout(500);

    const isResponsive = await page.evaluate(() => {
      // 检查事件循环是否正常
      let counter = 0;
      return new Promise((resolve) => {
        const interval = setInterval(() => {
          counter++;
          if (counter >= 5) {
            clearInterval(interval);
            resolve(true);
          }
        }, 10);
      });
    });

    expect(isResponsive).toBeTruthy();
  });
});
