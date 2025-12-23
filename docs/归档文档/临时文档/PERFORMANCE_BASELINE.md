# MyStocks 性能基准报告

## 概述

本文档定义了MyStocks量化交易数据管理系统的性能基准标准、测试方法和验收标准。确保系统在生产环境中达到预期的性能水平。

## 性能基准标准

### 核心性能指标

| 性能指标 | 标准值 | 测量方法 | 备注 |
|---------|--------|----------|------|
| **页面加载时间** | ≤ 1.5秒 | 从请求发送到页面完全渲染 | 包括静态资源加载 |
| **API响应时间** | ≤ 500ms | API端点到响应返回 | 不含网络延迟 |
| **数据库查询时间** | ≤ 2秒 | SQL执行到结果返回 | 复杂查询 ≤ 5秒 |
| **数据同步服务** | ≤ 30分钟 | 5000只股票完整同步 | 增量同步 ≤ 5分钟 |
| **缓存命中率** | ≥ 85% | 缓存命中次数/总请求 | 应用层缓存 |
| **并发处理能力** | ≥ 1000 QPS | 压力测试结果 | 峰值负载 |
| **内存使用率** | ≤ 80% | 运行时内存占用 | 避免内存泄漏 |
| **CPU使用率** | ≤ 70% | 正常运行负载 | 峰值 ≤ 90% |

### 页面级性能标准

| 页面 | 加载时间标准 | 交互响应时间 | 数据更新频率 |
|------|-------------|-------------|-------------|
| 仪表盘页面 | ≤ 1.5秒 | ≤ 200ms | 实时更新 |
| 股票列表页面 | ≤ 2.0秒 | ≤ 300ms | 按需更新 |
| 股票详情页面 | ≤ 2.5秒 | ≤ 300ms | 按需更新 |
| 技术分析页面 | ≤ 3.0秒 | ≤ 500ms | 按需更新 |
| 行业概念分析页面 | ≤ 2.5秒 | ≤ 400ms | 按需更新 |

### API性能标准

| API类别 | 响应时间标准 | 并发处理 | 备注 |
|---------|-------------|----------|------|
| 数据查询API | ≤ 500ms | 500 QPS | 分页查询 ≤ 1秒 |
| 技术指标API | ≤ 1秒 | 200 QPS | 复杂计算 ≤ 3秒 |
| 行业概念API | ≤ 800ms | 300 QPS | 列表查询 ≤ 1.5秒 |
| 监控健康API | ≤ 100ms | 1000 QPS | 心跳检查 |
| 搜索API | ≤ 800ms | 400 QPS | 模糊搜索 ≤ 1.5秒 |

## 测试环境配置

### 硬件配置

```
生产环境推荐配置:
- CPU: 8核心以上 (Intel Xeon或AMD EPYC)
- 内存: 32GB以上
- 存储: SSD 500GB以上 (NVMe推荐)
- 网络: 千兆网络
- GPU: RTX 3080以上 (可选，用于GPU加速)

测试环境最低配置:
- CPU: 4核心
- 内存: 16GB
- 存储: SSD 256GB
- 网络: 百兆网络
```

### 软件环境

```
操作系统: Ubuntu 20.04 LTS / CentOS 8
数据库: PostgreSQL 17.x + TimescaleDB
时序数据库: TDengine 3.3.x
Web服务: Nginx + PM2
Python: 3.12+
Node.js: 18.x+
Redis: 6.x+ (可选)
```

## 测试方法

### 性能测试工具

```bash
# 前端性能测试
- 浏览器开发者工具 (Lighthouse)
- WebPageTest.org
- Google PageSpeed Insights

# API性能测试  
- Apache Bench (ab)
- wrk (现代HTTP基准测试工具)
- curl (简单延迟测试)

# 数据库性能测试
- pgbench (PostgreSQL基准)
- sysbench (综合基准测试)
- 自定义Python测试脚本

# 压力测试
- JMeter
- Locust
- 自定义并发测试脚本
```

### 测试场景设计

#### 1. 页面加载性能测试

```bash
# 使用curl测试页面加载时间
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:3000/"

# curl-format.txt内容:
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

#### 2. API响应性能测试

```bash
# 使用ab进行API压力测试
ab -n 1000 -c 10 http://localhost:8888/api/data/stocks/basic

