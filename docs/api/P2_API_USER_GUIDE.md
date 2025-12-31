# P2 API 使用指南

**版本**: v1.0
**最后更新**: 2025-12-31
**API版本**: v2.0.0

---

## 📋 目录

1. [API概览](#api概览)
2. [快速开始](#快速开始)
3. [技术指标API (Indicators)](#技术指标api-indicators)
4. [公告监控API (Announcement)](#公告监控api-announcement)
5. [系统管理API (System)](#系统管理api-system)
6. [认证和授权](#认证和授权)
7. [速率限制](#速率限制)
8. [错误处理](#错误处理)
9. [最佳实践](#最佳实践)
10. [SDK和工具](#sdk和工具)

---

## API概览

### P2 API分类

MyStocks P2 API 提供辅助功能和管理接口,包括:

| 模块 | 端点数 | 功能描述 |
|------|--------|----------|
| **Indicators** | 11 | 技术指标计算、缓存管理、配置管理 |
| **Announcement** | 13 | 公告抓取、监控规则、重要性分级 |
| **System** | 29 | 系统健康检查、监控管理、日志查询 |
| **总计** | **53** | - |

### API优先级说明

- **P0 API**: 核心业务API (47个) - 市场数据、实时行情等
- **P1 API**: 重要功能API (85个) - 回测、风控、用户管理等 (待完成)
- **P2 API**: 辅助功能API (53个) - 技术指标、系统管理等

### 基础URL

```
开发环境: http://localhost:8000
生产环境: https://api.mystocks.com
```

---

## 快速开始

### 1. 访问API文档

启动服务后,访问以下地址查看完整的交互式API文档:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 2. 健康检查

```bash
curl http://localhost:8000/api/indicators/health
curl http://localhost:8000/api/announcement/health
curl http://localhost:8000/api/system/health
```

### 3. 简单API调用示例

#### 获取指标注册表

```bash
curl -X GET "http://localhost:8000/api/indicators/registry" \
  -H "accept: application/json"
```

#### 获取系统架构信息

```bash
curl -X GET "http://localhost:8000/api/system/architecture" \
  -H "accept: application/json"
```

#### 获取今日公告

```bash
curl -X GET "http://localhost:8000/api/announcement/today" \
  -H "accept: application/json"
```

---

## 技术指标API (Indicators)

### 模块概览

技术指标模块提供50+种技术指标的计算和批量处理功能。

**基础路径**: `/api/indicators`

**主要功能**:
- ✅ 单个/批量指标计算
- ✅ 指标配置管理 (CRUD)
- ✅ 缓存统计和清理
- ✅ 智能缓存机制 (TTL: 1小时)

**性能特性**:
- 🚀 速率限制: 60次/分钟
- 🚀 批量并发: 最多3个
- 🚀 缓存优化: 自动缓存常用计算

**计算引擎**: pandas_ta, talib

---

### 1. 获取指标注册表

获取所有可用技术指标的注册表信息。

**端点**: `GET /api/indicators/registry`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/registry" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取指标注册表成功",
  "data": {
    "trend": {
      "SMA": {
        "name": "简单移动平均",
        "description": "计算简单移动平均线",
        "parameters": ["period", "price"],
        "default_period": 20
      },
      "EMA": {
        "name": "指数移动平均",
        "description": "计算指数移动平均线",
        "parameters": ["period", "price"],
        "default_period": 20
      },
      "MACD": {
        "name": "MACD指标",
        "description": "移动平均收敛散度",
        "parameters": ["fast", "slow", "signal"],
        "default": [12, 26, 9]
      }
    },
    "momentum": {
      "RSI": {
        "name": "相对强弱指标",
        "description": "计算RSI指标",
        "parameters": ["period"],
        "default_period": 14
      }
    }
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 2. 获取指定分类的指标

获取特定分类的指标列表。

**端点**: `GET /api/indicators/registry/{category}`

**路径参数**:
- `category` (string): 指标分类
  - 可选值: `trend`, `momentum`, `volatility`, `volume`

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/registry/trend" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取趋势指标成功",
  "data": {
    "SMA": {...},
    "EMA": {...},
    "MACD": {...}
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 3. 计算技术指标

计算单个技术指标。

**端点**: `POST /api/indicators/calculate`

**认证**: 不需要

**请求体**:
```json
{
  "symbol": "000001.SZ",
  "indicator": "MACD",
  "period": 20,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/indicators/calculate" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001.SZ",
    "indicator": "MACD",
    "period": 20,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "指标计算成功",
  "data": {
    "symbol": "000001.SZ",
    "indicator": "MACD",
    "result": [
      {
        "date": "2025-01-01",
        "macd": 0.523,
        "signal": 0.498,
        "histogram": 0.025
      }
    ]
  },
  "cached": false,
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 4. 批量计算技术指标

批量计算多个技术指标。

**端点**: `POST /api/indicators/calculate/batch`

**认证**: 不需要

**请求体**:
```json
{
  "symbol": "000001.SZ",
  "indicators": ["SMA", "EMA", "RSI", "MACD"],
  "period": 20,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/indicators/calculate/batch" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001.SZ",
    "indicators": ["SMA", "EMA", "RSI", "MACD"],
    "period": 20,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "批量指标计算成功",
  "data": {
    "symbol": "000001.SZ",
    "results": {
      "SMA": {...},
      "EMA": {...},
      "RSI": {...},
      "MACD": {...}
    }
  },
  "cached": false,
  "timestamp": "2025-12-31T12:00:00Z"
}
```

**性能说明**:
- 最多支持3个并发计算
- 自动使用缓存优化重复计算
- 速率限制: 60次/分钟

---

### 5. 缓存统计

获取指标计算的缓存统计信息。

**端点**: `GET /api/indicators/cache/stats`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/cache/stats" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取缓存统计成功",
  "data": {
    "total_keys": 1523,
    "hit_rate": 0.85,
    "miss_rate": 0.15,
    "memory_usage": "45.2 MB",
    "ttl": 3600
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 6. 清理缓存

清理指标计算的缓存。

**端点**: `POST /api/indicators/cache/clear`

**认证**: 不需要

**请求体** (可选):
```json
{
  "pattern": "MACD_*"
}
```

**请求示例**:
```bash
# 清理所有缓存
curl -X POST "http://localhost:8000/api/indicators/cache/clear" \
  -H "accept: application/json"

# 清理特定模式缓存
curl -X POST "http://localhost:8000/api/indicators/cache/clear" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "MACD_*"}'
```

**响应示例**:
```json
{
  "success": true,
  "message": "缓存清理成功",
  "data": {
    "cleared_keys": 345
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 7. 指标配置管理

#### 创建指标配置

**端点**: `POST /api/indicators/configs`

**认证**: 需要

**请求体**:
```json
{
  "name": "我的MACD策略",
  "indicator": "MACD",
  "parameters": {
    "fast": 12,
    "slow": 26,
    "signal": 9
  },
  "description": "短期MACD策略"
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/indicators/configs" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "我的MACD策略",
    "indicator": "MACD",
    "parameters": {
      "fast": 12,
      "slow": 26,
      "signal": 9
    },
    "description": "短期MACD策略"
  }'
```

#### 获取配置列表

**端点**: `GET /api/indicators/configs`

**认证**: 需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/configs" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 获取配置详情

**端点**: `GET /api/indicators/configs/{config_id}`

**认证**: 需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/configs/123" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 更新配置

**端点**: `PUT /api/indicators/configs/{config_id}`

**认证**: 需要

**请求示例**:
```bash
curl -X PUT "http://localhost:8000/api/indicators/configs/123" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "更新的MACD策略",
    "parameters": {
      "fast": 5,
      "slow": 34,
      "signal": 5
    }
  }'
```

#### 删除配置

**端点**: `DELETE /api/indicators/configs/{config_id}`

**认证**: 需要

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/api/indicators/configs/123" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 公告监控API (Announcement)

### 模块概览

公告监控模块提供上市公司公告的抓取、解析和监控功能。

**基础路径**: `/api/announcement`

**主要功能**:
- ✅ 公告数据抓取和存储
- ✅ 智能重要性分级 (0-5级)
- ✅ 监控规则管理 (CRUD)
- ✅ 触发记录追踪
- ✅ AI分析集成 (待实现)

**监控特性**:
- 🔍 关键词匹配
- 🔍 重要性过滤
- 🔍 股票黑白名单
- 🔍 多渠道通知

---

### 1. 健康检查

检查公告服务健康状态。

**端点**: `GET /api/announcement/health`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/announcement/health" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "服务健康",
  "data": {
    "status": "healthy",
    "database": "connected",
    "last_fetch": "2025-12-31T12:00:00Z"
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 2. 获取服务状态

获取公告服务的详细状态信息。

**端点**: `GET /api/announcement/status`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/announcement/status" \
  -H "accept: application/json"
```

---

### 3. AI分析数据

对公告数据进行AI分析。

**端点**: `POST /api/announcement/analyze`

**认证**: 不需要

**请求体**:
```json
{
  "announcement_id": "123456"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "AI分析完成",
  "data": {
    "sentiment": "positive",
    "importance": 4,
    "summary": "公司发布业绩预增公告..."
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

**注意**: 此功能待实现。

---

### 4. 获取并保存公告

手动触发公告数据抓取和保存。

**端点**: `POST /api/announcement/fetch`

**认证**: 不需要

**请求体** (可选):
```json
{
  "symbol": "000001.SZ",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

**请求示例**:
```bash
# 抓取所有公告
curl -X POST "http://localhost:8000/api/announcement/fetch" \
  -H "accept: application/json"

# 抓取特定股票公告
curl -X POST "http://localhost:8000/api/announcement/fetch" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001.SZ",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

---

### 5. 查询公告列表

查询公告列表,支持多种过滤条件。

**端点**: `GET /api/announcement/list`

**认证**: 不需要

**查询参数**:
- `symbol` (string, 可选): 股票代码
- `start_date` (string, 可选): 开始日期
- `end_date` (string, 可选): 结束日期
- `importance` (integer, 可选): 重要性级别 (0-5)
- `category` (string, 可选): 公告分类
- `page` (integer, 可选): 页码,默认1
- `page_size` (integer, 可选): 每页数量,默认20

**请求示例**:
```bash
# 查询所有公告
curl -X GET "http://localhost:8000/api/announcement/list" \
  -H "accept: application/json"

# 查询特定股票的重要公告
curl -X GET "http://localhost:8000/api/announcement/list?symbol=000001.SZ&importance=4" \
  -H "accept: application/json"

# 分页查询
curl -X GET "http://localhost:8000/api/announcement/list?page=1&page_size=10" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "total": 1523,
    "page": 1,
    "page_size": 20,
    "announcements": [
      {
        "id": "123456",
        "symbol": "000001.SZ",
        "title": "2024年年度报告",
        "publish_date": "2025-01-15",
        "importance": 5,
        "category": "定期报告"
      }
    ]
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 6. 获取今日公告

获取今日发布的公告列表。

**端点**: `GET /api/announcement/today`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/announcement/today" \
  -H "accept: application/json"
```

---

### 7. 获取重要公告

获取重要级别(4-5级)的公告列表。

**端点**: `GET /api/announcement/important`

**认证**: 不需要

**查询参数**:
- `symbol` (string, 可选): 股票代码
- `days` (integer, 可选): 最近天数,默认7天

**请求示例**:
```bash
# 获取最近7天所有重要公告
curl -X GET "http://localhost:8000/api/announcement/important" \
  -H "accept: application/json"

# 获取特定股票的重要公告
curl -X GET "http://localhost:8000/api/announcement/important?symbol=000001.SZ&days=30" \
  -H "accept: application/json"
```

---

### 8. 获取公告统计

获取公告数据统计信息。

**端点**: `GET /api/announcement/stats`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/announcement/stats" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取统计成功",
  "data": {
    "total_announcements": 15234,
    "today_count": 45,
    "important_count": 234,
    "by_category": {
      "定期报告": 1234,
      "临时公告": 8900,
      "股东变动": 2100
    }
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 9. 监控规则管理

#### 获取监控规则列表

**端点**: `GET /api/announcement/monitor-rules`

**认证**: 需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/announcement/monitor-rules" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 创建监控规则

**端点**: `POST /api/announcement/monitor-rules`

**认证**: 需要

**请求体**:
```json
{
  "name": "重要公告监控",
  "keywords": ["业绩预增", "重大资产重组"],
  "importance_threshold": 4,
  "symbols": ["000001.SZ", "000002.SZ"],
  "notification_enabled": true
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/announcement/monitor-rules" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "重要公告监控",
    "keywords": ["业绩预增", "重大资产重组"],
    "importance_threshold": 4,
    "symbols": ["000001.SZ", "000002.SZ"],
    "notification_enabled": true
  }'
```

#### 更新监控规则

**端点**: `PUT /api/announcement/monitor-rules/{rule_id}`

**认证**: 需要

**请求示例**:
```bash
curl -X PUT "http://localhost:8000/api/announcement/monitor-rules/123" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "keywords": ["业绩预增", "重大资产重组", "分红派息"],
    "importance_threshold": 5
  }'
```

#### 删除监控规则

**端点**: `DELETE /api/announcement/monitor-rules/{rule_id}`

**认证**: 需要

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/api/announcement/monitor-rules/123" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 10. 获取触发记录

获取监控规则的触发记录列表。

**端点**: `GET /api/announcement/triggered-records`

**认证**: 需要

**查询参数**:
- `rule_id` (integer, 可选): 规则ID
- `symbol` (string, 可选): 股票代码
- `start_date` (string, 可选): 开始日期
- `end_date` (string, 可选): 结束日期

**请求示例**:
```bash
# 获取所有触发记录
curl -X GET "http://localhost:8000/api/announcement/triggered-records" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取特定规则的触发记录
curl -X GET "http://localhost:8000/api/announcement/triggered-records?rule_id=123" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 系统管理API (System)

### 模块概览

系统管理模块提供系统级管理、监控和配置功能。

**基础路径**: `/api/system`, `/api/health`, `/api/monitoring`

**主要功能**:
- ✅ 双数据库架构监控 (TDengine + PostgreSQL)
- ✅ LGTM Stack集成 (Loki, Grafana, Tempo, Prometheus)
- ✅ 实时告警规则管理
- ✅ 系统日志查询和分析
- ✅ 数据库连接测试

**监控指标**:
- 📊 40+ Prometheus指标
- 📊 实时性能数据
- 📊 数据质量评分
- 📊 缓存命中率

---

### 1. 系统健康检查

#### 基础健康检查

**端点**: `GET /api/health` 或 `GET /api/system/health`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/health" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "系统健康",
  "data": {
    "status": "healthy",
    "version": "2.0.0",
    "uptime": 86400
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

#### 详细健康检查

**端点**: `GET /api/health/detailed`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/health/detailed" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "系统健康",
  "data": {
    "status": "healthy",
    "components": {
      "api": "healthy",
      "tdengine": "healthy",
      "postgresql": "healthy",
      "redis": "disabled"
    },
    "version": "2.0.0"
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

#### 获取历史健康报告

**端点**: `GET /api/health/reports/{timestamp}`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/health/reports/20251231_120000" \
  -H "accept: application/json"
```

---

### 2. 适配器健康检查

检查所有数据源适配器的健康状态。

**端点**: `GET /api/system/adapters/health`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/adapters/health" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "适配器健康检查完成",
  "data": {
    "akshare": {
      "status": "healthy",
      "last_check": "2025-12-31T12:00:00Z"
    },
    "baostock": {
      "status": "healthy",
      "last_check": "2025-12-31T12:00:00Z"
    },
    "tushare": {
      "status": "disabled",
      "reason": "未配置token"
    }
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 3. 数据源管理

#### 获取数据源列表

**端点**: `GET /api/system/datasources`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/datasources" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取数据源列表成功",
  "data": {
    "sources": [
      {
        "name": "akshare",
        "enabled": true,
        "priority": 1
      },
      {
        "name": "baostock",
        "enabled": true,
        "priority": 2
      }
    ]
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

#### 测试数据库连接

**端点**: `POST /api/system/test-connection`

**认证**: 不需要

**请求体**:
```json
{
  "database_type": "tdengine"
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/system/test-connection" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "database_type": "tdengine"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "连接测试成功",
  "data": {
    "database": "tdengine",
    "status": "connected",
    "latency_ms": 5.2
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 4. 日志管理

#### 查询系统日志

**端点**: `GET /api/system/logs`

**认证**: 不需要

**查询参数**:
- `level` (string, 可选): 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `start_time` (string, 可选): 开始时间
- `end_time` (string, 可选): 结束时间
- `limit` (integer, 可选): 返回数量,默认100

**请求示例**:
```bash
# 查询最近的ERROR日志
curl -X GET "http://localhost:8000/api/system/logs?level=ERROR&limit=50" \
  -H "accept: application/json"

# 查询特定时间范围的日志
curl -X GET "http://localhost:8000/api/system/logs?start_time=2025-01-01&end_time=2025-12-31" \
  -H "accept: application/json"
```

#### 获取日志统计摘要

**端点**: `GET /api/system/logs/summary`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/logs/summary" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取日志摘要成功",
  "data": {
    "total_logs": 15234,
    "by_level": {
      "DEBUG": 8900,
      "INFO": 5234,
      "WARNING": 890,
      "ERROR": 210
    },
    "recent_errors": [
      {
        "timestamp": "2025-12-31T12:00:00Z",
        "level": "ERROR",
        "message": "Database connection failed"
      }
    ]
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 5. 系统架构信息

获取系统架构和数据源配置信息。

**端点**: `GET /api/system/architecture`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/architecture" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取架构信息成功",
  "data": {
    "architecture": "dual-database",
    "databases": {
      "tdengine": {
        "purpose": "高频时序数据",
        "tables": ["tick_data", "minute_data"]
      },
      "postgresql": {
        "purpose": "通用数据存储",
        "extensions": ["TimescaleDB"]
      }
    },
    "adapters": ["akshare", "baostock", "tushare"],
    "monitoring": "LGTM Stack"
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 6. 数据库健康和统计

#### 数据库健康检查

**端点**: `GET /api/system/database/health`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/database/health" \
  -H "accept: application/json"
```

#### 数据库统计信息

**端点**: `GET /api/system/database/stats`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/database/stats" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取数据库统计成功",
  "data": {
    "tdengine": {
      "tables": 25,
      "total_records": 152345678,
      "compression_ratio": "20:1"
    },
    "postgresql": {
      "tables": 45,
      "total_records": 892345,
      "size_mb": 5120
    }
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

### 7. 监控管理

#### 告警规则管理

**获取告警规则列表**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/alert-rules" \
  -H "accept: application/json"
```

**创建告警规则**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/alert-rules" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "数据库连接告警",
    "metric": "database_connection_failed",
    "threshold": 5,
    "window_minutes": 5
  }'
```

**更新告警规则**:
```bash
curl -X PUT "http://localhost:8000/api/monitoring/alert-rules/123" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"threshold": 10}'
```

**删除告警规则**:
```bash
curl -X DELETE "http://localhost:8000/api/monitoring/alert-rules/123" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 查询告警记录

**端点**: `GET /api/monitoring/alerts`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/alerts" \
  -H "accept: application/json"
```

#### 标记告警为已读

**端点**: `POST /api/monitoring/alerts/{alert_id}/mark-read`

**认证**: 需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/alerts/123/mark-read" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 批量标记所有告警为已读

**端点**: `POST /api/monitoring/alerts/mark-all-read`

**认证**: 需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/alerts/mark-all-read" \
  -H "accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 8. 实时监控

#### 获取实时监控数据

**端点**: `GET /api/monitoring/realtime`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/realtime" \
  -H "accept: application/json"
```

#### 获取单只股票的实时监控数据

**端点**: `GET /api/monitoring/realtime/{symbol}`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/realtime/000001.SZ" \
  -H "accept: application/json"
```

#### 手动触发获取实时数据

**端点**: `POST /api/monitoring/realtime/fetch`

**认证**: 不需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/realtime/fetch" \
  -H "accept: application/json"
```

---

### 9. 龙虎榜监控

#### 获取龙虎榜数据

**端点**: `GET /api/monitoring/dragon-tiger`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/dragon-tiger" \
  -H "accept: application/json"
```

#### 手动触发获取龙虎榜数据

**端点**: `POST /api/monitoring/dragon-tiger/fetch`

**认证**: 不需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/dragon-tiger/fetch" \
  -H "accept: application/json"
```

---

### 10. 监控统计

#### 获取监控系统摘要

**端点**: `GET /api/monitoring/summary`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/summary" \
  -H "accept: application/json"
```

#### 获取今日统计数据

**端点**: `GET /api/monitoring/stats/today`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/stats/today" \
  -H "accept: application/json"
```

---

### 11. 监控控制

#### 启动监控

**端点**: `POST /api/monitoring/control/start`

**认证**: 不需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/control/start" \
  -H "accept: application/json"
```

#### 停止监控

**端点**: `POST /api/monitoring/control/stop`

**认证**: 不需要

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/monitoring/control/stop" \
  -H "accept: application/json"
```

#### 获取监控状态

**端点**: `GET /api/monitoring/control/status`

**认证**: 不需要

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/monitoring/control/status" \
  -H "accept: application/json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取监控状态成功",
  "data": {
    "status": "running",
    "uptime_seconds": 3600,
    "last_update": "2025-12-31T12:00:00Z"
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

---

## 认证和授权

### JWT Token认证

部分P2 API需要JWT Token认证。需要认证的API包括:
- 指标配置管理 (POST/PUT/DELETE)
- 监控规则管理 (POST/PUT/DELETE)
- 部分系统管理操作

#### 获取Token

1. 通过登录接口获取Token (参见认证API文档)
2. Token有效期为24小时

#### 使用Token

在请求头中添加Authorization字段:

```bash
curl -X POST "http://localhost:8000/api/indicators/configs" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### CSRF保护

所有修改操作(POST/PUT/DELETE)需要CSRF Token保护。

**请求头**:
```
X-CSRF-Token: YOUR_CSRF_TOKEN
```

**完整示例**:
```bash
curl -X POST "http://localhost:8000/api/indicators/configs" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-CSRF-Token: YOUR_CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 速率限制

### 默认速率限制

- **P2 API速率限制**: 60次/分钟
- **批量计算限制**: 最多3个并发

### 速率限制响应头

当触发速率限制时,响应头会包含以下信息:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```

### 429 Too Many Requests

当超过速率限制时,API会返回HTTP 429状态码:

```json
{
  "success": false,
  "message": "速率限制超出",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "data": {
    "retry_after": 30
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

**建议**:
- 实现指数退避重试策略
- 使用缓存减少重复请求
- 批量操作时合理控制并发数

---

## 错误处理

### 标准错误响应格式

所有API错误响应遵循统一格式:

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "错误字段",
    "reason": "错误原因"
  },
  "timestamp": "2025-12-31T12:00:00Z"
}
```

### 常见HTTP状态码

| 状态码 | 说明 | 示例场景 |
|--------|------|----------|
| 200 | 请求成功 | 成功获取数据 |
| 201 | 创建成功 | 成功创建配置 |
| 204 | 删除成功 | 成功删除资源 |
| 400 | 请求参数错误 | 缺少必需参数 |
| 401 | 未授权 | Token无效或缺失 |
| 403 | 禁止访问 | CSRF Token无效 |
| 404 | 资源不存在 | 配置ID不存在 |
| 422 | 数据验证失败 | Pydantic验证错误 |
| 429 | 速率限制超出 | 超过60次/分钟 |
| 500 | 服务器内部错误 | 数据库连接失败 |

### 错误码列表

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| INVALID_PARAMETER | 参数验证失败 | 检查请求参数格式 |
| UNAUTHORIZED | 未授权访问 | 检查JWT Token |
| FORBIDDEN | 禁止访问 | 检查CSRF Token |
| RESOURCE_NOT_FOUND | 资源不存在 | 检查资源ID |
| VALIDATION_ERROR | 数据验证失败 | 检查请求体结构 |
| RATE_LIMIT_EXCEEDED | 速率限制超出 | 等待后重试 |
| INTERNAL_ERROR | 内部错误 | 联系技术支持 |

### 错误处理最佳实践

1. **始终检查success字段**:
```python
response = requests.get("http://localhost:8000/api/indicators/registry")
data = response.json()

if not data.get("success"):
    print(f"错误: {data.get('message')}")
    print(f"错误码: {data.get('error_code')}")
    # 处理错误
else:
    # 处理成功响应
    pass
```

2. **实现指数退避重试**:
```python
import time

def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            # 速率限制,等待后重试
            retry_after = response.json().get("data", {}).get("retry_after", 30)
            time.sleep(retry_after)
            continue

        if response.status_code >= 500:
            # 服务器错误,指数退避
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            continue

        return response.json()

    raise Exception("Max retries exceeded")
```

3. **记录错误日志**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    response = requests.get("http://localhost:8000/api/indicators/registry")
    data = response.json()

    if not data.get("success"):
        logger.error(f"API错误: {data.get('error_code')} - {data.get('message')}")
        logger.error(f"详情: {data.get('details')}")

except Exception as e:
    logger.exception(f"请求失败: {str(e)}")
```

---

## 最佳实践

### 1. 缓存策略

#### 利用指标计算缓存

```python
# 首次计算会缓存结果
response = requests.post("http://localhost:8000/api/indicators/calculate", json={
    "symbol": "000001.SZ",
    "indicator": "MACD",
    "period": 20,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
})

# 后续相同请求会返回缓存结果 (cached: true)
# TTL: 1小时
```

#### 批量计算优化

```python
# ✅ 推荐: 批量计算多个指标
response = requests.post("http://localhost:8000/api/indicators/calculate/batch", json={
    "symbol": "000001.SZ",
    "indicators": ["SMA", "EMA", "RSI", "MACD"],  # 一次计算4个指标
    "period": 20
})

# ❌ 不推荐: 多次单独计算
for indicator in ["SMA", "EMA", "RSI", "MACD"]:
    requests.post("http://localhost:8000/api/indicators/calculate", json={
        "symbol": "000001.SZ",
        "indicator": indicator,
        "period": 20
    })
```

---

### 2. 监控和告警

#### 配置告警规则

```bash
# 创建数据库连接告警规则
curl -X POST "http://localhost:8000/api/monitoring/alert-rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "数据库连接告警",
    "metric": "database_connection_failed",
    "threshold": 5,
    "window_minutes": 5,
    "notification_enabled": true
  }'
```

#### 查询告警记录

```python
# 定期检查新告警
response = requests.get("http://localhost:8000/api/monitoring/alerts")
data = response.json()

if data.get("success"):
    alerts = data["data"]["alerts"]
    unread_alerts = [a for a in alerts if not a["read"]]

    if unread_alerts:
        # 处理未读告警
        for alert in unread_alerts:
            print(f"告警: {alert['message']}")
```

---

### 3. 日志查询优化

#### 使用过滤条件

```bash
# ❌ 不推荐: 获取所有日志
curl "http://localhost:8000/api/system/logs?limit=10000"

# ✅ 推荐: 使用时间范围和级别过滤
curl "http://localhost:8000/api/system/logs?level=ERROR&start_time=2025-01-01&limit=100"
```

#### 定期获取日志摘要

```python
# 定期获取日志摘要,而不是完整日志
response = requests.get("http://localhost:8000/api/system/logs/summary")
data = response.json()

if data.get("success"):
    summary = data["data"]
    error_count = summary["by_level"]["ERROR"]
    recent_errors = summary["recent_errors"]

    print(f"错误数量: {error_count}")
    print(f"最近的错误: {recent_errors}")
```

---

### 4. 性能优化

#### 使用连接池

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

# 配置重试策略
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,
    pool_maxsize=20
)

session.mount("http://", adapter)
session.mount("https://", adapter)

# 使用session发送请求
response = session.get("http://localhost:8000/api/indicators/registry")
```

#### 异步请求

```python
import asyncio
import aiohttp

async def fetch_indicator(session, indicator):
    async with session.get(
        f"http://localhost:8000/api/indicators/registry/{indicator}"
    ) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_indicator(session, "trend"),
            fetch_indicator(session, "momentum"),
            fetch_indicator(session, "volatility")
        ]
        results = await asyncio.gather(*tasks)
        return results

# 运行异步请求
results = asyncio.run(main())
```

---

### 5. 安全实践

#### 保护Token

```python
import os
from dotenv import load_dotenv

# 从环境变量加载Token
load_dotenv()
JWT_TOKEN = os.getenv("MYSTOCKS_JWT_TOKEN")

# 使用Token
response = requests.get(
    "http://localhost:8000/api/indicators/configs",
    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
)
```

#### 验证SSL证书 (生产环境)

```python
# 开发环境: 关闭SSL验证
response = requests.get("http://localhost:8000/api/health", verify=False)

# 生产环境: 启用SSL验证
response = requests.get("https://api.mystocks.com/api/health", verify=True)
```

---

## SDK和工具

### Python SDK

#### 安装

```bash
pip install mystocks-sdk
```

#### 使用示例

```python
from mystocks import MyStocksClient

# 初始化客户端
client = MyStocksClient(
    base_url="http://localhost:8000",
    jwt_token="YOUR_JWT_TOKEN"
)

# 技术指标API
registry = client.indicators.get_registry()
result = client.indicators.calculate(
    symbol="000001.SZ",
    indicator="MACD",
    period=20
)

# 公告监控API
announcements = client.announcement.list(
    symbol="000001.SZ",
    importance=4
)

# 系统管理API
health = client.system.get_health()
logs = client.system.get_logs(level="ERROR", limit=50)
```

---

### cURL脚本

#### 批量计算脚本

```bash
#!/bin/bash

# batch_calculate_indicators.sh

SYMBOLS=("000001.SZ" "000002.SZ" "600000.SH")
INDICATORS=("SMA" "EMA" "RSI" "MACD")

for symbol in "${SYMBOLS[@]}"; do
    for indicator in "${INDICATORS[@]}"; do
        echo "计算 $symbol 的 $indicator 指标..."
        curl -X POST "http://localhost:8000/api/indicators/calculate" \
          -H "Content-Type: application/json" \
          -d "{
            \"symbol\": \"$symbol\",
            \"indicator\": \"$indicator\",
            \"period\": 20,
            \"start_date\": \"2025-01-01\",
            \"end_date\": \"2025-12-31\"
          }"
        echo ""
    done
done
```

---

### JavaScript/TypeScript SDK

#### 安装

```bash
npm install @mystocks/sdk
```

#### 使用示例

```typescript
import { MyStocksClient } from '@mystocks/sdk';

const client = new MyStocksClient({
  baseURL: 'http://localhost:8000',
  jwtToken: 'YOUR_JWT_TOKEN'
});

// 技术指标API
const registry = await client.indicators.getRegistry();
const result = await client.indicators.calculate({
  symbol: '000001.SZ',
  indicator: 'MACD',
  period: 20
});

// 公告监控API
const announcements = await client.announcement.list({
  symbol: '000001.SZ',
  importance: 4
});

// 系统管理API
const health = await client.system.getHealth();
```

---

## 附录

### A. API契约文件

所有P2 API契约文件位于:
```
contracts/p2/
├── indicators/
│   ├── p2_indicators_01_get_api_indicators_registry.yaml
│   ├── ... (11 files)
├── announcement/
│   ├── p2_announcement_01_get_api_announcement_health.yaml
│   ├── ... (13 files)
├── system/
│   ├── p2_system_01_get_api_system_health.yaml
│   ├── ... (29 files)
└── index.yaml
```

### B. 相关文档

- **P2 API扫描报告**: `docs/api/P2_API_SCAN_REPORT.md`
- **T4.1完成报告**: `docs/api/T4.1_COMPLETION_REPORT.md`
- **API契约模板**: `contracts/CONTRACT_TEMPLATE.md`

### C. 支持和反馈

- **GitHub Issues**: https://github.com/your-repo/issues
- **技术支持**: api@mystocks.com
- **文档**: http://localhost:8000/docs

---

**文档版本**: v1.0
**最后更新**: 2025-12-31
**维护者**: Backend CLI (Claude Code)

**总结**: 本文档提供了P2 API的完整使用指南,包括53个API端点的详细说明、请求响应示例、认证授权、错误处理和最佳实践。
