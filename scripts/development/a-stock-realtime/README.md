# MyStocks A股实时行情WebSocket服务器

基于FastAPI + WebSocket的A股实时行情数据推送服务器。

## 功能特性

✅ **实时推送**: 每1秒推送增量市场数据更新
✅ **完整快照**: 连接时立即发送完整市场数据快照
✅ **多客户端支持**: 同时支持多个WebSocket连接
✅ **CORS支持**: 支持跨域访问，方便前端集成
✅ **健康检查**: 提供HTTP健康检查端点
✅ **API文档**: 自动生成的Swagger文档

## 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 启动服务器

**方式1: 使用启动脚本（推荐）**
```bash
bash start_server.sh
```

**方式2: 直接运行**
```bash
python3 websocket_server.py
```

服务器将在 `http://localhost:8000` 启动

### 3. 测试连接

**在新终端运行测试客户端:**
```bash
python3 test_client.py
```

## API端点

### WebSocket端点

- **URL**: `ws://localhost:8001/ws/market`
- **协议**: WebSocket
- **消息格式**: JSON

#### 客户端消息格式

```json
// 开始接收实时数据
{"action": "start"}

// 停止接收数据
{"action": "stop"}

// 请求完整快照
{"action": "snapshot"}
```

#### 服务器消息格式

**1. 初始快照消息**
```json
{
  "type": "init",
  "data": {
    "indices": [...],
    "stocks": [...],
    "marketStats": {...},
    "hotSectors": [...]
  }
}
```

**2. 增量更新消息**
```json
{
  "type": "incremental",
  "timestamp": "2025-12-26T10:23:45",
  "updates": [
    {"type": "index", "data": {...}},
    {"type": "stock", "data": {...}}
  ]
}
```

**3. 信息消息**
```json
{
  "type": "info",
  "message": "开始接收实时行情数据..."
}
```

### HTTP端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根路径，返回API信息 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger API文档 |

## 数据结构

### 指数数据

```typescript
{
  code: string,        // 指数代码，如 "000001"
  name: string,        // 指数名称，如 "上证指数"
  value: number,       // 当前点位
  change: number,     // 涨跌幅 (%)
  changeAmount: number, // 涨跌点数
  volume: string,     // 成交量，如 "2856亿"
  timestamp: string   // 时间戳
}
```

### 股票数据

```typescript
{
  code: string,        // 股票代码，如 "600519"
  name: string,        // 股票名称，如 "贵州茅台"
  price: number,       // 最新价
  change: number,      // 涨跌幅 (%)
  volume: string,      // 成交量，如 "2.3万手"
  timestamp: string    // 时间戳
}
```

### 市场统计数据

```typescript
{
  limitUp: number,      // 涨停数
  limitDown: number,    // 跌停数
  northBound: number,   // 北向资金（亿）
  totalVolume: number,  // 总成交额（亿）
  riseCount: number,    // 上涨家数
  fallCount: number     // 下跌家数
}
```

## 集成到前端

### JavaScript/TypeScript示例

```typescript
class MarketDataClient {
  private ws: WebSocket;
  private handlers: Map<string, (data: any) => void>;

  constructor(url: string) {
    this.ws = new WebSocket(url);
    this.handlers = new Map();

    this.ws.onopen = () => {
      console.log('✅ WebSocket连接成功');
      this.send({ action: 'start' });
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket错误:', error);
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket连接关闭');
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'init':
        this.handlers.get('init')?.(message.data);
        break;
      case 'incremental':
        message.updates.forEach((update: any) => {
          this.handlers.get(update.type)?.(update.data);
        });
        break;
      case 'info':
        console.log('ℹ️', message.message);
        break;
    }
  }

  on(event: string, handler: (data: any) => void) {
    this.handlers.set(event, handler);
  }

  send(message: any) {
    this.ws.send(JSON.stringify(message));
  }
}

// 使用示例
const client = new MarketDataClient('ws://localhost:8000/ws/market');

client.on('init', (snapshot) => {
  console.log('收到初始快照:', snapshot);
});

client.on('index', (index) => {
  console.log('指数更新:', index);
});

client.on('stock', (stock) => {
  console.log('股票更新:', stock);
});
```

## 技术栈

- **FastAPI 0.115.0**: 现代Python Web框架
- **WebSocket**: 实时双向通信
- **Uvicorn**: ASGI服务器
- **Pydantic 2.7**: 数据验证

## 配置

### 修改端口

编辑 `websocket_server.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8888)  # 修改端口
```

### 修改更新频率

编辑 `market_data_simulator.py`:

```python
await asyncio.sleep(0.5)  # 改为0.5秒更新一次
```

### 添加更多股票

编辑 `market_data_simulator.py`:

```python
self.stocks = {
    '600519': {'name': '贵州茅台', 'price': 1856.00, 'change': 2.35},
    # 添加更多股票...
}
```

## 故障排除

### 端口被占用

```bash
# 查找占用进程
lsof -i :8000

# 停止进程
kill -9 <PID>
```

### 依赖安装失败

```bash
# 升级pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 许可证

MIT License

---

**MyStocks量化交易平台** © 2025