# 使用wrk进行现代HTTP测试
wrk -t12 -c400 -d30s http://localhost:8888/api/monitoring/health
```

#### 3. 数据库性能测试

```bash
# PostgreSQL基准测试
pgbench -i -s 100 mystocks
pgbench -c 10 -j 4 -T 60 mystocks

# 自定义查询性能测试
python3 scripts/automation/performance_test.py --test-type database
```

### 性能监控指标

#### 实时监控指标

```python
# 系统资源监控
{
    "cpu_usage": "当前CPU使用率 (%)",
    "memory_usage": "当前内存使用率 (%)", 
    "disk_usage": "当前磁盘使用率 (%)",
    "network_io": "网络IO流量 (MB/s)"
}

# 应用性能监控
{
    "api_response_time": "API平均响应时间 (ms)",
    "api_error_rate": "API错误率 (%)",
    "cache_hit_rate": "缓存命中率 (%)",
    "concurrent_users": "并发用户数"
}

# 数据库性能监控  
{
    "db_connections": "数据库连接数",
    "db_query_time": "数据库查询平均时间 (ms)",
    "db_lock_waits": "数据库锁等待数",
    "db_cache_hit_ratio": "数据库缓存命中率 (%)"
}
```

## 测试用例清单

### 基础功能测试

- [ ] **API健康检查**
  - [ ] 监控系统健康端点
  - [ ] 数据库连接状态
  - [ ] 服务可用性检查

- [ ] **前端页面测试**
  - [ ] 仪表盘页面加载和交互
  - [ ] 股票列表页面功能
  - [ ] 股票详情页面显示
  - [ ] 技术分析页面渲染
  - [ ] 行业概念分析页面

- [ ] **数据一致性测试**
  - [ ] 多次请求数据一致性
  - [ ] Mock与真实数据格式对比
  - [ ] 分页数据连续性

### 性能专项测试

- [ ] **页面加载性能**
  - [ ] 首页加载时间 ≤ 1.5秒
  - [ ] 子页面加载时间 ≤ 2.5秒
  - [ ] 静态资源缓存效果
  - [ ] 图片和JS/CSS压缩

- [ ] **API响应性能**
  - [ ] 数据查询API ≤ 500ms
  - [ ] 技术指标API ≤ 1秒
  - [ ] 搜索API ≤ 800ms
  - [ ] 健康检查API ≤ 100ms

- [ ] **数据库性能**
  - [ ] 简单查询 ≤ 200ms
  - [ ] 复杂查询 ≤ 2秒
  - [ ] 批量插入性能
  - [ ] 分页查询优化

- [ ] **并发处理能力**
  - [ ] 100并发用户测试
  - [ ] 500并发用户测试
  - [ ] 1000并发用户测试
  - [ ] 峰值负载恢复能力

### 稳定性测试

- [ ] **长时间运行测试**
  - [ ] 24小时连续运行
  - [ ] 内存泄漏检测
  - [ ] 资源清理验证

- [ ] **故障恢复测试**
  - [ ] 服务重启恢复时间
  - [ ] 数据库故障转移
  - [ ] 缓存失效处理

## 性能调优指南

### 前端优化

```javascript
// 1. 资源优化
// 启用Gzip压缩
// 实施资源缓存策略
// 压缩图片和静态资源

// 2. 代码分割
const lazyComponent = React.lazy(() => import('./Component'))

// 3. 缓存策略
const cacheConfig = {
  stocksBasic: 300000,    // 5分钟
  industries: 3600000,    // 1小时  
  markets: 60000,         // 1分钟
  klineData: 300000       // 5分钟
}
```

### 后端优化

```python
# 1. 数据库优化
# 添加适当索引
CREATE INDEX idx_stocks_symbol ON stocks_basic(symbol);
CREATE INDEX idx_kline_date_symbol ON kline_data(date, symbol);

# 2. 查询优化
# 使用连接池
# 实施查询缓存
# 分页查询优化

# 3. 并发处理
# 使用异步编程
# 实施限流机制
# 负载均衡配置
```

### 数据库优化

```sql
-- 1. PostgreSQL优化配置
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 64MB

-- 2. TimescaleDB优化
timescaledb.max_background_workers = 8
timescaledb.max_insert_batch_size = 1000

