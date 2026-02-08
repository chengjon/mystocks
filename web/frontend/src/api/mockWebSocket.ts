// web/frontend/src/api/mockWebSocket.ts

type MessageHandler = (data: any) => void;

class MockWebSocketService {
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private timers: Map<string, number> = new Map();
  private connected: boolean = false;

  constructor() {
    this.connected = true; // Auto connect for mock
  }

  // Subscribe to a topic (e.g., 'market.quote.000001')
  subscribe(topic: string, handler: MessageHandler) {
    if (!this.handlers.has(topic)) {
      this.handlers.set(topic, new Set());
      this.startEmitting(topic);
    }
    this.handlers.get(topic)?.add(handler);
  }

  unsubscribe(topic: string, handler: MessageHandler) {
    const topicHandlers = this.handlers.get(topic);
    if (topicHandlers) {
      topicHandlers.delete(handler);
      if (topicHandlers.size === 0) {
        this.stopEmitting(topic);
        this.handlers.delete(topic);
      }
    }
  }

  private startEmitting(topic: string) {
    // Generate random data based on topic type
    const interval = 3000; // 3 seconds update
    
    const timer = setInterval(() => {
        const data = this.generateData(topic);
        this.handlers.get(topic)?.forEach(h => h(data));
    }, interval) as unknown as number; // Node.js vs Browser typing

    this.timers.set(topic, timer);
  }

  private stopEmitting(topic: string) {
    const timer = this.timers.get(topic);
    if (timer) {
        clearInterval(timer);
        this.timers.delete(topic);
    }
  }

  private generateData(topic: string) {
    if (topic.startsWith('market.trend.')) {
        // Return a new price point for trend
        // In real WS, this might be a single point { timestamp, price }
        return {
            topic,
            data: {
                timestamp: Date.now(),
                price: (3120 + Math.random() * 20).toFixed(2)
            }
        };
    } else if (topic.startsWith('market.quote.')) {
        // Return quote update
        return {
            topic,
            data: {
                price: (100 + Math.random() * 5).toFixed(2),
                change: (Math.random() * 2 - 1).toFixed(2),
                volume: Math.floor(Math.random() * 10000)
            }
        };
    }
    return { topic, data: {} };
  }
}

export const mockWebSocket = new MockWebSocketService();
