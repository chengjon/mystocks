# API接口对齐清单

## 概述

本文档详细梳理了前端页面使用的API端点与后端实现的对应关系，确保Mock数据与真实数据的一致性。

## 前端主要API端点清单

### 1. 认证相关API

| 前端端点 | 方法 | 功能描述 | 后端实现状态 |
|---------|------|----------|-------------|
| `/auth/login` | POST | 用户登录 | ✅ 已实现 |
| `/auth/logout` | POST | 用户登出 | ✅ 已实现 |
| `/auth/me` | GET | 获取当前用户信息 | ✅ 已实现 |
| `/auth/refresh` | POST | 刷新token | ✅ 已实现 |

### 2. 数据查询API

| 前端端点 | 方法 | 功能描述 | 后端实现状态 | 备注 |
|---------|------|----------|-------------|------|
| `/data/stocks/basic` | GET | 获取股票基本信息 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |
| `/data/stocks/industries` | GET | 获取行业列表 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |
| `/data/stocks/concepts` | GET | 获取概念列表 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |
| `/data/stocks/daily` | GET | 获取日K线数据 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |
| `/data/markets/overview` | GET | 获取市场概览 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |
| `/data/stocks/search` | GET | 股票搜索 | ⚠️ 需要确认 | 前端调用但未找到对应实现 |

### 3. K线图表API

| 前端端点 | 方法 | 功能描述 | 后端实现状态 | 备注 |
|---------|------|----------|-------------|------|
| `/market/kline` | GET | 获取K线数据 | ✅ 已实现 | 在market.py中实现 |

### 4. 股票详情API

| 前端端点 | 方法 | 功能描述 | 后端实现状态 | 备注 |
|---------|------|----------|-------------|------|
| `/data/stocks/{symbol}/detail` | GET | 获取股票详情 | ✅ 已实现 | 在data.py中新增 |
| `/data/stocks/intraday` | GET | 获取分时数据 | ✅ 已实现 | 在data.py中新增 |
| `/data/stocks/{symbol}/trading-summary` | GET | 获取交易摘要 | ✅ 已实现 | 在data.py中新增 |

### 5. 行业概念分析API

| 前端端点 | 方法 | 功能描述 | 后端实现状态 | 备注 |
|---------|------|----------|-------------|------|
| `/analysis/industry/list` | GET | 获取行业列表 | ✅ 已实现 | 在industry_concept_analysis.py中 |
| `/analysis/concept/list` | GET | 获取概念列表 | ✅ 已实现 | 在industry_concept_analysis.py中 |
| `/analysis/industry/stocks` | GET | 获取行业成分股 | ✅ 已实现 | 在industry_concept_analysis.py中 |
| `/analysis/concept/stocks` | GET | 获取概念成分股 | ✅ 已实现 | 在industry_concept_analysis.py中 |
| `/analysis/industry/performance` | GET | 获取行业表现数据 | ✅ 已实现 | 在industry_concept_analysis.py中 |

## 后端实际实现的API端点

### 1. 已确认实现的后端API

#### data.py
- `/api/data/stocks/{symbol}/detail` - 股票详情 ✅
- `/api/data/stocks/intraday` - 分时数据 ✅
- `/api/data/stocks/{symbol}/trading-summary` - 交易摘要 ✅

#### market.py
- `/api/market/kline` - K线数据 ✅
- `/api/market/wencai/` - 问财筛选相关 ✅

#### industry_concept_analysis.py
- `/api/analysis/industry/list` - 行业列表 ✅
- `/api/analysis/concept/list` - 概念列表 ✅
- `/api/analysis/industry/stocks` - 行业成分股 ✅
- `/api/analysis/concept/stocks` - 概念成分股 ✅
- `/api/analysis/industry/performance` - 行业表现数据 ✅

#### 其他已实现的API
- 认证相关API在auth.py中 ✅
- 监控相关API在monitoring.py中 ✅
- 技术分析相关API在technical_analysis.py中 ✅

### 2. 需要补充实现的后端API