-- 3. 索引策略
CREATE INDEX CONCURRENTLY idx_kline_time_period ON kline_data(ts, period);
CREATE INDEX CONCURRENTLY idx_stocks_industry ON stocks_basic(industry);
```

## 验收标准

### 必达指标 (Must Have)

1. **页面加载**: 所有页面加载时间 ≤ 2.5秒
2. **API响应**: 核心API响应时间 ≤ 500ms
3. **数据一致性**: Mock与真实数据100%一致
4. **系统稳定**: 24小时无崩溃或内存泄漏
5. **错误处理**: 所有错误有友好的用户提示

### 期望指标 (Should Have)

1. **页面加载**: 主要页面加载时间 ≤ 1.5秒
2. **API响应**: 所有API响应时间 ≤ 300ms
3. **缓存效果**: 缓存命中率 ≥ 85%
4. **并发处理**: 支持500+并发用户
5. **用户体验**: 页面交互响应时间 ≤ 200ms

### 优秀指标 (Could Have)

1. **页面加载**: 所有页面加载时间 ≤ 1秒
2. **API响应**: 所有API响应时间 ≤ 200ms
3. **缓存效果**: 缓存命中率 ≥ 95%
4. **并发处理**: 支持1000+并发用户
5. **性能监控**: 实时性能监控和告警

## 测试报告模板

### 性能测试报告结构

```markdown
# MyStocks 性能测试报告

## 测试概览
- 测试时间: YYYY-MM-DD HH:MM:SS
- 测试环境: 生产环境/测试环境
- 测试版本: v1.3.1
- 测试人员: XXX

## 性能指标达成情况

### 页面加载性能
| 页面 | 标准值 | 实际值 | 状态 | 备注 |
|------|--------|--------|------|------|
| 仪表盘 | ≤1.5s | 1.2s | ✅ 通过 | 优秀 |
| 股票列表 | ≤2.0s | 1.8s | ✅ 通过 | 良好 |

### API响应性能  
| API | 标准值 | 实际值 | 状态 | 备注 |
|-----|--------|--------|------|------|
| 健康检查 | ≤100ms | 45ms | ✅ 通过 | 优秀 |
| 股票数据 | ≤500ms | 320ms | ✅ 通过 | 良好 |

### 数据库性能
| 查询类型 | 标准值 | 实际值 | 状态 | 备注 |
|----------|--------|--------|------|------|
| 简单查询 | ≤200ms | 120ms | ✅ 通过 | 优秀 |
| 复杂查询 | ≤2.0s | 1.5s | ✅ 通过 | 良好 |

## 问题和建议

### 发现的问题
1. 技术分析页面加载时间略长，建议优化图表渲染
2. 行业概念分析API响应时间可进一步优化

### 优化建议
1. 实施前端代码分割，减少初始加载时间
2. 优化数据库索引，提升查询性能
3. 增加Redis缓存层，提升响应速度

## 结论
系统性能指标整体达标，可以投入生产使用。
建议优先处理发现的问题，进一步提升用户体验。
```

## 监控和维护

### 性能监控脚本

```bash
#!/bin/bash
# performance_monitor.sh - 持续性能监控

# 检查API响应时间
api_response_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8888/api/monitoring/health)
if (( $(echo "$api_response_time > 0.5" | bc -l) )); then
    echo "WARNING: API响应时间超过500ms: ${api_response_time}s"
fi

# 检查页面加载时间
page_load_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:3000/)
if (( $(echo "$page_load_time > 1.5" | bc -l) )); then
    echo "WARNING: 页面加载时间超过1.5s: ${page_load_time}s"
fi

# 检查系统资源使用率
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
memory_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')

echo "$(date): CPU: ${cpu_usage}%, Memory: ${memory_usage}%"
```

### 定期性能测试

```bash
# 每日性能基准测试
0 2 * * * /opt/claude/mystocks_spec/scripts/automation/regression_test.sh --performance-only

# 每周完整回归测试  
0 1 * * 0 /opt/claude/mystocks_spec/scripts/automation/regression_test.sh

# 性能阈值告警
*/15 * * * * /opt/claude/mystocks_spec/scripts/automation/performance_monitor.sh
```

---

**文档版本**: PERFORMANCE_BASELINE.md v1.0  
**创建时间**: 2025-11-17  
**最后更新**: 2025-11-17  
**负责人**: MyStocks开发团队