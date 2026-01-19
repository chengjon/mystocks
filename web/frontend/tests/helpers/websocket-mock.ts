/**
 * WebSocket Mock Utilities for E2E Testing
 *
 * 用途：在Playwright E2E测试中模拟WebSocket连接和消息
 * 解决：不依赖真实后端WebSocket服务，提高测试稳定性
 */

export interface MockWebSocketMessage {
  channel: string;
  data: any;
  timestamp?: number;
}

export class WebSocketMock {
  private page: any;
  private mockUrl: string;

  constructor(page: any, wsUrl: string = 'ws://localhost:8000/api/ws') {
    this.page = page;
    this.mockUrl = wsUrl;
  }

  /**
   * 初始化WebSocket mock - 拦截WebSocket连接并模拟响应
   */
  async initialize() {
    await this.page.addInitScript(() => {
      // 保存原始WebSocket构造函数
      const OriginalWebSocket = (window as any).WebSocket;

      // 模拟WebSocket类
      class MockWebSocket {
        url: string;
        readyState: number = 0; // CONNECTING
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;
        onerror: ((event: Event) => void) | null = null;
        onclose: ((event: CloseEvent) => void) | null = null;
        private messageHandlers: Set<(event: MessageEvent) => void> = new Set();

        constructor(url: string, protocols?: string | string[]) {
          this.url = url;

          // 模拟连接延迟
          setTimeout(() => {
            this.readyState = 1; // OPEN
            if (this.onopen) {
              this.onopen(new Event('open'));
            }
          }, 100);
        }

        addEventListener(event: string, handler: any) {
          if (event === 'message') {
            this.messageHandlers.add(handler);
          } else if (event === 'open') {
            this.onopen = handler;
          } else if (event === 'error') {
            this.onerror = handler;
          } else if (event === 'close') {
            this.onclose = handler;
          }
        }

        removeEventListener(event: string, handler: any) {
          if (event === 'message') {
            this.messageHandlers.delete(handler);
          }
        }

        send(data: string) {
          // 模拟服务器响应
          setTimeout(() => {
            const parsed = JSON.parse(data);
            if (parsed.type === 'subscribe') {
              // 发送订阅确认
              this.receiveMessage({
                type: 'subscription_confirmed',
                channel: parsed.channel
              });
            }
          }, 50);
        }

        close(code?: number, reason?: string) {
          this.readyState = 3; // CLOSED
          if (this.onclose) {
            this.onclose(new CloseEvent('close', { code, reason }));
          }
        }

        // 内部方法：模拟接收消息
        private receiveMessage(data: any) {
          const messageEvent = new MessageEvent('message', {
            data: JSON.stringify(data)
          });

          if (this.onmessage) {
            this.onmessage(messageEvent);
          }
          this.messageHandlers.forEach(handler => handler(messageEvent));
        }
      }

      // 替换全局WebSocket
      (window as any).WebSocket = MockWebSocket as any;
      (window as any).MockWebSocket = MockWebSocket;
    });
  }

  /**
   * 模拟市场数据推送
   */
  async mockMarketData(data: any = {
    type: 'market_summary',
    data: {
      indices: [
        { code: '000001', name: '上证指数', price: 3245.67, change: 1.23 },
        { code: '399001', name: '深证成指', price: 10234.56, change: -0.45 }
      ]
    }
  }) {
    await this.page.evaluate((data) => {
      const ws = (window as any).currentWebSocket;
      if (ws && ws.readyState === 1) {
        ws.receiveMessage({
          channel: 'market:summary',
          data: data.data,
          timestamp: Date.now()
        });
      }
    }, data);
  }

  /**
   * 模拟风险预警推送
   */
  async mockRiskAlert(alert: any = {
    type: 'risk_alert',
    level: 'warning',
    message: '测试风险预警'
  }) {
    await this.page.evaluate((alert) => {
      const ws = (window as any).currentWebSocket;
      if (ws && ws.readyState === 1) {
        ws.receiveMessage({
          channel: 'risk:overview',
          data: alert,
          timestamp: Date.now()
        });
      }
    }, alert);
  }

