# MyStocks API 压力测试指南

## 前置要求

1. 安装 Locust：
```bash
pip install locust
```

2. 确保后端服务运行在：
```bash
cd web/backend
python -m app.main
```

## 运行压力测试

### 1. Web界面模式（推荐）

启动 Locust Web 界面：
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

然后访问 http://localhost:8089

### 2. 命令行模式

运行5分钟压力测试：
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=reports/locust_report.html
```

### 3. 测试特定用户类型

只测试市场数据用户：
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --user-class=MarketDataUser \
  --users=50 \
  --spawn-rate=5 \
  --run-time=3m \
  --headless \
  --html=reports/locust_market_data.html
```

## 性能目标

- **并发用户**: 100
- **RPS (Requests Per Second)**: > 500
- **响应时间 P95**: < 500ms
- **响应时间 P99**: < 1000ms
- **错误率**: < 1%

## 用户类型说明

1. **StockAPIUser**: 基础API用户（健康检查、CSRF Token、文档等）
2. **MarketDataUser**: 市场数据用户（股票列表、K线、实时数据）
3. **TechnicalAnalysisUser**: 技术分析用户（指标计算）
4. **CacheUser**: 缓存管理用户（缓存统计、清除）
5. **StrategyUser**: 策略执行用户（策略列表、执行策略）

## 报告位置

生成的HTML报告将保存在 `reports/` 目录：
- `locust_report.html` - 完整测试报告
- `locust_market_data.html` - 市场数据测试报告
- 等...
