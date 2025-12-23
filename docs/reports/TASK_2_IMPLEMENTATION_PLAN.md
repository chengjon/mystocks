# Task 2: TDengine 缓存集成 - 实现计划

**任务**: TDengine 缓存集成
**周期**: Week 2
**优先级**: CRITICAL (P0-架构)
**预计时长**: 3-4 周

---

## 📋 任务概述

搭建 TDengine 时序数据库服务，实现市场数据缓存层，包括：
- TDengine 服务部署（单机/集群）
- 缓存读写逻辑实现
- 时间窗口淘汰策略（7天自动清理）
- 缓存命中率监控（目标≥80%）
- 热点数据识别和预加载

---

## 🎯 子任务分解

### 2.1: 搭建 TDengine 服务 ✏️ 进行中
- **时长**: 1-2 天
- **输出**:
  - Docker 容器配置文件
  - TDengine 单机/集群部署脚本
  - 数据库和表初始化 SQL

**检查清单**:
- [ ] 验证 TDengine 容器正常启动
- [ ] 验证数据库连接
- [ ] 创建缓存表结构

### 2.2: 实现缓存读写逻辑
- **时长**: 2-3 天
- **输出**:
  - CacheManager 类
  - fetch_from_cache() 方法
  - write_to_cache() 方法
  - 缓存更新接口

### 2.3: 时间窗口淘汰策略
- **时长**: 1-2 天
- **输出**:
  - TTL 管理器
  - 7 天自动清理定时任务
  - 访问频率淘汰算法
  - 管理员清理接口

### 2.4: 缓存预热和监控
- **时长**: 2-3 天
- **输出**:
  - 启动时数据预加载逻辑
  - 缓存命中率监控指标
  - 热点数据识别算法
  - 监控仪表板

---

## 💾 数据架构

### 缓存表结构

```sql
-- 市场数据缓存表
CREATE TABLE market_data_cache (
    ts TIMESTAMP,
    symbol VARCHAR(10),
    data_type VARCHAR(20),      -- 'fund_flow', 'etf', 'chip_race', etc.
    timeframe VARCHAR(10),       -- '1d', '3d', '5d', '10d'
    data JSON,                   -- 完整数据
    hit_count BIGINT DEFAULT 0,  -- 命中次数
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (ts, symbol, data_type, timeframe)
) USING SMA;

-- 缓存统计表
CREATE TABLE cache_stats (
    ts TIMESTAMP,
    total_requests BIGINT,
    cache_hits BIGINT,
    cache_misses BIGINT,
    hit_rate FLOAT,
    PRIMARY KEY (ts)
);

-- 热点数据表
CREATE TABLE hot_symbols (
    ts TIMESTAMP,
    symbol VARCHAR(10),
    access_count BIGINT,
    last_access TIMESTAMP,
    PRIMARY KEY (ts, symbol)
);
```

---

## 🏗️ 实现路线

### Phase 1: 基础设施 (Week 2)
1. TDengine 部署和初始化
2. 缓存表创建和管理
3. 基础读写接口

### Phase 2: 高级功能 (Week 3)
1. 淘汰策略实现
2. 性能优化
3. 监控集成

### Phase 3: 优化和验证 (Week 3-4)
1. 缓存命中率优化
2. 压力测试
3. 生产部署

---

## 🔧 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 数据库 | TDengine | 3.x |
| 驱动 | taospy | Latest |
| 缓存策略 | LRU + TTL | Custom |
| 监控 | Prometheus | Latest |

---

## 📊 成功指标

- ✅ TDengine 服务正常运行
- ✅ 缓存命中率 ≥ 80%
- ✅ 单次查询 < 100ms
- ✅ 自动淘汰正常工作
- ✅ 监控告警配置完成

---

## 🚀 开始实现

**下一步**: 搭建 TDengine 容器环境

Generated: 2025-11-06
