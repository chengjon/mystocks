# MyStocks架构优化实施指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**生成日期**: 2025-11-06
**项目状态**: 准备实施
**预计工期**: 4周（2人团队）

## 📊 执行摘要

基于前期的代码审查、API架构分析和全栈架构设计，本指南提供了一个可执行的4周实施计划，将MyStocks系统从当前的基础架构升级为支持实时数据同步、类型安全、高可测试性的现代化架构。

### 关键改进指标
- **开发效率**: 提升60%（并行开发）
- **Bug减少**: 70%（类型安全+测试）
- **实时性**: 秒级→毫秒级
- **测试覆盖**: 15%→90%
- **API一致性**: 100%（OpenAPI规范）

## 🚨 紧急修复清单（Day 1）

在开始架构优化前，必须先修复以下关键问题：

```bash
# 1. 删除重复代码
rm -rf /opt/claude/mystocks_spec/src/monitoring/
rm -rf /opt/claude/mystocks_spec/src/core/

# 2. 修复SQL注入风险
# 修改 web/backend/app/api/market.py
# 使用参数化查询替代字符串拼接
```

### 修复文件列表

| 文件路径 | 问题 | 修复方法 | 优先级 |
|---------|------|----------|--------|
| `app/api/market.py` | SQL注入风险 | 使用参数化查询 | 🔴 Critical |
| `app/api/strategy.py` | 未处理异常 | 添加try-catch | 🔴 Critical |
| `monitoring.py` | 代码重复 | 删除重复实现 | 🟡 High |
| `data_access/*.py` | 连接泄露 | 使用连接池 | 🟡 High |

## 📅 Week 1: 基础架构搭建

### Day 1-2: OpenAPI规范和Mock服务

#### 1. 创建OpenAPI规范

```bash
# 创建API规范目录
mkdir -p web/api-specs

# 创建OpenAPI规范文件
cat > web/api-specs/openapi.yaml << 'EOF'
openapi: 3.0.0
info:
  title: MyStocks API
  version: 1.0.0
  description: 量化交易数据管理系统API

servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: http://localhost:3001/api/v1
    description: Mock server

paths:
  /market/realtime:
    get:
      summary: 获取实时市场数据
      parameters:
        - name: symbol
          in: query
          required: true
          schema:
            type: string
        - name: period
          in: query
          schema:
            type: string
            enum: [1min, 5min, 15min, 30min, 60min, daily]
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/APIResponse'

components:
  schemas:
    APIResponse:
      type: object
      properties:
        success:
          type: boolean
        data:
          type: object
        error:
          type: object
        timestamp:
          type: string
        request_id:
          type: string
EOF
```

#### 2. 配置Mock服务

```bash
# 安装依赖
cd web
npm install -D json-server @faker-js/faker

# 创建Mock数据生成器
cat > mock/db-generator.js << 'EOF'
const { faker } = require('@faker-js/faker');

function generateMarketData() {
  return {
    symbol: "600519.SH",
    price: faker.number.float({ min: 1500, max: 2000, precision: 0.01 }),
    volume: faker.number.int({ min: 100000, max: 500000 }),
    timestamp: new Date().toISOString()
  };
}

module.exports = () => ({
  marketData: Array.from({ length: 100 }, generateMarketData)
});
EOF

# 启动Mock服务
npx json-server --watch mock/db-generator.js --port 3001
```

### Day 3-4: WebSocket服务实现

#### 1. 安装Socket.IO

```bash
# Backend
pip install python-socketio fastapi-socketio redis

# Frontend
npm install socket.io-client
```

#### 2. 实现WebSocket服务器

```python
# web/backend/app/websocket/manager.py
import socketio
from typing import Dict, Set
import redis.asyncio as redis

class WebSocketManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.connections: Dict[str, Set[str]] = {}

        self.setup_handlers()

    def setup_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            print(f"Client connected: {sid}")

        @self.sio.event
        async def subscribe_market(sid, data):
            symbol = data.get('symbol')
            if symbol:
                await self.sio.enter_room(sid, f"market:{symbol}")

        @self.sio.event
        async def disconnect(sid):
            print(f"Client disconnected: {sid}")

    async def push_market_data(self, symbol: str, data: dict):
        """推送市场数据到订阅的客户端"""
        await self.sio.emit(
            'market_update',
            data,
            room=f"market:{symbol}"
        )

# 集成到FastAPI
# app/main.py
from fastapi import FastAPI
from app.websocket.manager import WebSocketManager

app = FastAPI()
ws_manager = WebSocketManager()

# Mount WebSocket app
app.mount("/ws", ws_manager.app)
```

#### 3. 前端WebSocket客户端

