# API合约规范 (API Contracts)

本目录包含股票数据扩展功能的所有API合约规范（OpenAPI 3.0格式）

## 已完成的合约

### 1. market_data_api.yaml - 市场行情数据API ✅
**端点**: `/api/market/*`
**功能**:
- 个股资金流向数据 (`/market/fund-flow`)
- ETF基金实时行情 (`/market/etf/list`)
- 竞价抢筹数据 (`/market/chip-race`)
- 龙虎榜数据 (`/market/long-hu-bang`)
- 大宗交易数据 (`/market/block-trade`)
- 分红配送数据 (`/market/dividend`)

**数据源**: Akshare Adapter (ENHANCE) + TQLEX Adapter (NEW)

### 2. strategy_api.yaml - 策略管理API ✅
**端点**: `/api/strategies/*`, `/api/signals/*`, `/api/backtest/*`
**功能**:
- 策略列表和配置管理 (`/strategies/list`, `/strategies/{id}/config`)
- 实时信号生成 (`/signals/generate`)
- 历史信号查询 (`/signals/history`)
- 策略回测 (`/backtest/run`)
- 回测结果查询 (`/backtest/{id}`, `/backtest/history`)

**核心组件**: StrategyEngine (NEW) + BacktestEngine (NEW)

### 3. technical_analysis_api.yaml - 技术分析API
**端点**: `/api/indicators/*`
**功能**:
- 指标注册表查询 (`/indicators/registry`) - EXISTING
- 技术指标计算 (`/indicators/calculate`) - EXISTING
- 指标分类查询 (`/indicators/registry/{category}`) - EXISTING

**状态**: 已有实现，此合约为文档化现有API

### 4. 数据服务API (集成到现有端点)
**端点**: `/api/data/*`
**功能**:
- 股票日线数据 (`/data/stocks/daily`) - EXISTING
- 股票搜索 (`/data/stocks/search`) - EXISTING
- 自动数据获取 (auto-fetch) - EXISTING

**状态**: 已有实现，与indicators API配合使用

## API设计原则

1. **RESTful风格**: 使用标准HTTP方法和状态码
2. **统一响应格式**: 所有响应使用 `{code, message, data}` 结构
3. **JWT认证**: 所有API使用Bearer Token认证
4. **分页支持**: 列表接口支持 `limit` 和 `offset` 参数
5. **错误处理**: 标准化错误响应格式

## 响应格式规范

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 实际数据
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Bad Request",
  "detail": "具体错误描述"
}
```

## HTTP状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源未找到
- `422 Unprocessable Entity`: 业务逻辑验证失败
- `500 Internal Server Error`: 服务器内部错误

## 使用示例

### 1. 获取资金流向数据
```bash
curl -X GET "http://localhost:8888/api/market/fund-flow?symbol=600519.SH&timeframe=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 运行策略回测
```bash
curl -X POST "http://localhost:8888/api/backtest/run" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "volume_breakout",
    "symbol": "600519.SH",
    "start_date": "2023-01-01",
    "end_date": "2024-10-14",
    "initial_capital": 1000000.00,
    "parameters": {
      "vol_period": 20,
      "volume_threshold": 2.0
    }
  }'
```

### 3. 计算技术指标
```bash
curl -X POST "http://localhost:8888/api/indicators/calculate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-10-14",
    "indicators": [
      {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
      {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
    ],
    "use_cache": true
  }'
```

## 开发工具

推荐使用以下工具查看和测试API:
- **Swagger UI**: 访问 `http://localhost:8888/docs` (FastAPI自动生成)
- **Postman**: 导入OpenAPI规范文件
- **curl**: 命令行测试

## 下一步

- ⏳ 实现market_data_api.yaml中定义的所有端点
- ⏳ 实现strategy_api.yaml中定义的策略引擎和回测引擎
- ✅ technical_analysis_api.yaml已有实现，需要集成新数据源
