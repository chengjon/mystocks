# MyStocks API 文档索引

## 在线文档

| 文档类型 | URL | 说明 |
|---------|-----|------|
| Swagger UI | http://localhost:8000/docs | 交互式 API 文档 |
| ReDoc | http://localhost:8000/redoc | 替代 API 文档界面 |
| OpenAPI Schema | `/docs/api/openapi.json` | OpenAPI 3.1.0 JSON 格式 |
| YAML Schema | `/docs/api/openapi.yaml` | OpenAPI 3.1.0 YAML 格式 |

---

## 核心端点

### 认证模块 (Authentication)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 用户登出 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/auth/csrf` | 获取 CSRF Token |

**请求示例** (登录):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 7200
  },
  "msg": "success"
}
```

---

### 市场数据模块 (Market Data)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/market/symbols` | 获取股票列表 |
| GET | `/api/v1/market/kline` | 获取 K 线数据 |
| GET | `/api/v1/market/realtime` | 获取实时行情 |
| GET | `/api/v1/market/quote` | 获取盘口报价 |
| GET | `/api/v1/market/history` | 获取历史数据 |
| GET | `/api/v1/market/moneyflow` | 获取资金流向 |
| GET | `/api/v1/market/limit` | 获取涨跌停信息 |
| GET | `/api/v1/market/adj` | 获取复权因子 |

**参数说明** (K 线):
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbol | string | 是 | 股票代码，如 `000001.SZ` |
| start_date | string | 是 | 开始日期，`YYYY-MM-DD` |
| end_date | string | 是 | 结束日期，`YYYY-MM-DD` |
| interval | string | 否 | 周期，`daily`/`weekly`/`monthly`，默认 `daily` |

---

### 策略管理模块 (Strategies)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/strategies` | 获取策略列表 |
| POST | `/api/v1/strategies` | 创建策略 |
| GET | `/api/v1/strategies/{id}` | 获取策略详情 |
| PUT | `/api/v1/strategies/{id}` | 更新策略 |
| DELETE | `/api/v1/strategies/{id}` | 删除策略 |
| POST | `/api/v1/strategies/{id}/clone` | 克隆策略 |
| PUT | `/api/v1/strategies/{id}/status` | 更新策略状态 |

---

### 回测模块 (Backtests)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/backtests` | 创建回测 |
| GET | `/api/v1/backtests/{id}` | 获取回测结果 |
| GET | `/api/v1/backtests/{id}/trades` | 获取回测交易记录 |
| GET | `/api/v1/backtests/{id}/equity` | 获取回测权益曲线 |
| GET | `/api/v1/backtests/{id}/metrics` | 获取回测指标 |
| DELETE | `/api/v1/backtests/{id}` | 删除回测结果 |

**回测指标**:
| 指标 | 说明 |
|------|------|
| total_return | 总收益率 |
| annual_return | 年化收益率 |
| max_drawdown | 最大回撤 |
| sharpe_ratio | 夏普比率 |
| sortino_ratio | 索提诺比率 |
| win_rate | 胜率 |
| profit_loss_ratio | 盈亏比 |

---

### 交易模块 (Trading)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/trade/order` | 下单 |
| POST | `/api/v1/trade/cancel` | 撤单 |
| GET | `/api/v1/trade/orders` | 查询委托 |
| GET | `/api/v1/trade/positions` | 查询持仓 |
| GET | `/api/v1/trade/account` | 查询账户 |

---

### 系统监控模块 (System)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/metrics` | Prometheus 指标 |
| GET | `/api/v1/system/status` | 系统状态 |
| GET | `/api/v1/system/info` | 系统信息 |
| GET | `/api/v1/system/version` | 版本信息 |

---

## 数据模型

详见: [DATA_MODELS.md](./DATA_MODELS.md)

## 错误码参考

详见: [ERROR_CODES.md](./ERROR_CODES.md)

## 常见问题

1. **认证失败**: 确保请求头包含 `Authorization: Bearer <token>`
2. **参数错误**: 检查必填参数是否完整
3. **权限不足**: 确认用户角色是否有权限访问该端点

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2025-12-28 | 统一响应格式，添加认证模块 |
| 1.0.0 | 2025-11-01 | 初始版本 |