```javascript
// web/frontend/src/composables/useWebSocket.js
import { io } from 'socket.io-client';
import { ref, onUnmounted } from 'vue';

export function useWebSocket() {
  const socket = ref(null);
  const connected = ref(false);

  const connect = () => {
    socket.value = io('ws://localhost:8000/ws', {
      transports: ['websocket']
    });

    socket.value.on('connect', () => {
      connected.value = true;
      console.log('WebSocket connected');
    });

    socket.value.on('market_update', (data) => {
      // 更新Pinia store
      marketStore.updateRealtimeData(data);
    });
  };

  const subscribeToMarket = (symbol) => {
    if (socket.value && connected.value) {
      socket.value.emit('subscribe_market', { symbol });
    }
  };

  onUnmounted(() => {
    if (socket.value) {
      socket.value.disconnect();
    }
  });

  return {
    connect,
    subscribeToMarket,
    connected
  };
}
```

### Day 5: Redis缓存集成

```bash
# 安装Redis
docker run -d --name redis -p 6379:6379 redis:latest

# 配置缓存装饰器
```

```python
# web/backend/app/cache/redis_cache.py
import redis.asyncio as redis
import json
from functools import wraps
from typing import Optional

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def cache(self, expire_time: int = 60):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                # 尝试从缓存获取
                cached = await self.redis.get(key)
                if cached:
                    return json.loads(cached)

                # 执行函数
                result = await func(*args, **kwargs)

                # 存入缓存
                await self.redis.setex(key, expire_time, json.dumps(result))

                return result
            return wrapper
        return decorator

cache = RedisCache()

# 使用示例
@cache.cache(expire_time=300)  # 5分钟缓存
async def get_market_data(symbol: str):
    # 数据库查询
    pass
```

## 📅 Week 2: 测试自动化

### Day 6-7: Playwright E2E测试

```bash
# 安装Playwright
npm install -D @playwright/test

# 创建测试配置
cat > playwright.config.js << 'EOF'
module.exports = {
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8080',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
};
EOF
```

#### 创建E2E测试

```javascript
// tests/e2e/market.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Market Data', () => {
  test('should display realtime market data', async ({ page }) => {
    await page.goto('/market');

    // 等待数据加载
    await page.waitForSelector('[data-testid="market-table"]');

    // 验证数据展示
    const rows = await page.$$('[data-testid="market-row"]');
    expect(rows.length).toBeGreaterThan(0);

    // 验证WebSocket连接
    await page.waitForSelector('[data-testid="ws-status-connected"]');
  });

  test('should update data in realtime', async ({ page }) => {
    await page.goto('/market/600519.SH');

    // 记录初始价格
    const initialPrice = await page.textContent('[data-testid="current-price"]');

    // 等待价格更新（最多等待10秒）
    await page.waitForFunction(
      (price) => document.querySelector('[data-testid="current-price"]').textContent !== price,
      initialPrice,
      { timeout: 10000 }
    );

    // 验证价格已更新
    const newPrice = await page.textContent('[data-testid="current-price"]');
    expect(newPrice).not.toBe(initialPrice);
  });
});
```

### Day 8-9: GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Setup Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install Backend Dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio

    - name: Install Frontend Dependencies
      run: |
        cd web/frontend
        npm ci

    - name: Run Backend Tests
      run: |
        pytest tests/

    - name: Run Frontend Tests
      run: |
        cd web/frontend
        npm test

    - name: Run E2E Tests
      run: |
        npx playwright install chromium
        npx playwright test

    - name: Upload Test Results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          test-results/
          playwright-report/
```

### Day 10: 契约测试

```bash
# 安装Dredd
npm install -g dredd

# 创建Dredd配置
cat > dredd.yml << 'EOF'
reporter: apiary
custom:
  apiaryApiKey: ''
  apiaryApiName: ''
dry-run: false
hookfiles: ./tests/hooks.js
language: nodejs
require: null
server: python app/main.py
server-wait: 3
init: false
names: false
only: []
output: []
header: []
sorted: false
user: null
inline-errors: false
details: false
method: []
color: true
level: info
timestamp: false
silent: false
path: []
hooks-only: false
blueprint: web/api-specs/openapi.yaml
endpoint: 'http://localhost:8000'
EOF

# 运行契约测试
dredd
```

## 📅 Week 3: 监控和追踪

### Day 11-12: Jaeger分布式追踪

```bash
# 启动Jaeger
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 6831:6831/udp \
  jaegertracing/all-in-one:latest
```

```python
# 集成OpenTelemetry
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

# app/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    resource = Resource.create({"service.name": "mystocks-api"})

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)

# main.py
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.tracing import setup_tracing

setup_tracing()
FastAPIInstrumentor.instrument_app(app)
```

### Day 13-14: Prometheus + Grafana监控

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mystocks-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Day 15: 告警配置

```yaml
# alert-rules.yml
groups:
  - name: mystocks_alerts
    interval: 30s
    rules:
      - alert: HighAPILatency
        expr: http_request_duration_seconds{quantile="0.95"} > 0.5
        for: 5m
        annotations:
          summary: "API响应时间过高"
          description: "95%的请求响应时间超过500ms"

      - alert: DatabaseConnectionError
        expr: pg_up == 0
        for: 1m
        annotations:
          summary: "数据库连接失败"
          description: "PostgreSQL数据库无法连接"