| 端点 | 功能描述 | 实现状态 | 优先级 | 备注 |
|------|----------|----------|--------|------|
| `/api/data/stocks/basic` | 股票基本信息 | ❌ 未实现 | 高 | Dashboard和Stocks页面使用 |
| `/api/data/stocks/industries` | 行业列表 | ❌ 未实现 | 中 | Stocks页面筛选使用 |
| `/api/data/stocks/concepts` | 概念列表 | ❌ 未实现 | 中 | Stocks页面筛选使用 |
| `/api/data/stocks/daily` | 日K线数据 | ❌ 未实现 | 高 | 技术分析页面使用 |
| `/api/data/markets/overview` | 市场概览 | ❌ 未实现 | 高 | Dashboard页面使用 |
| `/api/data/stocks/search` | 股票搜索 | ❌ 未实现 | 中 | 通用搜索功能 |

## Mock数据一致性分析

### 1. 当前Mock数据生成方式

前端使用了以下Mock数据生成策略：

1. **API-first策略**: 优先调用真实API，失败时降级到Mock数据
2. **缓存机制**: 使用CacheManager进行前端缓存
3. **随机种子**: 基于symbol生成一致的随机数据

### 2. Mock数据与真实数据结构对齐

需要确保Mock数据字段与真实API返回的字段完全一致：

```javascript
// 示例：股票详情Mock数据结构
const mockStockDetail = {
  symbol: '600000',
  name: '浦发银行',
  price: 12.34,
  change: 0.12,
  change_pct: 0.98,
  industry: '银行',
  concepts: ['人工智能', '5G概念'],
  list_date: '2000-01-01',
  market: 'SH',
  area: '上海'
}
```

## 对齐行动计划

### 第一阶段：API端点补充 (高优先级)

1. **股票基本信息API** (`/api/data/stocks/basic`)
   - 实现股票基本信息查询
   - 支持分页和筛选
   - 确保与前端期望字段一致

2. **日K线数据API** (`/api/data/stocks/daily`)
   - 实现日K线数据查询
   - 支持时间范围查询
   - 确保与`/api/market/kline`格式一致

3. **市场概览API** (`/api/data/markets/overview`)
   - 实现市场概览数据查询
   - 包含主要指数、涨跌统计等

### 第二阶段：筛选相关API (中优先级)

4. **行业列表API** (`/api/data/stocks/industries`)
   - 实现行业列表查询
   - 与`/api/analysis/industry/list`格式对齐

5. **概念列表API** (`/api/data/stocks/concepts`)
   - 实现概念列表查询
   - 与`/api/analysis/concept/list`格式对齐

6. **股票搜索API** (`/api/data/stocks/search`)
   - 实现股票搜索功能
   - 支持代码和名称模糊搜索

### 第三阶段：数据格式统一

7. **响应格式标准化**
   - 统一所有API的响应格式
   - 确保success、data、timestamp字段一致
   - 错误处理格式统一

8. **字段名称标准化**
   - 检查前端期望字段与后端返回字段的一致性
   - 统一字段命名规范（如symbol vs stock_code）

## 实施建议

### 1. 立即行动项
- [ ] 实现`/api/data/stocks/basic`端点
- [ ] 实现`/api/data/markets/overview`端点
- [ ] 检查并对齐现有API的响应格式

### 2. 短期行动项
- [ ] 实现筛选相关API端点
- [ ] 统一字段命名规范
- [ ] 完善Mock数据结构

### 3. 中期行动项
- [ ] 实现双数据源统一封装
- [ ] 优化缓存策略
- [ ] 完善错误处理机制

## 质量保证

### 1. 测试覆盖
- 确保所有API端点都有对应的测试用例
- Mock数据与真实数据的一致性测试
- 前后端接口契约测试

### 2. 文档维护
- 保持API文档的实时更新
- 记录字段变更历史
- 提供版本迁移指南

---

*本文档将根据实际开发进展持续更新*
*最后更新: 2025-11-17*
