# MyStocks Mock数据系统使用指南

## 📋 概述

MyStocks Mock数据系统是一个完整的模拟数据解决方案，专为开发和测试环境设计。系统基于环境变量控制，可以在真实数据源和Mock数据之间无缝切换，为开发者提供稳定、一致、快速的开发和测试体验。

## 🎯 核心特性

- ✅ **环境变量控制**: 通过`USE_MOCK_DATA`开关控制数据源
- ✅ **统一数据管理器**: 集中管理所有Mock数据模块
- ✅ **前端代理配置**: 完整的Vite代理设置
- ✅ **API端点覆盖**: 支持监控、问财、技术分析、策略管理等核心功能
- ✅ **数据格式验证**: 所有Mock数据严格遵循真实API格式
- ✅ **高性能响应**: 毫秒级响应时间，无需外部依赖

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Vite + Vue 3)                   │
├─────────────────────────────────────────────────────────────┤
│                    API代理 (端口3000)                       │
│           /api/* → http://localhost:8888/api/*             │
├─────────────────────────────────────────────────────────────┤
│                   后端API (FastAPI)                        │
│                   端口: 8888 (Mock)                       │
│                   端口: 8000 (真实数据)                     │
├─────────────────────────────────────────────────────────────┤
│                   Mock数据管理层                           │
│         UnifiedMockDataManager + 环境变量控制             │
├─────────────────────────────────────────────────────────────┤
│                   Mock数据模块                             │
│  Dashboard | Stocks | Technical | Wencai | Strategy       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**核心环境变量:**
```bash
# 启用Mock数据系统
USE_MOCK_DATA=true
DATA_SOURCE=mock

# 后端服务配置
BACKEND_PORT=8888
FRONTEND_PORT=3000
```

### 2. 前端配置

```bash
# 复制Mock环境配置
cd web/frontend
cp .env.mock .env

# 启动前端服务
npm run dev
```

**前端环境配置 (.env):**
```bash
# API基础URL（指向Mock后端）
VITE_API_BASE_URL=http://localhost:8888

# Mock模式标识
VITE_APP_MODE=mock
VITE_APP_TITLE=MyStocks Mock System

# 开发工具配置
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

### 3. 启动服务

```bash
# 启动后端Mock服务
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 &

# 启动前端服务 (新终端)
cd web/frontend
npm run dev
```

### 4. 验证系统

```bash
# 检查后端健康状态
curl http://localhost:8888/health

# 测试问财API
curl http://localhost:8888/api/market/wencai/queries

# 测试前端代理
curl http://localhost:3000/api/market/wencai/queries
```

## 📊 API端点文档

### 监控模块 (`/api/monitoring/*`)

#### 获取监控摘要
```bash
GET /api/monitoring/summary
```

**响应示例:**
```json
{
  "total_stocks": 1568,
  "limit_up_count": 23,
  "limit_down_count": 5,
  "strong_up_count": 127,
  "strong_down_count": 89,
  "avg_change_percent": 0.85,
  "total_amount": 2456789000.0,
  "active_alerts": 12,
  "unread_alerts": 5
}
```

### 问财模块 (`/api/market/wencai/*`)

#### 获取预定义查询
```bash
GET /api/market/wencai/queries
```

**响应示例:**
```json
{
  "queries": [
    {
      "id": 1,
      "query_name": "qs_1",
      "query_text": "今天涨停的股票",
      "description": "获取今日涨停股票列表",
      "category": "市场表现",
      "created_at": "2024-01-01T00:00:00",
      "is_active": true
    }
  ],
  "total": 9
}
```

#### 执行查询
```bash
POST /api/market/wencai/query
```

### 技术分析模块 (`/api/technical/*`)

#### 获取技术指标
```bash
GET /api/technical/{symbol}/indicators
```

**响应示例:**
```json
{
  "symbol": "000001",
  "latest_price": 11.7,
  "latest_date": "2025-11-13",
  "data_points": 244,
  "total_indicators": 19,
  "trend": {
    "ma5": 11.65,
    "ma10": 11.48,
    "ma20": 11.32,
    "ma60": 11.05,
    "macd": 0.023,
    "macd_signal": 0.018,
    "macd_hist": 0.005
  },
  "momentum": {
    "rsi6": 74.61,
    "rsi12": 64.20,
    "rsi24": 55.64,
    "kdj_k": 84.69,
    "kdj_d": 87.67,
    "kdj_j": 78.72
  },
  "volatility": {
    "bb_upper": 11.73,
    "bb_middle": 11.52,
    "bb_lower": 11.30,
    "atr": 0.146,
    "atr_percent": 1.25
  },
  "volume": {
    "obv": 123456789,
    "mfi": 65.4,
    "vwap": 11.52
  }
}
```

### 策略管理模块 (`/api/strategy/*`)

#### 获取策略定义
```bash
GET /api/strategy/definitions
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "strategy_code": "volume_surge",
      "strategy_name_cn": "放量上涨",
      "strategy_name_en": "Volume Surge",
      "description": "成交量放大2倍以上且价格上涨的股票",
      "parameters": {
        "threshold": 60,
        "vol_ratio": 2,
        "min_amount": 200000000
      },
      "is_active": true
    }
  ],
  "total": 10
}
```

## 🧪 测试验证

### 运行完整测试套件

```bash
# Mock系统验证测试
python scripts/tests/test_mock_data_validation_simple.py

# 端到端测试
python scripts/tests/test_simple_end_to_end.py

# API健康检查
./scripts/tests/test_all_endpoints.sh
```

### 性能基准

```bash
# 响应时间测试
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8888/api/monitoring/summary

# 并发测试
ab -n 1000 -c 10 http://localhost:8888/api/market/wencai/queries
```

**预期性能指标:**
- API响应时间: < 50ms
- 并发支持: 100+ 请求/秒
- 数据一致性: 100%
- Mock数据覆盖率: >90%

## 🔧 配置选项

### 环境变量详解

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `USE_MOCK_DATA` | `false` | 启用/禁用Mock数据 |
| `DATA_SOURCE` | `real` | 数据源类型 (mock/real) |
| `BACKEND_PORT` | `8888` | Mock后端端口 |
| `FRONTEND_PORT` | `3000` | 前端开发端口 |
| `MOCK_CACHE_TTL` | `300` | Mock数据缓存时间(秒) |

### 前端Vite配置

```javascript
// web/frontend/vite.config.js
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8888',  // Mock后端
        changeOrigin: true
      }
    }
  }
})
```

## 📁 Mock数据模块

### Dashboard模块 (`mock_Dashboard.py`)
- 市场统计 (`get_market_stats()`)
- 市场热度 (`get_market_heat_data()`)
- 领涨板块 (`get_leading_sectors()`)

### Stocks模块 (`mock_Stocks.py`)
- 股票列表 (`get_stock_list()`)
- 实时行情 (`get_real_time_quote()`)
- 历史数据 (`get_historical_data()`)

### Technical模块 (`mock_TechnicalAnalysis.py`)
- 技术指标 (`get_technical_indicators()`)
- 交易信号 (`get_signal_analysis()`)
- K线数据 (`get_kline_data()`)

### Wencai模块 (`mock_Wencai.py`)
- 预定义查询 (`get_wencai_queries()`)
- 查询执行 (`execute_query()`)
- 结果获取 (`get_query_results()`)

### Strategy模块 (`mock_StrategyManagement.py`)
- 策略定义 (`get_strategy_definitions()`)
- 策略执行 (`get_strategy_results()`)
- 匹配股票 (`get_matched_stocks()`)

## 🛠️ 开发指南

### 添加新的Mock数据模块

1. **创建Mock模块**
```python
# src/mock/mock_NewModule.py
def get_new_module_data():
    return {
        "status": "success",
        "data": "mock_data_here"
    }
```

2. **注册到统一管理器**
```python
# web/backend/app/mock/unified_mock_data.py
elif data_type == "new_module":
    from src.mock.mock_NewModule import get_new_module_data
    return get_new_module_data()
```

3. **创建API端点**
```python
# web/backend/app/api/new_module.py
@router.get("/data")
async def get_new_module_data():
    use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    if use_mock:
        mock_manager = get_mock_data_manager()
        return mock_manager.get_data("new_module")
    # ... 真实数据逻辑
```

### 自定义Mock数据

```python
# 修改Mock数据生成逻辑
def custom_mock_generator():
    # 添加随机化
    import random
    random.seed(42)  # 可重现性
    
    # 添加时间戳
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    # 返回格式化数据
    return {
        "timestamp": timestamp,
        "data": "custom_mock_data"
    }
```

## 🔍 故障排查

### 常见问题

**1. 端口占用**
```bash
# 检查端口占用
lsof -i :8888
lsof -i :3000

# 清理进程
pkill -f uvicorn
pkill -f "npm run dev"
```

**2. 代理配置问题**
```bash
# 检查Vite配置
grep -A5 -B5 "proxy" web/frontend/vite.config.js

# 测试代理
curl http://localhost:3000/api/market/wencai/queries
```

**3. 环境变量未生效**
```bash
# 重新加载环境变量
source .env

# 检查变量设置
echo $USE_MOCK_DATA
echo $DATA_SOURCE
```

**4. Mock数据格式错误**
```bash
# 验证API响应
curl -s http://localhost:8888/api/monitoring/summary | jq '.'

# 检查Mock模块导入
python -c "from src.mock.mock_Wencai import get_wencai_queries; print(get_wencai_queries())"
```

### 日志调试

```bash
# 启用详细日志
export LOG_LEVEL=debug

# 查看API请求日志
tail -f web/backend/logs/api.log

# 查看前端代理日志
tail -f web/frontend/npm-debug.log
```

## 📈 性能优化

### 缓存策略
```python
# 调整缓存TTL
mock_manager._cache_ttl = 600  # 10分钟

# 清除缓存
mock_manager.clear_cache()
```

### 数据库连接优化
```python
# 禁用数据库连接池（Mock模式）
os.environ['DISABLE_DB_POOL'] = 'true'
```

### 前端构建优化
```bash
# 生产构建
npm run build

# 分析包大小
npm run build -- --analyze
```

## 🔒 安全注意事项

1. **环境变量安全**
   - 生产环境务必禁用Mock数据
   - 不要在生产环境暴露Mock API密钥
   - 定期更新Mock数据种子

2. **API安全**
   - Mock模式下的API权限验证
   - 防止敏感数据泄露
   - 速率限制和防滥用

3. **数据一致性**
   - Mock数据与真实数据格式对齐
   - 定期更新Mock数据模型
   - 版本控制和变更管理

## 📞 技术支持

### 联系方式
- 项目文档: `/docs/guides/`
- 问题反馈: GitHub Issues
- 技术讨论: 项目Wiki

### 相关资源
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Vue 3官方文档](https://v3.vuejs.org/)
- [Vite配置指南](https://vitejs.dev/config/)

---

## 📝 更新日志

### v1.3.1 (2025-11-13)
- ✅ 完成Mock数据系统完整集成
- ✅ 修复监控摘要API数据格式问题
- ✅ 补充技术分析API缺失字段
- ✅ 优化前端代理配置
- ✅ 实现端到端测试验证

### v1.3.0 (2025-11-12)
- ✅ 创建统一Mock数据管理器
- ✅ 集成问财API Mock数据支持
- ✅ 集成策略管理API Mock数据支持
- ✅ 创建完整测试验证套件

---

*本文档基于MyStocks v1.3.1生成，最后更新: 2025-11-13*