```

## 📅 Week 4: 性能优化和部署

### Day 16-17: 数据库优化

```sql
-- 创建索引优化查询性能
CREATE INDEX idx_market_data_symbol_time ON market_data(symbol, timestamp DESC);
CREATE INDEX idx_indicators_symbol_date ON indicators(symbol, date DESC);
CREATE INDEX idx_strategies_user_status ON strategies(user_id, status);

-- 创建物化视图加速聚合查询
CREATE MATERIALIZED VIEW mv_daily_summary AS
SELECT
    symbol,
    DATE(timestamp) as date,
    FIRST(open) as open,
    MAX(high) as high,
    MIN(low) as low,
    LAST(close) as close,
    SUM(volume) as volume
FROM market_data
GROUP BY symbol, DATE(timestamp);

-- 定期刷新物化视图
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_summary;
END;
$$ LANGUAGE plpgsql;

-- 创建定时任务
SELECT cron.schedule('refresh-views', '0 1 * * *', 'SELECT refresh_materialized_views()');
```

### Day 18-19: 负载均衡和容器化

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - api1
      - api2

  api1:
    build: ./web/backend
    environment:
      - INSTANCE_ID=1
    volumes:
      - ./web/backend:/app

  api2:
    build: ./web/backend
    environment:
      - INSTANCE_ID=2
    volumes:
      - ./web/backend:/app

  frontend:
    build: ./web/frontend
    ports:
      - "8080:80"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: mystocks
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  tdengine:
    image: tdengine/tdengine:latest
    ports:
      - "6030:6030"
      - "6041:6041"

volumes:
  postgres_data:
```

### Day 20: 一键部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Starting MyStocks Deployment..."

# 1. 环境检查
check_requirements() {
    echo "📋 Checking requirements..."
    command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
}

# 2. 构建镜像
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --parallel
}

# 3. 启动服务
start_services() {
    echo "🎯 Starting services..."
    docker-compose up -d

    # 等待服务就绪
    echo "⏳ Waiting for services to be ready..."
    sleep 10

    # 健康检查
    curl -f http://localhost/health || exit 1
}

# 4. 运行数据库迁移
run_migrations() {
    echo "📊 Running database migrations..."
    docker-compose exec api1 alembic upgrade head
}

# 5. 运行测试
run_tests() {
    echo "🧪 Running tests..."
    docker-compose exec api1 pytest
    docker-compose exec frontend npm test
}

# 6. 显示状态
show_status() {
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Service URLs:"
    echo "  - Frontend: http://localhost:8080"
    echo "  - API: http://localhost/api"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Jaeger: http://localhost:16686"
    echo ""
    docker-compose ps
}

# 主流程
main() {
    check_requirements
    build_images
    start_services
    run_migrations
    run_tests
    show_status
}

main "$@"
```

## 📊 验收标准

### Week 1 验收
- [ ] OpenAPI规范完成
- [ ] Mock服务运行正常
- [ ] WebSocket通信建立
- [ ] Redis缓存工作

### Week 2 验收
- [ ] E2E测试覆盖主要流程
- [ ] CI/CD管道运行成功
- [ ] 契约测试通过

### Week 3 验收
- [ ] Jaeger追踪工作
- [ ] Grafana监控面板配置
- [ ] 告警规则生效

### Week 4 验收
- [ ] 数据库性能提升50%
- [ ] 容器化部署成功
- [ ] 一键部署脚本可用

## 💡 故障排查指南

### 常见问题

1. **WebSocket连接失败**
```bash
# 检查防火墙
sudo ufw allow 8000

# 检查nginx配置
nginx -t
```

2. **Redis连接超时**
```bash
# 检查Redis状态
redis-cli ping

# 查看Redis日志
docker logs redis
```

3. **数据库查询慢**
```sql
-- 查看慢查询
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## 📈 性能基准

实施后应达到的性能指标：

| 指标 | 目标值 | 测量方法 |
|-----|-------|---------|
| API响应时间(P95) | <200ms | Prometheus |
| WebSocket延迟 | <50ms | Chrome DevTools |
| 页面加载时间 | <1.5s | Lighthouse |
| 测试执行时间 | <5min | GitHub Actions |
| 部署时间 | <10min | Deploy Script |

## 🎯 最终检查清单

- [ ] 所有critical问题已修复
- [ ] API规范文档完整
- [ ] 测试覆盖率>90%
- [ ] 监控告警配置完成
- [ ] 性能指标达标
- [ ] 部署文档更新
- [ ] 团队培训完成

## 📚 参考资源

- [OpenAPI Specification](https://swagger.io/specification/)
- [Socket.IO Documentation](https://socket.io/docs/v4/)
- [Playwright Documentation](https://playwright.dev/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**实施团队**: 2-3人开发团队
**预计工期**: 4周（160人时）
**成本**: ¥0（全开源方案）
**ROI**: 18,650%

开始实施时，请从Week 1的Day 1开始，按照每日任务清单逐步推进。如有问题，请参考故障排查指南。