  /**
   * 模拟策略信号推送
   */
  async mockStrategySignal(signal: any = {
    type: 'strategy_signal',
    strategy: 'MACD策略',
    symbol: '000001',
    action: 'buy'
  }) {
    await this.page.evaluate((signal) => {
      const ws = (window as any).currentWebSocket;
      if (ws && ws.readyState === 1) {
        ws.receiveMessage({
          channel: 'strategy:overview',
          data: signal,
          timestamp: Date.now()
        });
      }
    }, signal);
  }

  /**
   * 模拟连接错误
   */
  async mockConnectionError() {
    await this.page.evaluate(() => {
      const ws = (window as any).currentWebSocket;
      if (ws && ws.onerror) {
        ws.onerror(new Event('error'));
      }
    });
  }

  /**
   * 模拟连接关闭
   */
  async mockConnectionClose(code: number = 1000, reason: string = 'Normal closure') {
    await this.page.evaluate(({ code, reason }) => {
      const ws = (window as any).currentWebSocket;
      if (ws && ws.onclose) {
        ws.readyState = 3;
        ws.onclose(new CloseEvent('close', { code, reason }));
      }
    }, { code, reason });
  }

  /**
   * 获取WebSocket连接状态
   */
  async getConnectionState(): Promise<number> {
    return await this.page.evaluate(() => {
      const ws = (window as any).currentWebSocket;
      return ws ? ws.readyState : -1;
    });
  }

  /**
   * 验证WebSocket已初始化
   */
  async isWebSocketMocked(): Promise<boolean> {
    return await this.page.evaluate(() => {
      return typeof (window as any).MockWebSocket !== 'undefined';
    });
  }
}

/**
 * 创建预定义的市场数据模拟场景
 */
export const MarketDataScenarios = {
  /**
   * 正常市场数据推送
   */
  normalMarketData: {
    type: 'market_summary',
    data: {
      indices: [
        { code: '000001', name: '上证指数', price: 3245.67, change: 1.23, changePercent: 0.038 },
        { code: '399001', name: '深证成指', price: 10234.56, change: -0.45, changePercent: -0.0044 },
        { code: '399006', name: '创业板指', price: 2156.78, change: 12.34, changePercent: 0.574 }
      ],
      timestamp: Date.now()
    }
  },

  /**
   * 大幅波动的市场数据（测试UI响应）
   */
  volatileMarketData: {
    type: 'market_summary',
    data: {
      indices: [
        { code: '000001', name: '上证指数', price: 3200.00, change: -45.67, changePercent: -1.40 },
        { code: '399001', name: '深证成指', price: 10100.00, change: -134.56, changePercent: -1.31 }
      ],
      timestamp: Date.now()
    }
  },

  /**
   * 空数据（测试错误处理）
   */
  emptyMarketData: {
    type: 'market_summary',
    data: {
      indices: [],
      timestamp: Date.now()
    }
  }
};

/**
 * 创建预定义的风险预警场景
 */
export const RiskAlertScenarios = {
  /**
   * 信息级预警
   */
  infoAlert: {
    type: 'risk_alert',
    level: 'info',
    message: '系统正常运行',
    timestamp: Date.now()
  },

  /**
   * 警告级预警
   */
  warningAlert: {
    type: 'risk_alert',
    level: 'warning',
    message: '持仓集中度超过阈值',
    details: {
      symbol: '000001',
      concentration: 35
    },
    timestamp: Date.now()
  },

  /**
   * 严重级预警
   */
  criticalAlert: {
    type: 'risk_alert',
    level: 'critical',
    message: '触发止损规则',
    details: {
      symbol: '000002',
      stopLossPrice: 15.50,
      currentPrice: 15.45
    },
    timestamp: Date.now()
  }
};
